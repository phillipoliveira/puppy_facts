from models.slack_commands import SlackCommands
from models.emailer import Emailer
from models.message_log import MessageLog
from models.users import Users
from models.images import Images
from models.facts import Facts
from models.distributors import Distributor
import time
# test channel = GCPJJ4G3U C0JS385LP


def cron_job():
    channels = Distributor.get_distributors("slack")
    emails = Distributor.get_distributors("email")
    print("sending...")
    used = False
    count = 0
    while used is False:
        user = Users.choose_user()
        image = Images.find_images_by_owner(user.instatag)
        fact = Facts.retrieve_random_fact(user.associated_fact_type)
        selected_attachment = SlackCommands.create_slack_attachment(
            img=image.image_url,
            insta_tag=user.instatag,
            ts=image.ts
        )
        count += 1
        if count > 100:
            raise LookupError("NO PUPPY FACTS AVAILABLE :(")
        used = MessageLog.used_check(fact=fact.fact_text, image=image.image_url)
    for channel in channels:
        slack_commands = SlackCommands()
        response = slack_commands.send_message(
            user=user,
            channel=channel,
            fact=fact,
            selected_attachment=selected_attachment
        )
        MessageLog.log_message(response)
    Emailer.send_email(emails, selected_attachment, fact.fact_text)


cron_job()

