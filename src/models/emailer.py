import smtplib
from email.mime.text import MIMEText
from commons.database import Database


class Emailer(object):
    def __init__(self, email_address, email_password):
        self.email_address = email_address
        self.email_password =email_password

    @classmethod
    def get_email_credentials(cls, returnless=False):
        database = Database()
        database.initialize()
        emailer_credential_object = database.find_one("emailer_credentials", ({}))
        if emailer_credential_object is None:
            email_address = input("Please enter the gmail account address you would like to use to send emails:")
            email_password = input("Please enter your gmail password:")
            while cls.email_check(email_address, email_password) is False:
                email_address = input("Login failed. Please enter your GMAIL address:")
                email_password = input("Please enter your GMAIL password:")
            database.insert("emailer_credentials", ({"email_address": email_address,
                                                     "email_password": email_password}))
        else:
            email_address = emailer_credential_object['email_address']
            email_password = emailer_credential_object['email_password']
        if returnless is False:
            return email_address, email_password

    @staticmethod
    def email_check(email, password):
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.ehlo()
            server.login(email, password)
            return True
        except smtplib.SMTPAuthenticationError:
            return False

    @classmethod
    def send_email(cls, users, selected_attachment, selected_fact):
        email, password = cls.get_email_credentials()
        gmail_user = email
        fromx = email
        gmail_password = password
        for user in users:
            to = user.email_address
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.ehlo()
            server.login(gmail_user, gmail_password)
            msg = MIMEText("{}\n \n{} \n{}".format(selected_fact,
                                                   selected_attachment[0]["author_name"],
                                                   selected_attachment[0]["image_url"]))
            msg['Subject'] = "Daily Facts Bot! (and sometimes horses and cats)"
            msg['From'] = fromx
            msg['To'] = to
            server.sendmail(fromx, to, msg.as_string())
            server.quit()


Emailer.get_email_credentials(returnless=False)