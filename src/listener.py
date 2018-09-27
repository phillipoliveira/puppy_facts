from flask import Flask, request, Response, make_response
from models.slack_commands import SlackCommands
from slackclient import SlackClient
from commons.database import Database
from app import App
import re
import json
import os
import time
import uuid


app = Flask(__name__)


@app.route('/slack', methods=['POST'])
def inbound():
    event_data = json.loads(request.data.decode('utf-8'))
    # Echo the URL verification challenge code back to Slack
    if "challenge" in event_data:
        return make_response(
            event_data.get("challenge"), 200, {"content_type": "application/json"}
           )
    elif all([("event" in event_data),
              (re.search("help", event_data['event']['text'])),
              (event_data['event']['type'] == "message")]):
        slack = SlackCommands()
        slack.send_raw_message(channel=event_data['event']['channel'], text=event_data)
        return


@app.route('/', methods=['GET'])
def test():
        return Response('It works!')


@app.route("/begin_auth", methods=["GET"])
def pre_install(self):
    return '''
      <a href="https://slack.com/oauth/authorize?scope={0}&client_id={1}">
          Add to Slack
      </a>
  '''.format(os.environ["SLACK_OAUTH_SCOPE"], os.environ["SLACK_BOT_CLIENT_ID"])


@app.route("/finish_auth", methods=["GET", "POST"])
def post_install(self):
    if 'error' in request.args:
        return Response("It didn't work!")
    # Retrieve the auth code from the request params
    else:
        auth_code = request.args['code']
        # An empty string is a valid token for this request
        slack = SlackCommands.get_credentials()
        slack.auth_code = auth_code
        auth_response = slack.get_token()
        slack.update_credentials(auth_response)
        return Response('It worked!')


if __name__ == "__main__":
        app.run(host='0.0.0.0')
