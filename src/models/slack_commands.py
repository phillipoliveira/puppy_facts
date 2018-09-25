from slackclient import SlackClient
from commons.database import Database
import getpass


class SlackCommands(object):
    def __init__(self, slack_client=None):
        self.slack_client = SlackClient(self.get_slack_token()) if slack_client is None else slack_client

    @classmethod
    def get_slack_token(cls):
        database = Database()
        database.initialize()
        slack_token_object = database.find_one("slack_token", ({}))
        if slack_token_object is None:
            slack_token = getpass.getpass("Please enter your slack token:")
            while cls.check_slack_token(slack_token) is False:
                slack_token = getpass.getpass("Invalid token. Please enter a valid slack token:")
            database.insert("slack_token", ({"token": slack_token}))
        else:
            slack_token = slack_token_object['token']
        return slack_token

    @staticmethod
    def check_slack_token(test_token):
        slack_client_test = SlackClient(test_token)
        result = slack_client_test.api_call("auth.test")
        if result['ok'] is True:
            return True
        else:
            return False

    def authenticate_slack(self):
        self.slack_client.api_call("api.test")
        self.slack_client.api_call("auth.test")

    def list_channels(self):
        channels_call = self.slack_client.api_call("channels.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None

    def list_groups(self):
        groups_call = self.slack_client.api_call("groups.list")
        if groups_call['ok']:
            return groups_call['groups']
        return None

    def channel_info(self, channel_id):
        channel_info = self.slack_client.api_call("channels.info", channel=channel_id)
        if channel_info:
            return channel_info['channel']
        return None

    def print_channels(self):
        channels = self.list_channels()
        if channels:
            print("Channels: ")
            for c in channels:
                print(c['name'] + " (" + c['id'] + ")")
                detailed_info = self.channel_info(c['id'])
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

    def send_message(self, user, channel, fact, selected_attachment):
        response = (self.slack_client.api_call(
            "chat.postMessage",
            channel=channel.slack_channel_id,
            text=fact.fact_text,
            username='Puppy Facts Bot (and sometimes horses and cats)',
            icon_emoji=':dog:',
            attachments=selected_attachment
        ))
        user.add_to_send_count()
        return response

    def send_raw_message(self, channel, text):
        self.slack_client.api_call("chat.postMessage", channel=channel, text=text)

    def delete_message(self, channel_id, ts):
        response = (self.slack_client.api_call(
            "chat.delete",
            channel=channel_id,
            ts=ts
        ))
        print(response)
        #delete_message(channel_id="D1V9HRYV8", ts=1527173692.000490)

    def return_group_id(self, name):
        groups_call = self.slack_client.api_call("groups.list")
        for g in groups_call['groups']:
            if g['name'] == name:
                return list(g['id'])

    def return_user_id(self, firstname):
        users = self.slack_client.api_call("users.list")
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

    def print_users(self):
        users = self.slack_client.api_call("users.list")
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


# Deleting a message:
# slack = SlackCommands()
# slack.delete_message(channel_id='C0JS385LP', ts='1537797654.000100')

# {'ok': True, 'url': 'https://checkout51.slack.com/', 'team': 'Checkout 51', 'user': 'phillolive', 'team_id': 'T0JRP51QF', 'user_id': 'U1V9CPH89', 'headers': {'Content-Type': 'application/json; charset=utf-8', 'Content-Length': '133', 'Connection': 'keep-alive', 'Date': 'Fri, 07 Sep 2018 01:32:12 GMT', 'Server': 'Apache', 'X-Content-Type-Options': 'nosniff', 'x-slack-router': 'p', 'Expires': 'Mon, 26 Jul 1997 05:00:00 GMT', 'Cache-Control': 'private, no-cache, no-store, must-revalidate', 'X-OAuth-Scopes': 'read,client,identify,post,apps', 'Pragma': 'no-cache', 'X-XSS-Protection': '0', 'X-Slack-Req-Id': '356122c5-868c-4dbd-b3bb-82d8a4d6a5b1', 'X-Slack-Exp': '1', 'X-Slack-Backend': 'h', 'Referrer-Policy': 'no-referrer', 'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload', 'Vary': 'Accept-Encoding', 'Content-Encoding': 'gzip', 'Access-Control-Allow-Origin': '*', 'X-Via': 'haproxy-www-f3wc', 'X-Cache': 'Miss from cloudfront', 'Via': '1.1 36fb5b95873f68753e3074960e927e21.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'cMVSvGzLy5PRE7I37y61dlOiPL7hKo0E2zv2210lccF3NgauZQ00bw=='}}