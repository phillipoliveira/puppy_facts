from src.models.database import Database
from src.models.image_scraper import ImageScraper
import uuid
import random
import time


class Users(object):
    def __init__(self, instatag, associated_fact_type, send_count=None, hashtag=None, _id=None):
        self.instatag = instatag
        self.associated_fact_type = self.check_associated_fact_type(associated_fact_type)
        self.hashtag = hashtag
        self.send_count = 0 if send_count is None else send_count
        self._id = uuid.uuid4().hex if _id is None else _id

    def onboard_user(self, update=False):
        json_data = ImageScraper.scrape_instagram(self)
        ImageScraper.update_image_database(json_data, user=self)
        if update is False:
            database = Database()
            database.initialize()
            database.insert("users", self.json())

    @staticmethod
    def check_associated_fact_type(associated_fact_type):
        if not any([(associated_fact_type == "puppy_fact"),
                    (associated_fact_type == "horse_fact"),
                    (associated_fact_type == "cat_fact")]):
            raise LookupError("associated_fact_type must be either 'puppy_fact', 'cat_fact' or 'horse_fact'")
        else:
            return associated_fact_type

    @classmethod
    def get_users(cls, query=({})):
        database = Database()
        database.initialize()
        users = database.find("users", query)
        return [cls(**user) for user in users]


    def json(self):
        return {
            "_id": self._id,
            "instatag": self.instatag,
            "hashtag": self.hashtag,
            "send_count": self.send_count,
            "associated_fact_type": self.associated_fact_type
        }

    @classmethod
    def get_lowest_send_count(cls):
        users = cls.get_users()
        num_list = []
        for user in users:
            num_list.append(user.send_count)
        try:
            lowest_num = min(num_list)
        except ValueError:
            lowest_num = 0
        return lowest_num

    @classmethod
    def choose_user(cls):
        lowest_num = cls.get_lowest_send_count()
        user_list = []
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
