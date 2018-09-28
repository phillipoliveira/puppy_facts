from flask import Flask, request, Response, make_response
from models.slack_commands import SlackCommands
from models.distributors import Distributor
from urllib.parse import unquote
from slackclient import SlackClient
from commons.database import Database
from app import App
import re
import json
import os
import time
import uuid


app = Flask(__name__)


@app.route('/puppy_facts/events', methods=['POST'])
def events():
    event_data = json.loads(request.data.decode('utf-8'))
    # Echo the URL verification challenge code back to Slack
    if "challenge" in event_data:
        return make_response(
            event_data.get("challenge"), 200, {"content_type": "application/json"}
           )
    elif "event" in event_data:
        if event_data['event']['type'] == 'group_left':
            Distributor.remove_distributor(slack_channel_id=event_data['event']['channel'])
        elif all ([(event_data['event']['type'] == 'member_joined_channel'), (event_data['event']['user'] == 'UCZDTNS80')]):
            Distributor.add_distributor(type="slack", slack_channel_id=event_data['event']['channel'])
    return json.dumps({'success': True}), 200, {"content_type": "application/json"}


@app.route('/puppy_facts/commands', methods=['POST'])
def commands():
    channel_id = request.form.getlist('channel_id')[0]
    # Echo the URL verification challenge code back to Slack
    app_response = App.cron_job(slack_user=channel_id, usage="command")
    response = app.response_class(
        response=json.dumps(app_response),
        status=200,
        mimetype='application/json')
    return response


@app.route('/', methods=['GET'])
def test():
        return Response('It works!')


@app.route("/puppy_facts/begin_auth", methods=["GET"])
def pre_install():
    return '''
      <a href="https://slack.com/oauth/authorize?scope={0}&client_id={1}">
          Add to Slack
      </a>
  '''.format(os.environ["SLACK_OAUTH_SCOPE"], os.environ["SLACK_BOT_CLIENT_ID"])


@app.route("/puppy_facts/finish_auth", methods=["GET", "POST"])
def post_install():
    if 'error' in request.args:
        return Response("It didn't work!")
    # Retrieve the auth code from the request params
    else:
        auth_code = request.args['code']
        # An empty string is a valid token for this request
        slack = SlackCommands()
        slack.auth_code = auth_code
        auth_response = slack.get_token()
        try:
            slack.get_credentials(auth_response)
            slack.update_credentials(auth_response)
        except TypeError:
            slack.add_credentials(auth_response)
        return Response('It worked!')


if __name__ == "__main__":
        app.run(host='0.0.0.0')
