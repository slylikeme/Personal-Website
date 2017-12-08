from email.mime.text import MIMEText
import smtplib

def send_email(email, username, password):
    from_email = "***********"
    from_password = "***********"
    to_email = email

    subject = "New Login Information"
    message = "Hello there! Welcome to Casey's Corner! <br> \
    Your username is <strong>{}</strong>. <br> \
    Your password is <strong>{}</strong>. <br> \
    Keep this information safe for future reference. \
    Thank you for signing up!".format(username, password)

    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['To'] = to_email
    msg['From'] = from_email

    gmail = smtplib.SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email, from_password)
    gmail.send_message(msg)
