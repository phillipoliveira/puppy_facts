import re
from src.models.users import Users
from src.models.distributors import Distributor
from src.models.slack_commands import SlackCommands
from src.models.facts import Facts
from src.models.images import Images
import os


class Commands(object):

    @classmethod
    def main(cls):
        raw_response = input()
        response = Commands.clean_response(raw_response)
        if len(response) == 0:
            Commands.failure()
        elif all([(len(response) == 1), (response[0].lower() == 'start')]):
            Commands.start()
        else:
            try:
                function_dict[response[0]](response)
            except KeyError:
                Commands.failure()

    @staticmethod
    def start():
        dirpath = os.path.dirname(__file__)
        file = open(os.path.join(dirpath, "README.txt")).read()
        print(file)

    @staticmethod
    def view_users(response):
        users = Users.get_users(query=({}))
        print(users)
        for user in users:
            image_count = Images.get_image_count(user)
            print("Instatag: {}".format(user.instatag))
            print("Hashtag: {}".format(user.hashtag))
            print("Image Count: {}".format(image_count))
            print("--")

    @classmethod
    def add_user(cls, response):
        if len(response) < 4:
            cls.failure()
            return
        elif all([(response[2] == "fact-type"),
                (cls.check_fact_type(response[3]))]):
            user = Users(instatag=response[1],
                         associated_fact_type=response[3])
            user.onboard_user()
            return
        elif len(response) == 6:
            if all([(response[2] == "hashtag"), (response[4] == "fact-type")]):
                if cls.check_fact_type(response[5]):
                    user = Users(instatag=response[1],
                                 hashtag=response[3],
                                 associated_fact_type=response[5])
                    user.onboard_user()
                    return
        cls.failure()

    @classmethod
    def remove_user(cls, response):
        if len(response) != 2:
            cls.failure()
        else:
            user = Users.get_one_user(query=({"instatag": response[1]}))
            if user is not None:
                user.remove_user()
            else:
                cls.user_not_found()

    @classmethod
    def update_user(cls, response):
        if len(response) != 2:
            cls.failure()
        else:
            user = Users.get_one_user(query=({"instatag": response[1]}))
            if user is not None:
                user.onboard_user(update=True)
            else:
                cls.user_not_found()

    @classmethod
    def add_distributor(cls, response):
        if len(response) == 2:
            if response[0] == "add-email":
                Distributor.add_distributor(type="email", email_address=response[1])
                print("Email address successfully added")
            elif response[0] == "add-slack":
                Distributor.add_distributor(type="slack", slack_channel_id=response[1])
                print("Slack channel successfully added")
        else:
            cls.failure()

    @classmethod
    def remove_distributor(cls, response):
        if len(response) == 2:
            if response[0] == "remove-email":
                if Distributor.remove_distributor(email_address=response[1]):
                    print("Email address successfully removed")
                    return
            elif response[0] == "remove-slack":
                if Distributor.remove_distributor(slack_channel_id=response[1]):
                    print("Slack channel successfully removed")
                    return
        cls.failure()

    @staticmethod
    def print_slack_channels(response):
        slack = SlackCommands()
        slack.authenticate_slack()
        slack.print_channels()

    @staticmethod
    def print_slack_groups(response):
        slack = SlackCommands()
        slack.authenticate_slack()
        slack.print_groups()

    @classmethod
    def migrate_facts(cls, response):
        Facts.migrate_facts()

    @staticmethod
    def failure():
        print("Invalid command. Enter 'start' for help executing commands")

    @staticmethod
    def user_not_found():
        print("User not found.")

    @staticmethod
    def check_fact_type(fact_type):
        return any([(fact_type == "puppy_fact"),
                    (fact_type == "cat_fact"),
                    (fact_type == "horse_fact")])

    @staticmethod
    def clean_response(response):
        response_split = re.split(' ', response.lower())
        response_split_clean = []
        for i in response_split:
            if i.strip() != "":
                response_split_clean.append(i)
        return response_split_clean


function_dict ={"add-user": Commands.add_user,
                "view-users": Commands.view_users,
                "update-user": Commands.update_user,
                "remove-user": Commands.remove_user,
                "add-email": Commands.add_distributor,
                "add-slack": Commands.add_distributor,
                "remove-email": Commands.remove_distributor,
                "remove-slack": Commands.remove_distributor,
                "print-slack-channels": Commands.print_slack_channels,
                "print-slack-groups": Commands.print_slack_groups,
                "migrate-facts": Commands.migrate_facts}

Commands.start()
while True:
    Commands.main()
