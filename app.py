import flask
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.user import RegisterForm, LoginForm
from data.users import User
from data.chats import Chats
from data import db_session

from Ai_models.yandexgpt import yandexgptlite_requst


app = flask.Flask(__name__)
db_session.global_init("db/users.db")
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect("/")

@app.route('/')
def hello_world():  # put application's code here
    return flask.render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return flask.redirect("/")
            return flask.render_template('login.html', message="Неправильный логин или пароль", form=form)
        return flask.render_template('login.html', title='Авторизация', form=form)
    else:
        return flask.redirect(f'/profile/{current_user.name}')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated:
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return flask.render_template('register.html', form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return flask.render_template('register.html', form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return flask.redirect(f'/profile/{user.name}')
        return flask.render_template('register.html', form=form)
    else:
        return flask.redirect(f'/profile/{current_user.name}')


@app.route('/profile/<name>')
def profile_view(name):
    db_sess = db_session.create_session()
    all_users = db_sess.query(User).all()
    if current_user.is_authenticated:
        if current_user.name == name:
            find_user = False
            for user in all_users:
                if name == user.name:
                    find_user = True
                    break
            if find_user:
                return flask.render_template('profile_info.html', name=name, count_tokens=user.count_tokes)
            else:
                return flask.render_template('error404.html')
        else:
            return flask.render_template('error404.html')
    else:
        return flask.redirect('/login')


@app.route('/russian_memory')
def Russian_Memory_view():
    return flask.render_template('russian_memory_view.html')


@app.route('/ai_platform')
def ai_platform():
    return flask.redirect('/pfai')

@app.route('/pfai/new_chat', methods=['POST', 'GET'])
def pfai_new_chat():
    if flask.request.method == 'GET':
        if current_user.is_authenticated:
            return flask.render_template('PFAI/new_chat_pfai.html')
        else:
            return flask.redirect('/login')
    elif flask.request.method == 'POST':
        if flask.request.form['ai'] == 'YandexGPT-lite':
            return flask.redirect('/pfai/chat')

@app.route('/pfai')
def pfai():
    return flask.render_template('PFAI/home_pfai.html')


@app.route('/pfai/chat', methods=['POST', 'GET'])
def pfai_chat():
    if flask.request.method == 'GET':
        return flask.render_template('PFAI/chat_prew.html', ai_name='YandexGPT Lite', first_quens=True)
    elif flask.request.method == 'POST':
        return flask.render_template('PFAI/chat_prew.html',
                                     answer="Ламинат подойдет для укладке на кухне или в детской", #test_requst(api_key, id_forder, flask.request.form['reqst_text'])
                                     ai_name='YandexGPT Lite')


@app.route('/test')
def bsbsbsb():
    return flask.render_template('PFAI/test.html')

@app.errorhandler(404)
def error404(error):
    return flask.render_template('error404.html')


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run()

