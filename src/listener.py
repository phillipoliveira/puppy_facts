from flask import Flask, request, Response, make_response
from models.slack_commands import SlackCommands
from models.distributors import Distributor
from models.facts import Facts
from app import App
from pprint import pprint
import json


app = Flask(__name__)


@app.route('/puppy_facts/instagram_redirect', methods=["GET"])
def instagram_redirect():
    if 'error' in request.args:
        return Response("It didn't work!")
    # Retrieve the auth code from the request params
    else:
        print(request.args['access_token'])
        return Response("It worked! Thanks!")


@app.route('')

@app.route('/puppy_facts/events', methods=['POST'])
def events():
    event_data = json.loads(request.data.decode('utf-8'))
    # Echo the URL verification challenge code back to Slack
    if "challenge" in event_data:
        return make_response(
            event_data.get("challenge"), 200, {"content_type": "application/json"}
           )
    elif "event" in event_data:
        print(event_data)
        if all([(event_data['event']['type'] == 'group_left'), (event_data['api_app_id'] == 'AD1G9047Q')]):
            Distributor.remove_distributor(slack_ids={"channel_id": event_data['event']['channel'],
                                                      "team_id": event_data['team_id']})
        elif all([(event_data['event']['type'] == 'member_joined_channel'), (event_data['api_app_id'] == 'AD1G9047Q')]):
            Distributor.add_distributor(type="slack", slack_ids={"channel_id": event_data['event']['channel'],
                                                                 "team_id": event_data['team_id']})
    return json.dumps({'success': True}), 200, {"content_type": "application/json"}


@app.route('/puppy_facts/<string:fact_type>', methods=['POST'])
def return_fact(fact_type):
    # Echo the URL verification challenge code back to Slack
    app_response = App.cron_job(usage="command", fact_type=fact_type)
    app_response["response_type"] = "in_channel"
    response = app.response_class(
        response=json.dumps(app_response),
        status=200,
        mimetype='application/json')
    return response


@app.route('/puppy_facts/add/<string:fact_type>', methods=['POST'])
def add_fact(fact_type):
    # Echo the URL verification challenge code back to Slack
    username = request.form.getlist('user_name')[0]
    raw_text = request.form.getlist('text')[0]
    fact_text = raw_text + " #CustomFact by {}".format(username)
    Facts.add_fact(fact_type=fact_type, fact_text=fact_text)
    response = app.response_class(
        response=json.dumps({"text": "Thanks {}! Your fact has been added. :slightly_smiling_face:".format(username),
                             "response_type": "in_channel"}),
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
  '''.format(SlackCommands.get_app_credentials()["SLACK_OAUTH_SCOPE"],
             (SlackCommands.get_app_credentials()["SLACK_BOT_CLIENT_ID"]))


@app.route("/puppy_facts/finish_auth", methods=["GET", "POST"])
def post_install():
    if 'error' in request.args:
        return Response("It didn't work!")
    # Retrieve the auth code from the request params
    else:
        auth_code = request.args['code']
        # An empty string is a valid token for this request
        auth_response = SlackCommands.slack_token_request(auth_code)
        try:
            token = SlackCommands.get_token_from_database(team_id=auth_response['team_id'],
                                                          user_id=auth_response['user_id'])
            token.update_token(auth_response)
        except TypeError:
            token = SlackCommands()
            token.add_token(auth_response)
        return Response('It worked!')


if __name__ == "__main__":
        app.run(host='0.0.0.0')
