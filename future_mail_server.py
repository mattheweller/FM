from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import smtplib
from email.message import EmailMessage
import time
from flask_cors import CORS
from flask import render_template
from dotenv import load_dotenv
import os

load_dotenv()
email_password = os.environ.get('EMAIL_PASSWORD')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
CORS(app)
db = SQLAlchemy(app)

class FutureMail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_email():
    data = request.json
    recipient = data['recipient']
    subject = data['subject']
    message_body = data['message']

    # Calculate random delivery date between 1 week to 1 year from now
    # random_days = random.randint(7, 365)
    random_seconds = random.randint(1, 60)
    delivery_date = datetime.now() + timedelta(seconds=random_seconds)

    # Store the email data in the database
    future_mail = FutureMail(recipient=recipient, subject=subject, message=message_body, delivery_date=delivery_date)
    db.session.add(future_mail)
    db.session.commit()

    return jsonify({'message': 'Your email is scheduled!', 'delivery_date': delivery_date.strftime('%Y-%m-%d')})

def check_and_send_emails():
    while True:
        mails_to_send = FutureMail.query.filter(FutureMail.delivery_date <= datetime.now()).all()
        for mail in mails_to_send:
            send_actual_email(mail.recipient, mail.subject, mail.message)
            db.session.delete(mail)
        db.session.commit()
        time.sleep(86400)  # Sleep for 1 day and then check again

def send_actual_email(to, subject, body):
    # Set up your actual email sending logic here
    # Here's a dummy implementation using smtplib:
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "futuremail52@gmail.com"  # Set your email here
    msg['To'] = to

    # Login to your email server and send the email
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Using Gmail as an example
    server.login("futuremail52@gmail.com", email_password)  # Use environment variables for real usage
    server.send_message(msg)
    server.quit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

