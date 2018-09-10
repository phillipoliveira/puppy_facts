from src.models.slack_commands import SlackCommands
from src.models.emailer import Emailer
from src.models.facts import Facts
from src.models.message_log import MessageLog
from src.models.users import Users
from src.models.images import Images
from src.models.facts import Facts
from src.models.distributors import Distributor
import time
import pdb
# test channel = GCPJJ4G3U C0JS385LP


def cron_job():
    channels = Distributor.get_distributors("slack")
    emails = Distributor.get_distributors("email")
    while True:
        if all([(time.localtime().tm_hour == 21), (time.localtime().tm_min == 58)]):
            print("sending...")
            used = False
            count = 0
            while used is False:
                user = Users.choose_user()
                image = Images.find_images_by_owner(user.instatag)
                fact = Facts.retrieve_random_fact(user.associated_fact_type)
                selected_attachment = SlackCommands.create_slack_attachment(img=image.image_url,
                                                                            insta_tag=user.instatag,
                                                                            ts=image.ts)
                count += 1
                if count > 100:
                    raise LookupError("NO PUPPY FACTS AVAILABLE :(")
                used = MessageLog.used_check(fact=fact.fact_text, image=image.image_url)
            for channel in channels:
                slack_commands = SlackCommands()
                response = slack_commands.send_message(channel_id=channel.slack_channel_id,
                                                       message=fact.fact_text,
                                                       attachment=selected_attachment)
                user.add_to_send_count()
                try:
                    message = MessageLog(channel=response['channel'],
                                         ts=response['ts'],
                                         text=response['message']['text'],
                                         image_url=response['attachments']['image_url'])
                    message.add_entry()
                except KeyError:
                    print("This response couldn't be added to the message_log: {}".format(response))
                    continue
            Emailer.send_email(emails, selected_attachment, fact.fact_text)
            pdb.set_trace()
            time.sleep(120)
        else:
            time.sleep(50)


cron_job()
