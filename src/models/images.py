import uuid
import random
import requests
from bs4 import BeautifulSoup
import json
import re
from commons.database import Database


class Images(object):
    def __init__(self, image_url, ts, _id=None):
        self.image_url = image_url
        self.ts = ts
        self._id = uuid.uuid4().hex if _id is None else _id

    @staticmethod
    def get_scripts(url):
        session = requests.session()
        request = session.get(url)
        page_content = request.content
        soup = BeautifulSoup(page_content, "html.parser")
        scripts = str(soup).split("""<script type="text/javascript">window._sharedData = """)[1].split(";</script>")
        raw_json = json.loads(scripts[0])
        return raw_json

    @classmethod
    def get_images(cls, user, hashtag):
        url = "https://www.instagram.com/{}/".format(user)
        raw_json = cls.get_scripts(url)
        nodes = raw_json['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        owner_id = nodes[0]['node']['owner']['id']
        images = list()
        if hashtag is None:
            for node in nodes:
                image = (node['node']['thumbnail_src'])
                ts = node['node']['taken_at_timestamp']
                images.append({"image_url": image, "ts": ts})
        else:
            url = "https://www.instagram.com/explore/tags/{}/".format(hashtag)
            raw_json = cls.get_scripts(url)
            nodes = raw_json['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
            for node in nodes:
                if node['node']['owner']['id'] == owner_id:
                    image = node['node']['thumbnail_src']
                    ts = node['node']['taken_at_timestamp']
                    images.append({"image_url": image, "ts": ts})
        chosen_image = {"image_url":""}
        while re.search(".jpg", chosen_image['image_url']) is None:
            chosen_image = random.choice(images)
        return chosen_image



