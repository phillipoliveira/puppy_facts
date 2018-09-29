from slackclient import SlackClient
from commons.database import Database
import time
import uuid
import os
import re


class SlackCommands(object):
    def __init__(self,
                 access_token=None,
                 auth_code=None,
                 token_expiry_time=None,
                 team_id=None,
                 user_id=None,
                 _id=None):
        self.access_token = None if access_token is None else access_token
        self.auth_code = None if auth_code is None else auth_code
        self.token_expiry_time = None if token_expiry_time is None else token_expiry_time
        self.team_id= None if team_id is None else team_id
        self.user_id=None if user_id is None else user_id
        self._id = self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_slack_token(cls):
        database = Database()
        database.initialize()
        try:
            slack_token_object = cls.get_credentials()
        except TypeError:
            print("Visit http://178.128.234.3:5000/begin_auth to authorize puppy_facts")
            raise ValueError("Slack authorization failed")
        if slack_token_object.token_expiry_time is None:
            print("Visit http://178.128.234.3:5000/begin_auth to authorize puppy_facts")
            raise ValueError("Slack authorization failed")
        elif int(slack_token_object.token_expiry_time) < int(time.time()):
            hook = cls.get_credentials()
            auth_response = hook.get_token()
            hook.update_credentials(auth_response)
            return SlackClient(str(auth_response['access_token']))
        else:
            return SlackClient(str(slack_token_object.access_token))

    def update_credentials(self, auth_response):
        self.access_token = auth_response['access_token']
        self.team_id = auth_response['team_id']
        self.user_id = auth_response['user_id']
        numbers = re.compile('\d+(?:\.\d+)?')
        max_age = int(numbers.findall(auth_response['headers']['Strict-Transport-Security'])[0])
        self.token_expiry_time = int(time.time()) + max_age
        Database.update(collection="slack_credentials",
                        query=({"_id": self._id}),
                        update=self.json())

    def add_credentials(self, auth_response):
        self.access_token = auth_response['access_token']
        self.user_id = auth_response['user_id']
        self.team_id = auth_response['team_id']
        numbers = re.compile('\d+(?:\.\d+)?')
        max_age = int(numbers.findall(auth_response['headers']['Strict-Transport-Security'])[0])
        self.token_expiry_time = int(time.time()) + max_age
        Database.insert(collection="slack_credentials",
                        data=self.json())

    def json(self):
        return({
            "_id": self._id,
            "access_token": self.access_token,
            "auth_code": self.auth_code,
            "token_expiry_time": self.token_expiry_time,
            "team_id": self.team_id,
            "user_id": self.user_id})

    def get_token(self):
        sc = SlackClient("")
        # Request the auth tokens from Slack
        auth_response = sc.api_call(
            "oauth.access",
            client_id=os.environ["SLACK_BOT_CLIENT_ID"],
            client_secret=os.environ["SLACK_BOT_CLIENT_SECRET"],
            code=self.auth_code
        )
        return auth_response

    @classmethod
    def get_credentials(cls):
        credentials = Database.find_one("slack_credentials", query=({}))
        return cls(**credentials)

    @staticmethod
    def check_slack_token(test_token):
        slack_client_test = SlackClient(test_token)
        result = slack_client_test.api_call("auth.test")
        if result['ok'] is True:
            return True
        else:
            return False

    @staticmethod
    def authenticate_slack():
        slack_client = SlackCommands.get_slack_token()
        slack_client.api_call("api.test")
        slack_client.api_call("auth.test")

    @classmethod
    def list_channels(cls):
        channels_call = cls.get_slack_token().api_call("conversations.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None

    @classmethod
    def list_groups(cls):
        groups_call = cls.get_slack_token().api_call("groups.list")
        if groups_call['ok']:
            return groups_call['groups']
        return None

    @classmethod
    def channel_info(cls, channel_id):
        channel_info = cls.get_slack_token().api_call("channels.info", channel=channel_id)
        if channel_info:
            return channel_info['channel']
        return None

    @classmethod
    def print_channels(cls):
        channels = cls.list_channels()
        if channels:
            print("Channels: ")
            for c in channels:
                print(c['name'] + " (" + c['id'] + ")")
                detailed_info = cls.channel_info(c['id'])
                if detailed_info['purpose']['value']:
                    try:
                        print("\t"+(detailed_info['purpose']['value']))
                    except:
                        continue
        else:
            print("Unable to authenticate.")

    def print_groups(self):
        groups = self.list_groups()
        if groups:
            print("Groups: ")
            for g in groups:
                print(g['name'] + " (" + g['id'] + ")")
        else:
            print("Unable to authenticate.")

    @classmethod
    def send_message(cls, user, channel, fact, selected_attachment):
        response = (cls.get_slack_token().api_call(
            "chat.postMessage",
            channel=channel.slack_channel_id,
            text=fact.fact_text,
            attachments=selected_attachment
        ))
        user.add_to_send_count()
        return response

    @classmethod
    def send_raw_message(cls, channel, text):
        cls.get_slack_token().api_call("chat.postMessage", channel=channel, text=text)

    @classmethod
    def delete_message(cls, channel_id, ts):
        response = (cls.get_slack_token().api_call(
            "chat.delete",
            channel=channel_id,
            ts=ts
        ))
        print(response)
        #delete_message(channel_id="D1V9HRYV8", ts=1527173692.000490)

    @classmethod
    def return_group_id(cls, name):
        groups_call = cls.get_slack_token().api_call("groups.list")
        for g in groups_call['groups']:
            if g['name'] == name:
                return list(g['id'])

    @classmethod
    def return_user_id(cls, firstname):
        users = cls.get_slack_token().api_call("users.list")
        l,results,count = [],[],0
        for i in users['members']:
            l.append(i['id'])
        while count < len(l):
            count+=1
            for i in users['members']:
                try:
                    if i[u'profile']['first_name'].lower() == firstname.lower():
                        results.append(i['id'])
                        break
                    else:
                        continue
                except:
                    continue
        return set(results)

    @classmethod
    def print_users(cls):
        users = cls.get_slack_token().api_call("users.list")
        for i in users['members']:
            try:
                print(i[u'profile']['first_name'] +" "+ i[u'profile']['last_name'])
                print(i['id'])
            except:
                continue

    @staticmethod
    def create_slack_attachment(insta_tag, img, ts):
        attachment = [
            {
                "fallback": "Puppy Facts.",
                "color": "#36a64f",
                "author_name": "@" + insta_tag,
                "image_url": img,
                "ts": int(ts)
            }
        ]
        return attachment


if __name__ == "__main__":
    slack = SlackCommands()
    slack.authenticate_slack()
    slack.print_channels()
# Deleting a message:
# slack = SlackCommands()
# slack.delete_message(channel_id='C0JS385LP', ts='1537797654.000100')

# {'ok': True, 'url': 'https://checkout51.slack.com/', 'team': 'Checkout 51', 'user': 'phillolive', 'team_id': 'T0JRP51QF', 'user_id': 'U1V9CPH89', 'headers': {'Content-Type': 'application/json; charset=utf-8', 'Content-Length': '133', 'Connection': 'keep-alive', 'Date': 'Fri, 07 Sep 2018 01:32:12 GMT', 'Server': 'Apache', 'X-Content-Type-Options': 'nosniff', 'x-slack-router': 'p', 'Expires': 'Mon, 26 Jul 1997 05:00:00 GMT', 'Cache-Control': 'private, no-cache, no-store, must-revalidate', 'X-OAuth-Scopes': 'read,client,identify,post,apps', 'Pragma': 'no-cache', 'X-XSS-Protection': '0', 'X-Slack-Req-Id': '356122c5-868c-4dbd-b3bb-82d8a4d6a5b1', 'X-Slack-Exp': '1', 'X-Slack-Backend': 'h', 'Referrer-Policy': 'no-referrer', 'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload', 'Vary': 'Accept-Encoding', 'Content-Encoding': 'gzip', 'Access-Control-Allow-Origin': '*', 'X-Via': 'haproxy-www-f3wc', 'X-Cache': 'Miss from cloudfront', 'Via': '1.1 36fb5b95873f68753e3074960e927e21.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'cMVSvGzLy5PRE7I37y61dlOiPL7hKo0E2zv2210lccF3NgauZQ00bw=='}}