from flask import Flask, render_template, redirect, url_for, request
from dotenv import load_dotenv 
import requests
import os

load_dotenv()
api_url = os.getenv("API_ENDPOINT")

current_username = None
message = ''
error = ''
access_token = None
refresh_token = None
current_results = ''

def create_app():
    app = Flask(__name__)
    
    @app.route('/home', methods=['GET', 'POST'])
    @app.route('/', methods=['GET', 'POST'])
    def home():
        global message
        global error
        global access_token
        global refresh_token
        global current_results
        global current_username


        if request.method == "POST":
            if 'error' in requests.get(f"{api_url}/api/auth/whoami", headers={"Authorization": f"Bearer {access_token}"}).json() and current_username:
                result = requests.get(f"{api_url}/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}).json()
                access_token = result['access_token']

        if request.method == "POST" and 'create-post' in request.form:
            data = request.form
            json = {"text": data['text']}
            results = requests.post(f"{api_url}/api/blog", json=json, headers={"Authorization": f"Bearer {access_token}"}).json()
            
            if 'message' in results.keys():
                message = results['message']
            if 'error' in results.keys():
                error = results['error']

            return redirect(url_for('home'))

        elif request.method == 'POST' and 'get-post' in request.form:

            id = request.form['id']
            data = requests.get(f"{api_url}/api/blog/{id}").json()
            error, message = '', ''
            current_results = ''

            if "date" in data: 
                current_results = [{"date": data["date"], "text": data["text"], "user": data['user']}]
            
            if 'message' in data.keys():
                message = data['message']
            if 'error' in data.keys():
                error = data['error']

            return redirect(url_for('home'))

        elif request.method == 'POST' and 'delete-post' in request.form:
            error, message = '', ''
            current_results = ''
            id = request.form['id']
            results = requests.delete(f"{api_url}/api/blog/{id}", headers={"Authorization": f"Bearer {access_token}"} ).json()
            
            if 'message' in results.keys():
                message = results['message']
            if 'error' in results.keys():
                error = results['error']

            return redirect(url_for('home'))

        elif request.method == 'POST' and 'patch-post' in request.form:
            error, message = '', ''
            current_results = ''
            id = request.form['id']
            new_text = request.form['new-text']

            results = requests.patch(f"{api_url}/api/blog/{id}", json={"text": new_text}, headers={"Authorization": f"Bearer {access_token}"}).json()
            
            if 'message' in results.keys():
                message = results['message']
            if 'error' in results.keys():
                error = results['error']

            return redirect(url_for('home'))

        elif request.method == 'POST' and 'get-all' in request.form:
            current_results = ''
            current_results = requests.get(f"{api_url}/api/blog").json()

            return redirect(url_for('home'))


        return render_template('home.html', username=current_username, message=message, error=error, results=current_results)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        global message
        global error

        if request.method == "POST":
            data = request.form
            username = data['username']
            password = data['password']
            message, error = '',''

            results = requests.post(url=f"{api_url}/api/auth/register", json={"username": username, "password": password}).json()

            if 'message' in results.keys():
                message = results['message']
            if 'error' in results.keys():
                error = results['error']

            return redirect(url_for('register'))

        return render_template('register.html', username=current_username, message=message, error=error)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        global message
        global error
        global access_token
        global refresh_token
        global current_username

        if request.method == "POST":
            data = request.form
            username = data['username']
            password = data['password']
            message, error = '', ''
            
            results = requests.post(url=f"{api_url}/api/auth/login", json={"username": username, "password": password}).json()

            if 'tokens' in results.keys():
                access_token = results['tokens']['access']
                refresh_token = results['tokens']['refresh']
                current_username = username 
            
            if 'message' in results.keys():
                message = results['message']
            if 'error' in results.keys():
                error = results['error']

            return redirect(url_for('login'))

        return render_template('login.html', username=current_username, message=message, error=error)
    
    @app.route('/logout')
    def logout():
        global access_token
        global refresh_token
        global current_username
        global message
        global error

        message, error = '', ''
        if access_token and refresh_token:
            results = requests.get(url=f"{api_url}/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"}).json()

            if 'message' in results.keys():
                message = results['message']

            results = requests.get(url=f"{api_url}/api/auth/logout", headers={"Authorization": f"Bearer {refresh_token}"}).json()

            if 'message' in results.keys():
                message = message + ' and ' + results['message']

            access_token = None
            refresh_token = None
            current_username = ''

            if 'error' in results.keys():
                error = results['error']

        return redirect(url_for('login', username=current_username, message=message, error=error))
    
    return app