import flask
import os
import json
import requests
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.user import RegisterForm, LoginForm
from data.users import User
from data.chats import Chats
from data.api_keys import API_keys
from data.promocodes import Promocode
from data import db_session
from Ai_models.count_tokens_wtf import count_tokens
from Ai_models.yandexgpt import yandexgptlite_requst
from API.generator_api_key import generate_api_key

app = flask.Flask(__name__)
db_session.global_init("db/users.db")
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")


def load_chats_navbar():
    db_sess = db_session.create_session()
    chat_in_db = db_sess.query(Chats).filter(Chats.user_id == current_user.id).all()
    # chat_id = chat_in_db[-1].id
    full_id_chats = {}
    for i in chat_in_db[::-1]:
        full_id_chats[i.id] = [i.name, i.ai_model]
    return full_id_chats

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
                db_sess.close()
                return flask.redirect(f'/profile/{current_user.id}')
            db_sess.close()
            return flask.render_template('login.html', message="Неправильный логин или пароль", form=form)
        return flask.render_template('login.html', title='Авторизация', form=form)
    else:
        return flask.redirect(f'/profile/{current_user.id}')


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
            db_sess.close()
            return flask.redirect(f'/profile/{user.name}')
        return flask.render_template('register.html', form=form)
    else:
        return flask.redirect(f'/profile/{current_user.name}')


@app.route('/profile/<idd>', methods=['GET', 'POST'])
def profile_view(idd):
    if flask.request.method == 'GET':
        db_sess = db_session.create_session()
        all_users = db_sess.query(User).all()
        if current_user.is_authenticated:
            if idd.isdigit() and current_user.id == int(idd):
                find_user = False
                for user in all_users:
                    if int(idd) == user.id:
                        find_user = True
                        break
                if find_user:
                    api_key = db_sess.query(API_keys).filter(API_keys.user_id == int(idd)).first()
                    if api_key:
                        ui_api_key = api_key.api_key
                    else:
                        ui_api_key = ""
                    db_sess.close()
                    status_promo = flask.request.cookies.get("status_promo", "")
                    resp = flask.make_response(flask.render_template('profile_info.html', name=current_user.name, count_tokens=user.count_tokes, user_api_key=ui_api_key, status_promo=status_promo))
                    resp.set_cookie('status_promo', '', max_age=0)
                    return resp
                else:
                    db_sess.close()
                    return flask.render_template('error404.html')
            else:
                db_sess.close()
                return flask.render_template('error404.html')
        else:
            db_sess.close()
            return flask.redirect('/login')
    elif flask.request.method == 'POST':
        promocode_ui = flask.request.form.get('inp_promo')
        resp = flask.make_response(flask.redirect(f'/profile/{current_user.id}'))
        resp.set_cookie('status_promo', check_promo(promocode_ui), max_age=60 * 60 * 24)
        return resp


def check_promo(promocode_ui):
    db_sess = db_session.create_session()
    promocode_db = db_sess.query(Promocode).filter(Promocode.promocode == promocode_ui).first()
    result = 'error:'
    if promocode_db:
        if promocode_db.used_count > 0:
            promocode_db.used_count -= 1
            add_token_for_promo(promocode_db.action)
            result = f'ok:{promocode_db.action}'
        else:
            result += 'Промокод уже неактивен'
    else:
        result += 'Промокод не найден'
    db_sess.commit()
    db_sess.close()
    return result



def add_token_for_promo(action):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if action[0] == "+":
        user.count_tokes += int(action[1:])
    db_sess.commit()
    db_sess.close()


@app.route('/new_api_key')
def new_api_key():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user.api_keys_id != None:
            api_key_for_del = db_sess.query(API_keys).filter(API_keys.id == user.api_keys_id).first()
            db_sess.delete(api_key_for_del)
            db_sess.commit()
        api_key = API_keys(
            api_key=generate_api_key(),
            user_id=current_user.id
        )
        db_sess.add(api_key)
        db_sess.commit()
        api_key_db = db_sess.query(API_keys).filter(API_keys.user_id == current_user.id).first()
        user.api_keys_id = api_key_db.id
        db_sess.commit()
        db_sess.close()
        return flask.redirect(f'/profile/{current_user.id}')
    else:
        return flask.redirect('/')


@app.route('/russian_memory')
def Russian_Memory_view():
    return flask.render_template('russian_memory_view.html')


@app.route('/ai_platform')
def ai_platform():
    return flask.redirect('/pfai')


@app.route('/pfai')
def pfai():
    return flask.render_template('PFAI/home_pfai.html')


@app.route('/pfai/new_chat', methods=['POST', 'GET'])
def pfai_new_chat():
    if flask.request.method == 'GET':
        if current_user.is_authenticated:
            return flask.render_template('PFAI/new_chat_pfai.html', items=load_chats_navbar())
        else:
            return flask.redirect('/login')
    elif flask.request.method == 'POST':
        new_chat = Chats(
            name=flask.request.form["prompt"][:20] + "...",
            ai_model = flask.request.form['ai'],
            text_chat=f'user:{flask.request.form["prompt"]}%#%',
            user_id=current_user.id
        )
        db_sess = db_session.create_session()
        db_sess.add(new_chat)
        db_sess.commit()
        chat_in_db = db_sess.query(Chats).filter(Chats.user_id == current_user.id).all()
        chat_id = chat_in_db[-1].id
        resp = flask.make_response(flask.redirect(f'/pfai/chat/{chat_id}'))
        resp.set_cookie('ai', flask.request.form['ai'], max_age=60 * 60 * 24)
        resp.set_cookie('prompt', flask.request.form['prompt'], max_age=60 * 60 * 24)
        db_sess.close()
        return resp



@app.route('/pfai/chat/<chat_id>', methods=['POST', 'GET'])
def pfai_chat(chat_id):
    db_sess = db_session.create_session()
    chat_in_db = db_sess.query(Chats).filter(Chats.id == chat_id).first()
    if flask.request.method == 'GET':
        if current_user.is_authenticated:
            api_key = db_sess.query(API_keys).filter(API_keys.user_id == current_user.id).first()
            if int(chat_id) in load_chats_navbar():
                if flask.request.cookies.get("prompt", "") != "":
                    answer = make_request(flask.request.cookies.get("prompt", ""), flask.request.cookies.get("ai", "Error"), api_key.api_key)
                    if answer == 404:
                        return flask.redirect('/api_key_invalid')
                    elif answer == 400:
                        return flask.redirect('/need_to_up_tokens')
                    chat_in_db.text_chat = str(chat_in_db.text_chat) + f'ai:{answer}%#%'
                    db_sess.commit()
                    answer_in_db = chat_in_db.text_chat
                    answer = []
                    answer_in_db = answer_in_db.split("%#%")
                    for past in answer_in_db:
                        if "ai:" in past:
                            answer.append("ai")
                            answer.append(past[3:])
                        elif "user:" in past:
                            answer.append("user")
                            answer.append(past[5:])
                    resp = flask.make_response(flask.render_template('PFAI/chat_prew.html', answer=answer, ai_name=chat_in_db.ai_model, items=load_chats_navbar()))
                    resp.set_cookie('prompt', '', max_age=0)
                    resp.set_cookie('ai', '', max_age=0)
                else:
                    answer = []
                    answer_in_db = chat_in_db.text_chat
                    answer_in_db = answer_in_db.split("%#%")
                    for past in answer_in_db:
                        if "ai:" in past:
                            answer.append("ai")
                            answer.append(past[3:])
                        elif "user:" in past:
                            answer.append("user")
                            answer.append(past[5:])
                    resp = flask.make_response(flask.render_template('PFAI/chat_prew.html', answer=answer, ai_name=chat_in_db.ai_model,items=load_chats_navbar()))
                db_sess.close()
                return resp
            else:
                db_sess.close()
                return flask.render_template('error404.html')

        else:
            db_sess.close()
            return flask.redirect('/login')
    elif flask.request.method == 'POST':
        resp = flask.make_response(flask.redirect(f'/pfai/chat/{chat_id}'))
        resp.set_cookie('ai', chat_in_db.ai_model, max_age=60 * 60 * 24)
        resp.set_cookie('prompt', flask.request.form['prompt'], max_age=60 * 60 * 24)
        chat_in_db.text_chat = chat_in_db.text_chat + f'user:{flask.request.form["prompt"]}%#%'
        db_sess.commit()
        db_sess.close()
        return resp



def send_requset(api_key, json_request):
    json_request = json.dumps(json_request)
    response = requests.get(f'http://127.0.0.1:8000/api/v0/{api_key}', data=json_request)
    response_json = response.json()
    if response.status_code == 404:
        return 404
    elif response.status_code == 400:
        return 400
    return response_json["message"]


def make_request(user_prompt, ai_model, api_key_user):
    request = {
        "model": f"{ai_model}",
        "messages": [
            {"role": "system", "content": "Ты полезный ассистент"},
            {"role": "user", "content": f"{user_prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 10000
    }
    return send_requset(api_key_user, request)



def processing_message(message: list) -> list:
    try:
        if message[0]['role'] != 'system':
            return [False, 'Uncorrected request, maybe "system"?', ""]
        if message[1]['role'] != 'user':
            return [False, 'Uncorrected request, maybe "user"?', ""]
        if message[0]['content'] == '':
            return [False, 'Uncorrected request, empty content for system', ""]
        if message[1]['content'] == '':
            return [False, 'Uncorrected request, empty content for user', ""]
        return [True, message[0]['content'], message[1]['content']]
    except:
        return [False, 'Uncorrected request, not enough data', ""]


@app.route('/api_key_invalid')
def api_key_invalid():
    return flask.render_template('tech_web_error_to_you.html')

@app.route('/need_to_up_tokens')
def need_to_up_tokens():
    return flask.render_template('PFAI/error_not_money_in_api.html')


@app.route('/test')
def bsbsbsb():
    return flask.render_template('PFAI/test.html')


@app.errorhandler(404)
def error404(error):
    return flask.render_template('error404.html')


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run()
