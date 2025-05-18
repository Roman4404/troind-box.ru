# PFAI

## [Ccылка на сайт📝](http://51.250.34.28:5000/pfai)
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
9.Создайте файл "ai.py" и поставьте значения с [сайта](http://51.250.34.28:5000/pfai/need/api_and_keys)
```python
YandexGPT_Lite_API = # API keys
YandexGPT_Lite_Folder_ID = # Folder ID
```
10.Вернитесь в начальную папку
```shell
cd ..
cd ..
```
11.Запустите "app.py" возьмите значения secret_key с [сайта](http://51.250.34.28:5000/pfai/need/api_and_keys)
```shell
SECRET_KEY=<secret_key с сайта> python app.py
```
12.Откройте другой терминал и запустите "main_api.py"
```shell
python main_api.py
```
Всё готово!

## Структура:

