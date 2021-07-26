import flask

app = flask.Flask(__name__)


@app.route('/hello-k8s')
def handle():
    return "Hello k8s"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='2333')
