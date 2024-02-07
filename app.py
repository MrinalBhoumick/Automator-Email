from flask import Flask, render_template, request, redirect, url_for
import csv
from io import TextIOWrapper
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')


def send_emails(emails, subject, message):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)

            for email in emails:
                msg = EmailMessage()
                msg.set_content(message)
                msg['Subject'] = subject
                msg['From'] = SMTP_EMAIL
                msg['To'] = email

                server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        csv_file = request.files['csv_file']
        subject = request.form.get('subject')
        message = request.form.get('message')

        if csv_file.filename.endswith('.csv'):
            emails = []
            csv_text = TextIOWrapper(csv_file, encoding='utf-8')
            csv_reader = csv.reader(csv_text)
            for row in csv_reader:
                emails.extend(row)

            if send_emails(emails, subject, message):
                return redirect(url_for('success'))
            else:
                return render_template('error.html', error='Failed to send emails. Please try again later.')

        return render_template('error.html', error='Invalid file format. Please upload a CSV file.')

    return render_template('index.html')


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(debug=True)
