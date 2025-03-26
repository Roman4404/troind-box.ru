import flask

app = flask.Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return flask.render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return flask.render_template('login_form.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return flask.render_template('register_form.html')
    elif flask.request.method == 'POST':
        file = flask.request.form['email']
        print(file)
        return flask.redirect('/')

if __name__ == '__main__':
    app.run()
