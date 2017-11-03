# RegformApi

Работа по тестовому заданию.
Проект выполнен с использованием Flask и WTForms
Веб-форма - templates/index.html
Для красоты добавил css в папке static/css. Так же темплейт ссылается на онлайн версию bootstrap.

Реализовано:

- Написана веб-форма, с использованием HTML5 и CSS3, а так же WTForms и шаблонизатора Jinja.
- Валидация введенных значений на этапе отправки формы.
- Проверка корректности json-файла перед началом работы.
- REST-сервис, обработка следующих запросов:
    
    GET /api/users?page=1 - - получение страницы по указанному номеру, выводится по 3 записи на странцу. Данные берутся из пункта "per_page" json-файла.
    
    GET /api/users/2 - получение конкретного юзера по его id.
    
    POST /api/users - добавление нового пользователя.
    

Проблемы:

- Веб форма отправляет данные типа выполняя нужный POST запрос, однако обработчик этого запроса new_user() не может распарсить json из запроса. Если выполнять POST запрос другими методами (например утилита Postman от Google) то все парсится корректно. Буду благодарен за помощь в решении данной проблемы.
- Не реализована проверка единой раскладки для имени и фамилии на этапе заполнения, в качестве "костыля" реализовал эту проверку на этапе добавления нового пользователя в json-фаил.
- Та же ситуация с возрастом регестрируемого пользователя.

Зависимости:

Flask==0.12.2
WTForms==2.1

Запуск:

1) Запустить приложение Flask (server.py) выполнив python server.py
2) Перейти по адресу http://127.0.0.1:5000/