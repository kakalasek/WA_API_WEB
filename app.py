from flask import Flask, render_template, request, flash, redirect, url_for
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = os.urandom(12)

load_dotenv()
api_url = os.getenv("API_URL")

current_results = None

@app.route('/', methods=["GET", "POST"])
def home():
    global current_results

    if request.method == "POST" and 'create-post' in request.form:
        json_output = {"author": request.form['author'], "text": request.form['text']}
        current_results = requests.post(f"{api_url}/api/blog", json=json_output).content.decode('utf-8')
        return redirect(url_for('home'))
    elif request.method == 'POST' and 'get-post' in request.form:
        id = request.form['id']
        current_results = requests.get(f"{api_url}/api/blog/{id}").content.decode('utf-8')
        return redirect(url_for('home'))
    elif request.method == 'POST' and 'delete-post' in request.form:
        id = request.form['id']
        current_results = requests.delete(f"{api_url}/api/blog/{id}").content.decode('utf-8')
        return redirect(url_for('home'))
    elif request.method == 'POST' and 'patch-post' in request.form:
        id = request.form['id']
        new_text = request.form['new-text']
        current_results = requests.patch(f"{api_url}/api/blog/{id}", json={"text": new_text}).content.decode('utf-8')
        return redirect(url_for('home'))
    elif request.method == 'POST' and 'get-all' in request.form:
        current_results = requests.get(f"{api_url}/api/blog").content.decode('utf-8')
        return redirect(url_for('home'))

    return render_template('home.html', results=current_results)


if __name__ == "__main__":
    app.run(port=8080, debug=True)