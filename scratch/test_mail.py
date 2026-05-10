import os
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Copy your actual credentials here temporarily for testing
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'purnima.g.in@gmail.com'
app.config['MAIL_PASSWORD'] = '@puriii2705'
app.config['MAIL_DEFAULT_SENDER'] = 'kayalclm65@gmail.com'

mail = Mail(app)

def test():
    with app.app_context():
        try:
            print("Attempting to send test email...")
            msg = Message(
                subject="StudyAI Mail Test",
                recipients=["purnima.g.in@gmail.com"], # Send to yourself to test
                body="This is a test to verify SMTP settings."
            )
            mail.send(msg)
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    test()
