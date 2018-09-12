from src.commons.database import Database
import uuid


class MessageLog(object):
    def __init__(self, channel, ts, text, image_url, _id=None):
        self.channel = channel
        self.ts = ts
        self.text = text
        self.image_url = image_url
        self._id = uuid.uuid4().hex if _id is None else _id

    def add_entry(self):
        database = Database()
        database.initialize()
        database.insert("message_log", self.json())

    def json(self):
        return {
            "_id": self._id,
            "channel": self.channel,
            "ts": self.ts,
            "text": self.text,
            "image_url": self.image_url
        }

    @classmethod
    def pull_message_log(cls):
        database = Database()
        database.initialize()
        messages = database.find("message_log", ({}))
        return [cls(**message) for message in messages]

    @classmethod
    def used_check(cls, fact, image):
        messages = cls.pull_message_log()
        for message in messages:
            if message.text == fact:
                return False
            if message.image_url == image:
                return False
        return True

    @classmethod
    def log_message(cls, response):
        try:
            message = cls(
                channel=response['channel'],
                ts=response['ts'],
                text=response['message']['text'],
                image_url=response['message']['attachments'][0]['image_url']
            )
            message.add_entry()
        except KeyError:
            print("This response couldn't be added to the message_log: {}".format(response))
        return


