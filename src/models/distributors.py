from src.models.database import Database
import uuid


class Distributor(object):
    def __init__(self, type, slack_channel_id=None, email_address=None, _id=None):
        self.type = type
        self.slack_channel_id = None if type is None else slack_channel_id
        self.email_address = None if email_address is None else email_address
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "_id": self._id,
            "type": self.type,
            "slack_channel_id": self.slack_channel_id,
            "email_address": self.email_address,
        }

    @staticmethod
    def remove_distributor(email_address=None, slack_channel_id=None):
        database = Database()
        database.initialize()
        if email_address is None:
            database.remove("distributors", {"email_address": email_address})
        elif slack_channel_id is None:
            database.remove("distributors", {"slack_channel_id": slack_channel_id})
        print("Distributor was successfully removed")

    @staticmethod
    def add_distributor(type, email_address=None, slack_channel_id=None):
        if "type" == "email":
            if email_address is None:
                return "Please pass an email address"
        if "type" == "slack":
            if email_address is None:
                return "Please pass an slack_channel_id"
        elif all([(type != "slack"), (type != "email")]):
            return "Valid 'type's are 'slack' and 'email'"
        else:
            distributor = Distributor(type=type,
                                      email_address=email_address,
                                      slack_channel_id=slack_channel_id)
            database = Database()
            database.initialize()
            database.insert("distributors", distributor.json())
            return "Distributor successfully added"

    @classmethod
    def get_distributors(cls, type):
        database = Database()
        database.initialize()
        distributors = database.find("distributors", {"type": type})
        return [cls(**distributor) for distributor in distributors]
