from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit


from werkzeug.utils import secure_filename
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase


import requests

import datetime
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


existingChats = []

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
                points = user_data[8]
                user_info = {
                    'password': password,
                    'age': age,
                    'location': location,
                    'weight': weight,
                    'height': height,
                    'goal': goal,
                    'activity': activity,
                    'points':points
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

rooms = {}
UserData = None
# Route to render the chat page
@app.route("/community", methods=["POST", "GET"])
def community():
    # Load user data
    with open('storage/userData.txt', 'r') as UserDataF:
        UsersData = eval(UserDataF.read())

    # Get current user and selected chat
    myUser = session.get('username')
    currentChatName = request.form.get('chatName')
    memberName = request.form.get('memberName')
    selectedChat = []

    # Check if user exists
    existsClient1 = any(user['user'] == myUser for user in UsersData)

    # Retrieve selected chat contents
    if UsersData:
        for ClientUser in UsersData:
            if ClientUser['user'] == myUser:
                for ChatSpace in ClientUser['chat_spaces']:
                    if ChatSpace['chat_name'] == currentChatName:
                        with open(os.path.join('storage/chats', currentChatName + ".txt"), 'r') as selectedChatFile:
                            selectedChat = [line.strip().split("|") for line in selectedChatFile]
                        break

    # Handling POST request
    if request.method == "POST":
        chat_name = request.form.get('newChatName')
        chat_code = request.form.get('newChatCode')

        # Add new member logic
        if UsersData:
            for ClientUser in UsersData:
                if ClientUser['user'] == myUser:
                    if ClientUser['chat_spaces']:
                        for ChatSpaceOfUser in ClientUser['chat_spaces']:
                            if memberName and ChatSpaceOfUser['chat_name'] == currentChatName and memberName not in ChatSpaceOfUser['chat_members']:
                                # Add member to existing chat
                                ChatSpaceOfUser['chat_members'].append(memberName)
                                for ClientUserX in UsersData:
                                    if ClientUserX['user'] == memberName:
                                        ClientUserX['chat_spaces'].append(ChatSpaceOfUser)
                                with open('storage/userData.txt', 'w') as file:
                                    file.write(str(UsersData))
                                chat_save_name = chat_name + ChatSpaceOfUser['chat_members'][0] + '.txt'
                                with open(os.path.join('storage/chats', chat_save_name), 'w'):
                                    pass

                            if ChatSpaceOfUser['chat_name'] == chat_name:
                                break

                    # Check if new chat needs to be created
                    if not any(ChatSpace['chat_name'] == chat_name for ChatSpace in ClientUser['chat_spaces']) and chat_name and chat_code:
                        ChatSpaceOfUser = {'chat_name': chat_name, 'chat_code': chat_code, 'chat_members': [myUser]}
                        ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                        with open('storage/userData.txt', 'w') as file:
                            file.write(str(UsersData))
                        chat_save_name = chat_name + ChatSpaceOfUser['chat_members'][0] + '.txt'
                        with open(os.path.join('storage/chats', chat_save_name), 'w'):
                            pass

                        # Find chat admin
                        chat_access_variable = currentChatName + ChatSpaceOfUser['chat_members'][0] + '.txt'

                        return render_template("chat.html", userData=ClientUser['chat_spaces'], selected_chat=selectedChat, chatAccessVariable=chat_access_variable)

                    else:
                        # Find chat admin
                        chat_access_variable = currentChatName + ChatSpaceOfUser['chat_members'][0] + '.txt'

                        return render_template("chat.html", userData=ClientUser['chat_spaces'], selected_chat=selectedChat, current_user=myUser, chatAccessVariable=chat_access_variable)

            # Check if new user needs to be created
            if not any(user['user'] == myUser for user in UsersData) and chat_name and chat_code:
                ClientUser = {'user': myUser, 'chat_spaces': []}
                ChatSpaceOfUser = {'chat_name': chat_name, 'chat_code': chat_code, 'chat_members': [myUser]}
                ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                UsersData.append(ClientUser)
                with open('storage/userData.txt', 'w') as file:
                    file.write(str(UsersData))
                chat_save_name = chat_name + ChatSpaceOfUser['chat_members'][0] + '.txt'
                with open(os.path.join('storage/chats', chat_save_name), 'w'):
                    pass

                # Find chat admin
                chat_access_variable = currentChatName + ChatSpaceOfUser['chat_members'][0] + '.txt'

                return render_template("chat.html", userData=ClientUser['chat_spaces'], selected_chat=selectedChat, current_user=myUser, chatAccessVariable=chat_access_variable)

        # If no user or chat exists, return blank template
        else:
            if not UsersData and existsClient1:
                return render_template("chat.html", userData=ClientUser['chat_spaces'], selected_chat=selectedChat, current_user=myUser)
            else:
                return render_template("chat.html")

    # If request method is GET, return chat template
    else:
        if UsersData and existsClient1:
            return render_template("chat.html", userData=ClientUser['chat_spaces'], selected_chat=selectedChat, current_user=myUser)
        else:
            return render_template("chat.html")
        


# Handle WebSocket event to receive and broadcast messages
@socketio.on("send_message")
def handle_message(data):
    chat_name = data["chatName"]
    sender = session.get('username')
    message = data["message"]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_message(chat_name, sender, message, timestamp)  # Save the message to the file
    send_message_to_group(chat_name, sender, message, timestamp)  # Broadcast the message to all clients in the chat

# Function to send message to all clients in the chat group
def send_message_to_group(chat_name, sender, message, timestamp):
    room = chat_name + ".txt"
    socketio.emit("receive_message", {"sender": sender, "message": message, "timestamp": timestamp}, room=room)

def save_message(chat_name, sender, message, timestamp):
    filename = os.path.join("storage/chats", chat_name + ".txt")
    with open(filename, "a") as chat_file:
        chat_file.write(f"{sender}|{message}|{timestamp}\n")\
        
# Function to send message to all clients in the chat
def send_message(chat_name, message):
    socketio.emit("receive_message", message, room=chat_name)

# Route handler to fetch chat data
@app.route("/get_chat_data", methods=["GET"])
def get_chat_data():
    chat_access_variable = request.args.get('chatAccessVariable')
    if chat_access_variable:
        try:
            chat_data = []
            filename = os.path.join('storage/chats', chat_access_variable)
            if os.path.exists(filename):
                with open(filename, 'r') as chat_file:
                    for line in chat_file:
                        parts = line.strip().split("|")
                        chat_data.append({"sender": parts[0], "message": parts[1], "timestamp": parts[2]})
            return jsonify({"success": True, "chatData": chat_data})
        except FileNotFoundError:
            return jsonify({"success": False, "message": "File not found."})
    else:
        return jsonify({"success": False, "message": "Chat access variable not provided."})

@app.route('/leaderboard')
def leaderboard():
    users = get_users()
    sorted_users = sorted(users.items(), key=lambda x: int(x[1]['points']), reverse=True)
    leaderboard_data = [{'username': username, 'points': user_info['points']} for username, user_info in sorted_users]
    UserClient = session['username']
    for user in range(len(leaderboard_data)):
        if UserClient == leaderboard_data[user]['username']:
            position = user
            break
    print(position+1)
    return render_template('leaderboard.html', leaderboard=leaderboard_data)


if __name__ == '__main__':
    socketio.run(app)