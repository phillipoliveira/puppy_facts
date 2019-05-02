from models.slack_commands import SlackCommands
from models.emailer import Emailer
from models.message_log import MessageLog
from models.users import Users
from models.images import Images
from models.facts import Facts
from models.distributors import Distributor
import time
# test channel = GCPJJ4G3U C0JS385LP
from pprint import pprint


class App(object):

    @staticmethod
    def cron_job(usage=None, fact_type=None):
        channels = Distributor.get_distributors("slack")
        emails = Distributor.get_distributors("email")
        print("sending...")
        used = False
        count = 0
        user = Users.choose_user(fact_type)
        image = Images.get_images(user=user.instatag, hashtag=user.hashtag)
        fact = Facts.retrieve_random_fact(user.associated_fact_type)
        selected_attachment = SlackCommands.create_slack_attachment(
            img=image['image_url'],
            insta_tag=user.instatag,
            ts=image['ts']
        )
        if usage == "command":
            return {"text": fact.fact_text,
                    "attachments": selected_attachment}
        else:
            for channel in channels:
                slack_commands = SlackCommands()
                response = slack_commands.send_message(
                    channel=channel,
                    fact=fact,
                    selected_attachment=selected_attachment
                )
                user.add_to_send_count()
                MessageLog.log_message(response=response,
                                       instatag=user.instatag)
            user.add_to_send_count()
            Emailer.send_email(emails, selected_attachment, fact.fact_text)
