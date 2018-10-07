import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from commons.database import Database
from PIL import Image, ImageTk
from io import BytesIO
from resizeimage import resizeimage


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
        gmail_password = password
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.ehlo()
        server.login(gmail_user, gmail_password)
        img_data = cls.get_image_resize(selected_attachment)
        html_part = MIMEMultipart(_subtype='related')
        body = MIMEText('<p>{}\n \n{}\n <img src="cid:myimage" /></p>'.format(selected_fact,
                                                                              selected_attachment[0][
                                                                                  "author_name"]),
                        _subtype='html')
        html_part.attach(body)
        # Now create the MIME container for the image
        img = MIMEImage(img_data, 'jpeg')
        img.add_header('Content-Id', '<myimage>')  # angle brackets are important
        img.add_header("Content-Disposition", "inline", filename="myimage")  # David Hess recommended this edit
        html_part.attach(img)
        msg = MIMEMultipart(_subtype='related')
        msg['Subject'] = "Daily Facts Bot! (and sometimes horses and cats)"
        msg['From'] = gmail_user
        msg.attach(html_part)
        for user in users:
            msg['To'] = user.email_address
            server.sendmail(gmail_user, user.email_address, msg.as_string())
        server.quit()

    @staticmethod
    def get_image_resize(selected_attachment):
        url = selected_attachment[0]["image_url"]
        r = requests.get(url)
        image = Image.open(BytesIO(r.content))
        image.mode = 'RGB'
        image = resizeimage.resize_contain(image, [800, 800])
        imgByteArr = BytesIO()
        image.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr


Emailer.get_email_credentials(returnless=False)