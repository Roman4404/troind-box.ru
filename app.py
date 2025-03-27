import flask
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from data.news import News
from data.users import User
from data import db_session


app = flask.Flask(__name__)
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
                return flask.render_template('profile_info.html', name=name)
            else:
                return flask.render_template('error404.html')
        else:
            return flask.render_template('error404.html')
    else:
        return flask.redirect('/login')


@app.route('/russian_memory')
def Russian_Memory_view():
    return flask.render_template('russian_memory_view.html')

if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run()