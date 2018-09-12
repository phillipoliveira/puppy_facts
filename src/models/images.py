import uuid
import random
from src.commons.database import Database


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

    def update_image_data(self, update):
        database = Database()
        database.initialize()
        database.update("images", {"_id": self._id}, update)

    @classmethod
    def remove_image_data(cls, owner):
        images = cls.find_images(query=({"owner": owner}))
        for image in images:
            database = Database()
            database.initialize()
            database.remove("images", image.json())

    @staticmethod
    def get_image_count(user):
        images = Images.find_images({"owner": user.instatag})
        image_count = len(images)
        return image_count

# mass updating images
# images = Images.find_images(query=({"owner": "balzner"}))
# for image in images:
#    image.update_image_data(update=({
#                                         "_id" : image._id,
#                                         "owner" : image.owner,
#                                         "associated_fact_type" : "horse_fact",
#                                         "image_url" : image.image_url,
#                                         "ts" : image.ts
#                                     }))

