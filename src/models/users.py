from commons.database import Database
from models.images import Images
import uuid
import random


class Users(object):
    def __init__(self, instatag, associated_fact_type, send_count=None, hashtag=None, _id=None):
        self.instatag = instatag
        self.associated_fact_type = associated_fact_type
        self.hashtag = hashtag
        self.send_count = 0 if send_count is None else send_count
        self._id = uuid.uuid4().hex if _id is None else _id

    def onboard_user(self):
        database = Database()
        database.initialize()
        database.insert("users", self.json())
        print("User successfully added")

    @classmethod
    def get_users(cls, query=({})):
        database = Database()
        database.initialize()
        users = database.find("users", query)
        return [cls(**user) for user in users]

    @classmethod
    def get_one_user(cls, query=({})):
        database = Database()
        database.initialize()
        user = database.find_one("users", query)
        return cls(**user)

    def json(self):
        return {
            "_id": self._id,
            "instatag": self.instatag,
            "hashtag": self.hashtag,
            "send_count": self.send_count,
            "associated_fact_type": self.associated_fact_type
        }

    @classmethod
    def get_lowest_send_count(cls, query=({})):
        users = cls.get_users(query)
        num_list = []
        for user in users:
            num_list.append(user.send_count)
        try:
            lowest_num = min(num_list)
        except ValueError:
            lowest_num = 0
        return lowest_num

    @classmethod
    def choose_user(cls, fact_type=None):
        user_list = []
        if fact_type is not None:
            lowest_num = cls.get_lowest_send_count(query=({"associated_fact_type": fact_type}))
            users = cls.get_users(query=({"send_count": lowest_num,
                                          "associated_fact_type": fact_type}))
        else:
            lowest_num = cls.get_lowest_send_count(query=({}))
            users = cls.get_users(query=({"send_count": lowest_num}))
        for user in users:
            user_list.append(user)
        choice = random.choice(user_list)
        return choice

    def add_to_send_count(self):
        database = Database()
        database.initialize()
        self.send_count += 1
        database.update("users", {"_id": self._id}, self.json())

    def update_user(self, update):
        database = Database()
        database.initialize()
        database.update("users", {"_id": self._id}, update)
        print("User successfully updated")

    def remove_user(self):
        database = Database()
        database.initialize()
        database.remove("users", {"_id": self._id})
        Images.remove_image_data(self.instatag)
        print("User successfully removed")


# Updating user database entry:
#user = Users.get_one_user({"instatag":"coreybrendan"})
#user.update_user({
#	"_id" : "a892b4e3c5f543de8ebf82da93ecea72",
#	"instatag" : "coreybrendan",
#	"hashtag" : "rubyloz",
#	"send_count" : 0,
#	"associated_fact_type" : "puppy_fact"
#})
