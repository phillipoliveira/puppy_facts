import uuid
import random
from src.models.database import Database


class Images(object):
    def __init__(self, owner, associated_fact_type, image_url, ts, _id=None):
        self.owner = owner
        self.associated_fact_type = associated_fact_type
        self.image_url = image_url
        self.ts = ts
        self._id = uuid.uuid4().hex if _id is None else _id

    def add_image_to_database(self):
        database = Database()
        database.initialize()
        database.insert("images", self.json())

    @classmethod
    def find_images(cls, query=({})):
        database = Database()
        database.initialize()
        images = database.find("images", query)
        return [cls(**image) for image in images]

    @classmethod
    def find_images_by_owner(cls, owner):
        images = cls.find_images(query=({"owner": owner}))
        chosen_image = random.choice(images)
        return chosen_image

    def json(self):
        return {
            "_id": self._id,
            "owner": self.owner,
            "associated_fact_type": self.associated_fact_type,
            "image_url": self.image_url,
            "ts": self.ts
        }
