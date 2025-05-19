# PFAI

## [Ccылка на сайт📝](http://51.250.34.28:5000/pfai)
## Для теста сайта используйте промокод: "полтинник"
Автор идеи: https://github.com/Roman4404

## Как запустить проект
0. Проверить что версия python 3.9 < версия python < 3.13 
1. Клонируйте репозиторий
```shell
git clone https://github.com/Roman4404/troind-box.ru.git
```
2. Перейдите в папку проекта
```shell
cd ./troind-box.ru/
```
3.Создайте и активируйте виртуальное окружение
```shell
python -m venv venv
venv\Scripts\activate.bat
```
4.Установите необходимые библиотеки
```shell
pip install -r requirements.txt
```
5.Создайте папку "db" для базы данных
```shell
mkdir db
```
6.Перейдите в папку "Ai_models"
```shell
cd Ai_models
```
7.Создайте папку "keys" для хранения API ключей
```shell
mkdir keys
```
8.Перейдите в папку "keys"
```shell
cd keys
```
9.Создайте файл "ai.py" и поставьте значения с http://51.250.34.28:5000/pfai/need/api_and_keys
```python
YandexGPT_Lite_API = # API keys
YandexGPT_Lite_Folder_ID = # Folder ID
```
10.Вернитесь в начальную папку
```shell
cd ..
cd ..
```
11.Запустите "app.py" возьмите значения secret_key с http://51.250.34.28:5000/pfai/need/api_and_keys
```shell
SECRET_KEY=<secret_key с сайта> python app.py
```
12.Откройте другой терминал и запустите "main_api.py"
```shell
python main_api.py
```
Всё готово!

app.py - Сайт
<br>
main_api.py - API сайта

## Как использовать API PFAI
Для использования API PFAI рекомендую установить [Postman](https://www.postman.com/)

Ссылка для отправки запроса в API PFAI:
<br>
```http request
http://localhost:8000/api/v0/Ваш API ключ с личного кабинета на сайте
```
Тело запроса json:
```json
{
  "model": "YandexGPT-lite", 
  "messages": [
    {"role": "system", "content": "Ты полезный ассистент"},
    {"role": "user", "content": "Где находятся Красноярские столбы?"}
  ],
  "temperature": 0.7,
  "max_tokens": 10000
}
```
**AI модели доступные для запроса:YandexGPT-lite, YandexGPT-pro, Llama-8b, Llama-70b**
<br>
**Для изменения AI модели в запросе поменяйте пункт 'model'**