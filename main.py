from flask import Flask, request, jsonify, render_template_string
from instagrapi import Client
import time
import threading

app = Flask(__name__)

# Global flag to control nickname changing process
stop_flag = False

# HTML Frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Nickname Automation By Hater</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #007bff;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: #333;
            color: white;
            border-radius: 10px;
            padding: 20px;
            width: 300px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        h1 {
            font-size: 18px;
            text-align: center;
            margin-bottom: 20px;
            color: orange;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
        }
        button {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background-color: orange;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: darkorange;
        }
        .stop-button {
            background-color: red;
        }
        .stop-button:hover {
            background-color: darkred;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Group Nickname Automation By Hater</h1>
        <form id="automationForm">
            <input type="text" id="username" placeholder="Instagram Username" required>
            <input type="password" id="password" placeholder="Instagram Password" required>
            <input type="text" id="chatId" placeholder="Target Group Chat ID" required>
            <input type="text" id="newNickname" placeholder="New Nickname" required>
            <input type="number" id="delay" placeholder="Delay (seconds)" min="1" required>
            <button type="submit">Change Nicknames</button>
        </form>
        <button class="stop-button" id="stopButton">Stop Changing</button>
        <p id="result" style="text-align: center; margin-top: 10px;"></p>
    </div>

    <script>
        const form = document.getElementById('automationForm');
        const stopButton = document.getElementById('stopButton');
        const result = document.getElementById('result');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const chatId = document.getElementById('chatId').value;
            const newNickname = document.getElementById('newNickname').value;
            const delay = document.getElementById('delay').value;

            result.textContent = 'Processing...';

            try {
                const response = await fetch('/change-nicknames', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, chatId, newNickname, delay })
                });
                const data = await response.json();
                result.textContent = data.message;
            } catch (error) {
                result.textContent = 'An error occurred. Please try again.';
            }
        });

        stopButton.addEventListener('click', async () => {
            result.textContent = 'Stopping process...';

            try {
                const response = await fetch('/stop-changing', { method: 'POST' });
                const data = await response.json();
                result.textContent = data.message;
            } catch (error) {
                result.textContent = 'An error occurred while stopping the process.';
            }
        });
    </script>
</body>
</html>
"""

# Route to serve the HTML
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Backend API route to change nicknames
@app.route('/change-nicknames', methods=['POST'])
def change_nicknames():
    global stop_flag
    stop_flag = False
    data = request.json
    username = data.get('username')
    password = data.get('password')
    chat_id = data.get('chatId')
    new_nickname = data.get('newNickname')
    delay = int(data.get('delay', 1))

    if not all([username, password, chat_id, new_nickname]):
        return jsonify({"message": "All fields are required!"}), 400

    def nickname_changer():
        global stop_flag
        try:
            client = Client()
            client.login(username, password)
            participants = client.direct_thread(chat_id).users

            for user in participants:
                if stop_flag:
                    break
                client.direct_thread_update_title(chat_id, new_nickname)
                time.sleep(delay)

        except Exception as e:
            print(f"Error: {str(e)}")

    thread = threading.Thread(target=nickname_changer)
    thread.start()
    return jsonify({"message": "Nickname change process started."})

# Backend API route to stop nickname changing
@app.route('/stop-changing', methods=['POST'])
def stop_changing():
    global stop_flag
    stop_flag = True
    return jsonify({"message": "Stopping nickname change process..."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
