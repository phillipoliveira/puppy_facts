from flask import Flask, request, Response, make_response
from models.slack_commands import SlackCommands
from app import App
import re
import json


app = Flask(__name__)


@app.route('/slack', methods=['POST'])
def inbound():
    event_data = json.loads(request.data.decode('utf-8'))
    # Echo the URL verification challenge code back to Slack
    if "challenge" in event_data:
        return make_response(
            event_data.get("challenge"), 200, {"content_type": "application/json"}
           )
    elif "event" in event_data:
        if re.search("help", event_data['event']['text']):
            slack = SlackCommands()
            slack.send_raw_message(channel=event_data['event']['channel'], text=event_data)
            return

@app.route('/', methods=['GET'])
def test():
        return Response('It works!')


if __name__ == "__main__":
        app.run(host='0.0.0.0')
