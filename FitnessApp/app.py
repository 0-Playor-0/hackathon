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
app.config['UPLOAD_FOLDER'] = 'static/uploads'


existingChats = []

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

@app.route("/community", methods=["POST", "GET"])
def community():
    UserDataF = open('storage\\userData.txt','r')
    UsersData = eval(UserDataF.read())
    myUser = session['username']
    existsClient1 = False
    
    print(rooms)

    if len(UsersData)>0:
        for ClientUser in UsersData:
            if ClientUser['user'] == myUser:
                existsClient1 = True
                break
    #Adding the new member when accessed:
    #Now you can use the chat_name variable in your Flask route logic
    #Adding the new member when accessed

    if request.method == "POST":
        chat_name = request.form.get('newChatName')
        chat_code = request.form.get('newChatCode')
        room = chat_name
        
        if room not in rooms:
            rooms[room] = {"members": 0, "messages": []}
            session['room'] = room
        
        currentChatName = request.form.get('chatName')
        memberName = request.form.get('memberName')
        print(memberName,currentChatName)
        Saved = None
        if len(UsersData)>0:
            existsClient = False
            for ClientUser in UsersData:
                existsChat = False
                if ClientUser['user'] == myUser:
                    existsClient = True
                    if len(ClientUser['chat_spaces'])>0:
                        for ChatSpaceOfUser in ClientUser['chat_spaces']:
                            if memberName!=None:
                                print(ChatSpaceOfUser, ClientUser)
                                if ChatSpaceOfUser['chat_name'] == currentChatName and memberName not in ChatSpaceOfUser['chat_members']:
                                    ChatSpaceOfUser['chat_members'].append(memberName)
                                    doesExist = False
                                    Saved = ChatSpaceOfUser
                                    if len(ChatSpaceOfUser['chat_members'])>1:
                                        for ClientUserX in UsersData:
                                            if ClientUserX['user'] == memberName:
                                                if Saved != None:
                                                    ClientUserX['chat_spaces'].append(Saved)
                                            with open('storage\\userData.txt','w') as file:
                                                file.write(str(UsersData))
                                                file.close()
                                            if ClientUserX['user'] != myUser and ClientUserX['user']!=memberName and ClientUserX['user'] in ChatSpaceOfUser['chat_members']:
                                                for ChatSpaceOfUserX in ClientUserX['chat_spaces']:
                                                    if ChatSpaceOfUserX['chat_name'] == currentChatName:
                                                        ChatSpaceOfUserX['chat_members'] = ChatSpaceOfUser['chat_members']
                                            if ClientUserX['user']==memberName:
                                                doesExist = True

                                    if doesExist == False:
                                        ClientUserNew = {'user':memberName,'chat_spaces':[]}
                                        if Saved != None:
                                            ClientUserNew['chat_spaces'].append(Saved)
                                        UsersData.append(ClientUserNew)
                                    with open('storage\\userData.txt','w') as file:
                                        file.write(str(UsersData))
                                        file.close()
                                
                                    
                                    
                            
                            if ChatSpaceOfUser['chat_name'] == chat_name:
                                existsChat = True
                                
                    if existsChat != True and chat_name != None and chat_code != None:
                        ChatSpaceOfUser = {'chat_name':chat_name,'chat_code':chat_code,'chat_members':[myUser]}
                        ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                        with open('storage\\userData.txt','w') as file:
                            file.write(str(UsersData))
                            file.close()
                        
                        
                        # Pass UserData to the frontend
                        return render_template("chat.html", existingChats=existingChats, userData=ClientUser['chat_spaces'])
                        
                    else:
                        return render_template("chat.html",userData = ClientUser['chat_spaces'])
                    
            
                        
                                

            
            if existsClient == False and chat_name!=None and chat_code !=None:
                ClientUser = {'user':myUser,'chat_spaces':[]}
                ChatSpaceOfUser = {'chat_name':chat_name,'chat_code':chat_code,'chat_members':[myUser]}
                ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                UsersData.append(ClientUser)
                with open('storage\\userData.txt','w') as file:
                    file.write(str(UsersData))
                    file.close()
                
                # If the request method is GET, simply render the chat.html template
                return render_template("chat.html", existingChats=existingChats, userData=ClientUser['chat_spaces'])

        else:
            if chat_name != None and chat_code != None:
                ClientUser = {'user':myUser,'chat_spaces':[]}
                ChatSpaceOfUser = {'chat_name':chat_name,'chat_code':chat_code,'chat_members':[myUser]}
                ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                UsersData.append(ClientUser)
                with open('storage\\userData.txt','w') as file:
                    file.write(str(UsersData))
                    file.close()
                
                # If the request method is GET, simply render the chat.html template
                return render_template("chat.html", existingChats=existingChats, userData=ClientUser['chat_spaces'])
            else:
                if len(UsersData)>0 and existsClient1 == True:
                    return render_template("chat.html",userData=ClientUser['chat_spaces'])
                else:
                    return render_template("chat.html")
        
    else:
        if len(UsersData)>0 and existsClient1 == True:
            return render_template("chat.html",userData=ClientUser['chat_spaces'])
        else:
            return render_template("chat.html")
        
@app.route("/community/<room_name>")
def roomF(room_name):
    print(room_name)
    room = str(room_name)
    session['room'] = str(room_name)
    #Based on the room_name and currentUser find out the roomCode.
    print(rooms)
    if room is None or room not in rooms:
        rooms[room] = {"members": 0, "messages": []}
        return render_template("room.html", code=room, messages=rooms[room]["messages"], name = session['username'])

    return render_template("room.html", room_name=room, messages=rooms[room]["messages"], name=session['username'])



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



#Extra Code for API's and easy access ---------------------------------------------------------------------------->


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

import json
import requests
url = 'http://127.0.0.1:8000/toxicity_pred'
furl = 'http://127.0.0.1:8002/feeling_pred'

import re

@socketio.on("message")
def message(data):
    # Update user points
    if 'message' not in data:
        print("Error: 'message' property is missing in the data")
        return
    
    users = get_users()
    UserClient = session.get('username')
    if UserClient in users:
        session['points'] = int(users[UserClient]['points'])

    print("Message received:", data)
    room = session.get('room')
    if room not in rooms:
        return 
    
    # The code for toxicity detection and content filtering remains unchanged

    input_data_for_model = {
        'StringInput': str(data.get("message"))
    }

    input_json = json.dumps(input_data_for_model)
    response = requests.post(url, data=input_json)

    if response.status_code == 200:
        response_text = str(response.text.strip().strip('"'))
        print(response_text)
    else:
        print(f"Error: {response.status_code} {response.text}")    
        return

    response_lines = response_text.strip().split('\\n')
    print(response_lines)

    flag = None
    for line in response_lines:
        print(line)
        if ':' in line:
            key, value = line.split(':', 1)
            if value.strip() == 'True':
                flag = key.strip()
                break

    if flag:
        content = {
            "name": "",
            "message": f"This message has been censored due to being {flag}."
        }
    else:       
        content = {
            "name": session.get('username', ""),
            "message": data.get("message", "")
        }
    
    fesponse = requests.post(furl, data=input_json)

    if fesponse.status_code == 200:
        fesponse_text = str(fesponse.text.strip().strip('"'))
    else:
        print(f"Error: {fesponse.status_code} {fesponse.text}")    

    fesponse_lines = fesponse_text.strip().split('\\n')
    print(fesponse_lines)

    Flag = None
    for line in fesponse_lines:
        print(line)
        if ':' in line:
            key, value = line.split(':', 1)
            if value.strip() == 'True':
                Flag = key.strip()
                break
    if Flag == None:        
        session['points'] += 5
        session['feeling'] = "Ok"
    else:
        session['feeling'] = Flag
    
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('username')} said: {data.get('message', '')}")

    # Check if the message starts with "@Fitbot" (case insensitive)
    if data.get("message").strip().lower().startswith("@fitbot"):
        # Call ChatGPT API to generate a response
        input_text = f"Scenario: I am feeling {session['feeling']}.Keep what im feeling in mind while responding Query: " + data.get("message")
        input_text = str(input_text)        
        # Call function to generate response from ChatGPT model
        fitbot_response = generate_chatgpt_response(input_text)
        
        # Prepare content for Fitbot response
        fitbot_content = {
            "name": "Fitbot",
            "message": fitbot_response
        }
        
        # Send Fitbot response to the room
        send(fitbot_content, to=room)
        rooms[room]["messages"].append(fitbot_content)
        
        # Update user points
        session['points'] -= 5
    # Check if the message starts with "@Fitbot" (case insensitive)
    if data.get("message").strip().lower().startswith("@picbot"):
        # Call ChatGPT API to generate a response
        input_text = data['message']
        input_text = str(input_text)        
        # Call function to generate response from ChatGPT model
        picbot_response = generate_dalle_response(input_text)
        
        # Prepare content for Fitbot response
        picbot_content = {
            "name": "Picbot",
            "message": picbot_response
        }
        
        # Send Fitbot response to the room
        send(picbot_content, to=room)
        rooms[room]["messages"].append(picbot_content)
        
        # Update user points
        session['points'] -= 5

    

@socketio.on("connect")
def connect(auth):
    if 'room' not in session:
        # Handle the case where 'room' key is not set in the session
        # Log an error or return an error response
        return

    room = session['room']
    name = session.get('username')
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session['room']
    name = session['username']
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

def generate_dalle_response(message):
    import openai

    openai.api_key = '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'

    prompt = message

    image_resp = openai.create(prompt="message", n=4, size="512x512")

    print(image_resp.data[0].url)

    return image_resp.data[0].url


def generate_chatgpt_response(message):
    import openai

    # API key here
    openai.api_key = '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'

    prompt = message

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chat assistant fitbot who helps users with fitness, mental health and meditation related queries. Also you keep the users engaged."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=250,
    )

    return response.choices[0].message.content.strip()
    
if __name__ == '__main__':
    socketio.run(app)