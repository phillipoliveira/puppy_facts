from commons.database import Database
import uuid
import random
import os


class Facts(object):
    def __init__(self, fact_type, fact_text, _id=None):
        self.fact_type = fact_type
        self.fact_text = fact_text
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_facts(cls, query=({})):
        database = Database()
        database.initialize()
        facts = database.find("facts", query)
        return [cls(**fact) for fact in facts]

    @classmethod
    def retrieve_random_fact(cls, fact_type):
        facts = cls.get_facts(query=({"fact_type": fact_type}))
        chosen_fact = random.choice(facts)
        return chosen_fact

    @staticmethod
    def remove_fact(fact_text):
        database = Database()
        database.initialize()
        if database.find_one("facts", {"fact_text": fact_text}) is None:
            raise LookupError('Fact was not found in the database')
        else:
            database.remove("facts", {"fact_text": fact_text})
            print("Fact was successfully removed")

    @staticmethod
    def add_fact(fact_type, fact_text):
        if not any([(fact_type == "puppy_fact"),
                    (fact_type == "cat_fact"),
                    (fact_type == "horse_fact")]):
            print("fact_type must be one of the following: puppy_fact, cat_fact, horse_fact")
        else:
            database = Database()
            database.initialize()
            fact = Facts(fact_type = fact_type, fact_text = fact_text)
            database.insert("facts", fact.json())
            print("Fact successfully added")

    @staticmethod
    def migrate_facts():
        dirpath = os.path.dirname(__file__)
        fact_files = {'horse_fact': 'facts/horse_facts.txt',
                      'cat_fact': 'facts/cat_facts.txt',
                      'puppy_fact': 'facts/puppy_facts.txt'}
        database = Database()
        database.initialize()
        for k, v in fact_files.items():
            lines = open(os.path.join(dirpath, v)).read().splitlines()
            for line in lines:
                if line == "":
                    continue
                else:
                    fact = Facts(fact_type=k, fact_text=line)
                    database.insert("facts", fact.json())

    def json(self):
        return {
            "_id": self._id,
            "fact_type": self.fact_type,
            "fact_text": self.fact_text,
        }


if len(Facts.get_facts()) == 0:
    Facts.migrate_facts()

