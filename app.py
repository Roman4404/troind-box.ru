import flask

app = flask.Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return flask.render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def about():
    return flask.render_template('login_form.html')

if __name__ == '__main__':
    app.run()
