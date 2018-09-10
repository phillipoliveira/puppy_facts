from src.models.database import Database
import uuid
import ast


class MessageLog(object):
    def __init__(self, channel, ts, text, image_url, _id=None):
        self.channel = channel
        self.ts = ts
        self.body = body
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
            "body": self.body
        }

    @staticmethod
    def migrate_message_log():
        message_log = "/Users/phillipoliveria/PycharmProjects/puppy_facts/src/message_log.txt"
        database = Database()
        database.initialize()
        lines = open(message_log).read().splitlines()
        for line in lines:
            ts = line.split(", ", 2)[0]
            channel = line.split(", ", 2)[1]
            body = line.split(", ", 2)[2]
            message = MessageLog(channel=channel,
                                 ts=ts,
                                 body=body)
            database.insert("message_log", message.json())

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

print(MessageLog.used_check(fact="hi", image="hi"))

