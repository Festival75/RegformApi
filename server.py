import flask
from flask import request, render_template, redirect
import json
from wtforms import Form, StringField, PasswordField, validators, DateField
import hashlib
import re

app = flask.Flask(__name__)


def read_json(path: str) -> dict:
    """Считать данные из .json"""
    try:
        with open(path) as data_file:
            data = json.load(data_file)
        return data
    except ValueError as e:
        print('invalid json: %s' % e)
        exit(0)
    except FileNotFoundError:
        print('file not found')
        exit(0)


class RegistrationForm(Form):
    """Шаблон формы для Jinja с валидацией полей"""
    users = read_json('users.json')
    logins = []
    for user in users['data']:
        logins.append(user['login'])
    first_name = StringField('Имя', [validators.Length(min=0, max=32, message='Длина не более 32х символов'),
                                     validators.Regexp('^[A-ZА-Я][а-я]*[a-z]*$', message='Содержит латиницу или кириллицу, без смешивания. Первая буква - верхний регистр, остальные- нижний.'),
                                     validators.DataRequired(message='Обязательное поле')], render_kw={'placeholder': ' Иван/John'})
    last_name = StringField('Фамилия', [validators.Length(min=0, max=32, message='Длина не более 32х символов'),
                                        validators.Regexp('^[A-ZА-Я][а-я]*[a-z]*$', message='Содержит латиницу или кириллицу, без смешивания. Первая буква - верхний регистр, остальные- нижний.'),
                                        validators.DataRequired(message='Обязательное поле')], render_kw={'placeholder': ' Иванов/Doe'})
    login = StringField('Логин', [validators.Length(min=0, max=32, message='Длина не более 32х символов'),
                                  validators.Regexp('^[a-zA-Z\d]*$', message='Содержит цифры и/или латиницу произвольного регистра'),
                                  validators.NoneOf(logins, message='Такой логин уже используется'),
                                  validators.DataRequired(message='Обязательное поле')], render_kw={'placeholder': ' jAcK1990'})
    password = PasswordField('Пароль', [validators.Length(min=8, max=32, message='Длина не менее 8ми и не более 32х символов'),
                                        validators.Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}', message='Содержит латиницу (как минимум один символ в нижнем регистре, и как минимум один символ в верхнем регистре), цифры (как минимум один символ), и печатные спецсимволы (как минимум один символ).'),
                                        validators.NoneOf(logins, message='Пароль и логин не должны совпадать'),
                                        validators.DataRequired(message='Обязательное поле')], render_kw={'placeholder': ' Super$$ecret1'})
    birth_date = DateField('День рождения', [validators.DataRequired(message='Формат даты ДД.ММ.ГГГГ'),
                                             validators.DataRequired(message='Обязательное поле')], format='%d.%m.%Y', render_kw={'placeholder': ' 25.01.1990'})


def to_json(data: str) ->dict:
    """записать произвольную строку в json"""
    return json.dumps(data) + "\n"


def resp(code: int, data: dict) ->object:
    """Формирует response на основе входных данных, тип данных - json"""
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


@app.route('/', methods=['GET', 'POST'])
def main() -> object:
    """Обработчик домашней страницы, возвращает отрисованный Jinja index.html"""
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect('/')
    return render_template('index.html', form=form)


@app.route('/api/users', methods=['POST'])
def new_user() -> object:
    """Обработчик для POST запроса /api/users, получает из запроса json и записывает в фаил"""
    data = request.get_json(force=True)
    first_name = data['first_name']
    last_name = data['last_name']
    input_type = 'en' if re.match(r'^[A-Z][a-z]*$', first_name) else 'ru'
    if re.match('^[А-Я][а-я]*$', last_name) and input_type == 'en':
        return resp(200, {"data": "Имя и Фамилия должны быть в одной раскладке"})
    login = data['login']
    password = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
    birth_date = data['birth_date']
    if int(birth_date[:4]) < 1999:
        return resp(200, {"data": "Пользователям младше 18 лет регистрация запрещена"})
    with open('users.json', 'r+') as f:
        users = json.load(f)
        new_user = {}
        new_user['id'] = [int(len(users['data']) + 1)][0]
        new_user['first_name'] = first_name
        new_user['last_name'] = last_name
        new_user['login'] = login
        new_user['password'] = password
        new_user['birth_date'] = birth_date
        users['data'].append(new_user)
        f.seek(0)
        json.dump(users, f, indent=4)
    return resp(200, {"data": data})


@app.route('/api/users', methods=['GET'])
def get_page() -> object:
    """Обработчик для GET запроса /api/users, получает из запроса номер страницы, выводит записи с этой страницы"""
    page = request.args.get('page', default=1, type=int)
    data = read_json('users.json')
    per_page = data['per_page']
    total = len(data['data'])
    total_pages = int(total / per_page)
    if page <= total_pages:
        users = []
        for count in range(page * per_page - 1, page * per_page - 4, -1):
            user = data['data'][count]
            users.append({"id": user['id'], "first_name": user['first_name'], "second_name": user['last_name'],
                          "login": user['login'], "password": user['password'], "birth_date": user['birth_date']})

        return resp(200, {"data": users})
    else:
        return resp(404, {})


@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    """Обработчик для GET запроса api/users/id, получает из запроса id, выводит пользователя с этим id"""
    data = read_json('users.json')
    users = []
    for user in data['data']:
        if id == user['id']:
            users.append({"id": user['id'], "first_name": user['first_name'], "second_name": user['last_name'],
                          "login": user['login'], "password": user['password'], "birth_date": user['birth_date']})
    return resp(200, {"data": users})


if __name__ == '__main__':

    app.debug = True
    app.run()
