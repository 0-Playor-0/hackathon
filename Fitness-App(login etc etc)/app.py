from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename


import requests

import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'


def get_users():
    with open('users.txt', 'r') as file:
        users = {}
        for line in file.readlines():
            user_data = line.strip().split(':')
            if len(user_data) >= 7:
                username = user_data[0]
                password = user_data[1]
                age = user_data[2]
                location = user_data[3]
                weight = user_data[4]
                height = user_data[5]
                goal = user_data[6]
                activity = user_data[7]
                user_info = {
                    'password': password,
                    'age': age,
                    'location': location,
                    'weight': weight,
                    'height': height,
                    'goal': goal,
                    'activity': activity
                }
                users[username] = user_info
        return users

def save_user(username, password, age='', location='', weight='', height='', goal='', activity=''):
    with open('users.txt', 'a') as file:
        file.write(f'{username}:{password}:{age}:{location}:{weight}:{height}:{goal}:{activity}\n')


def get_random_quote():
    response = requests.get('https://api.quotable.io/random')
    if response.status_code == 200:
        data = response.json()
        return data['content']
    return 'No quote available'

def get_greeting():
  current_time = datetime.datetime.now()
  print(current_time)
  if current_time.hour < 12:
      return 'Good morning'
  elif 12 <= current_time.hour < 18:
      return 'Good afternoon'
  else:
      return 'Good evening'

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        quote = get_random_quote()
        greeting = get_greeting()
        posts = get_posts()
        return render_template('index.html', quote=quote, greeting=greeting, username=username, posts=posts)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = get_users()
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = get_users()
        if username in users:
            return 'Username already exists'
        else:
            save_user(username, password)
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        username = session['username']
        users = get_users()
        if request.method == 'POST':
            age = request.form.get('age', '')
            location = request.form.get('location', '')
            weight = request.form.get('weight', '')
            height = request.form.get('height', '')
            goal = request.form.get('goal', '')
            activity = request.form.get('activity', '')
            users[username]['age'] = age
            users[username]['location'] = location
            users[username]['weight'] = weight
            users[username]['height'] = height
            users[username]['goal'] = goal
            users[username]['activity'] = activity
            with open('users.txt', 'w') as file:
                for user, data in users.items():
                    file.write(f"{user}:{data['password']}:{data['age']}:{data['location']}:{data['weight']}:{data['height']}:{data['goal']}:{data['activity']}\n")
            session['profile'] = users[username]
            return redirect(url_for('index'))
        else:
            user_info = users.get(username, {})
            session['profile'] = user_info
            return render_template('profile.html', user_info=user_info)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('profile', None)
    return redirect(url_for('index'))

def get_posts():
    posts = []
    
    if os.path.exists('posts.txt'):
        with open('posts.txt', 'r') as file:
            for line in reversed(file.readlines()): 
                post_data = line.strip().split(':')
                print(url_for('static', filename='uploads/' + post_data[0]))
                if len(post_data) >= 3:
                    post = {
                        'image':url_for('static', filename='uploads/' + post_data[0]),
                        'caption': post_data[1],
                        'username': post_data[2]
                    }
                    posts.append(post)
    return posts

def save_post(image_filename, caption, username):
    with open('posts.txt', 'a') as file:
        file.write(f'{image_filename}:{caption}:{username}\n')

@app.route('/add_post', methods=['POST'])
def add_post():
    if 'username' in session:
        username = session['username']
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                # Save image file
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Save post data
                caption = request.form.get('caption', '')
                save_post(filename, caption, username)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)