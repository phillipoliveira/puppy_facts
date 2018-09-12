from flask import Flask, request, Response


# LEGACY CODE TO POTENTIALLY SUPPORT FUTURE INCOMING COMMANDS - CURRENTLY BROKEN.

app = Flask(__name__)
SLACK_WEBHOOK_SECRET =


@app.route('/slack', methods=['POST'])
def inbound():
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        channel = request.form.get('channel_name')
        username = request.form.get('user_name')
        text = request.form.get('text')


@app.route('/', methods=['GET'])
def test():
	return Response('It works!')


if __name__ == "__main__":
	app.run(debug=True)



