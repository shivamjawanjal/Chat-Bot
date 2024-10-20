from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, send
from config import get_database

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
socketio = SocketIO(app)

# Database setup
db = get_database()
users_collection = db['users']
chats_collection = db['chats']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/joinchat', methods=['GET', 'POST'])
def joinChat():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = {'username': username, 'password': password}
        existingUser = users_collection.find_one(user)

        if existingUser and existingUser['password'] == password:
            return render_template('chat.html', username=username)
        else:
            return render_template('index.html', alertMsg='User does not exist with this username or incorrect password')

@app.route('/createuser', methods=['POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        create_user_in_db(username, password)

        return render_template('chat.html', username=username)

@app.route('/createchat', methods=['POST'])
def create_chat_route():
    if request.method == 'POST':
        chat = request.form['chat']
        username = request.form['username']

        create_chat(username, chat)

        chatList = get_chat()
        myChatList = [item for item in chatList if item['username'] == username]
        strangerChatList = [item for item in chatList if item['username'] != username]

        return render_template('chat.html', username=username, myChatList=myChatList, strangerChatList=strangerChatList)

# Serve manifest.json
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

# Serve service-worker.js
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

def create_user_in_db(username, password):
    user = {'username': username, 'password': password}
    result = users_collection.insert_one(user)
    return result.inserted_id

def create_chat(username, chat):
    chat_data = {'username': username, 'chat': chat}
    result = chats_collection.insert_one(chat_data)
    return result.inserted_id

def get_chat():
    chats = chats_collection.find()
    return list(chats)

# SocketIO handlers
@socketio.on('join')
def handle_join(data):
    join_room(data['room'])
    send({'msg': data['username'] + ' has joined the room.'}, room=data['room'])

@socketio.on('leave')
def handle_leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + ' has left the room.'}, room=data['room'])

@socketio.on('message')
def handle_message(data):
    chat_data = {'username': data['username'], 'chat': data['msg']}
    chats_collection.insert_one(chat_data)
    send({'username': data['username'], 'msg': data['msg']}, room=data['room'])

if __name__ == '__main__':
    port = 8000
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
