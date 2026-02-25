from flask import Flask, render_template, request, jsonify
import imaplib

app = Flask(__name__)


def delete_messages(mail, mailbox, search_criteria):
    deleted_count = 0

    # Select mailbox
    status, _ = mail.select(mailbox)
    if status != "OK":
        return 0

    # Search messages
    status, data = mail.search(None, search_criteria)
    if status != "OK":
        return 0

    ids = data[0].split()
    if not ids:
        return 0

    for msg_id in ids:
        # Move to Trash instead of expunge
        mail.copy(msg_id, '"[Gmail]/Trash"')
        mail.store(msg_id, "+FLAGS", "\\Deleted")

    # Expunge INSIDE selected mailbox
    mail.expunge()

    deleted_count = len(ids)
    return deleted_count


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/clean", methods=["POST"])
def clean():
    email_user = request.json.get("email")
    password = request.json.get("password")
    delete_read = request.json.get("read")
    delete_promo = request.json.get("promo")

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, password)

        total_deleted = 0

        if delete_read:
            total_deleted += delete_messages(mail, "INBOX", "SEEN")

        if delete_promo:
            total_deleted += delete_messages(mail, '"[Gmail]/Promotions"', "ALL")

        mail.logout()

        return jsonify({
            "success": True,
            "deleted": total_deleted
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)