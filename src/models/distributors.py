from commons.database import Database
import uuid


class Distributor(object):
    def __init__(self, type, slack_ids=None, email_address=None, _id=None):
        self.type = type
        self.slack_ids = None if slack_ids is None else slack_ids
        self.email_address = None if email_address is None else email_address
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "_id": self._id,
            "type": self.type,
            "slack_ids": self.slack_ids,
            "email_address": self.email_address,
        }

    @staticmethod
    def remove_distributor(email_address=None, slack_ids=None):
        database = Database()
        database.initialize()
        if database.find_one("distributors", {"email_address": email_address,
                                              "slack_ids": slack_ids}):
            database.remove("distributors", {"email_address": email_address})
            return True

    @staticmethod
    def add_distributor(type, email_address=None, slack_ids=None):
        if "type" == "email":
            if email_address is not None:
                return "Please pass an email address"
        if "type" == "slack":
            if email_address is not None:
                return "Please pass an slack_channel_id"
        elif all([(type != "slack"), (type != "email")]):
            return "Valid 'type's are 'slack' and 'email'"
        else:
            distributor = Distributor(type=type,
                                      email_address=email_address,
                                      slack_ids=slack_ids)
            database = Database()
            database.initialize()
            database.insert("distributors", distributor.json())

    @classmethod
    def get_distributors(cls, type):
        database = Database()
        database.initialize()
        distributors = database.find("distributors", {"type": type})
        return [cls(**distributor) for distributor in distributors]



#Distributor.add_distributor(type="slack", slack_channel_id="C0JS385LP")
#Distributor.add_distributor(type="email", email_address="tabrinalw@gmail.com")