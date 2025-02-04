from flask import Flask, render_template_string, request, redirect, url_for
from instagrapi import Client
import time
import threading

app = Flask(__name__)

# Global flag to stop the process
stop_flag = False

# Function to login to Instagram
def login_instagram(username, password):
    cl = Client()
    cl.login(username, password)
    return cl

def change_nickname_in_group(cl, thread_id, new_nickname, delay_seconds):
    global stop_flag
    thread = cl.direct_thread(thread_id)  # Fetch thread using direct_thread

    for user in thread.users:
        if stop_flag:  # Check the stop flag
            print("Process stopped by the user.")
            break

        try:
            print(f"Changing nickname for user {user.username} to {new_nickname}")
            cl.direct_thread_edit_title(thread_id, new_nickname)  # Corrected method
            print(f"Nickname changed to {new_nickname}")
            time.sleep(delay_seconds)
        except Exception as e:
            print(f"Error changing nickname for {user.username}: {str(e)}")

# HTML template as a string
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Nickname Changer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 50px;
        }
        .container {
            width: 400px;
            margin: auto;
        }
        input[type="text"], input[type="password"], input[type="number"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
        }
        button:hover {
            background-color: #0056b3;
        }
        h1 {
            text-align: center;
        }
        .stop-btn {
            background-color: #e74c3c;
        }
        .stop-btn:hover {
            background-color: #c0392b;
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>Instagram GC Nickname Changer Made By Anish:-</h1>
        <form method="POST">
            <label for="username">Instagram Username:</label>
            <input type="text" name="username" id="username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" name="password" id="password" required>

            <label for="thread_id">Thread ID:</label>
            <input type="text" name="thread_id" id="thread_id" required>

            <label for="new_nickname">New Nickname:</label>
            <input type="text" name="new_nickname" id="new_nickname" required>

            <label for="delay_seconds">Delay (seconds):</label>
            <input type="number" name="delay_seconds" id="delay_seconds" value="2" required>

            <button type="submit">Change Nicknames</button>
        </form>

        <form method="POST" action="/stop">
            <button class="stop-btn" type="submit">Stop</button>
        </form>
    </div>

</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    global stop_flag
    if request.method == 'POST':
        # Get the form data for nickname changing
        username = request.form['username']
        password = request.form['password']
        thread_id = request.form['thread_id']
        new_nickname = request.form['new_nickname']
        delay_seconds = int(request.form['delay_seconds'])

        # Reset stop flag before starting
        stop_flag = False

        # Log in to Instagram and start changing nicknames in a separate thread
        cl = login_instagram(username, password)
        threading.Thread(target=change_nickname_in_group, args=(cl, thread_id, new_nickname, delay_seconds)).start()

        return redirect(url_for('index'))  # Redirect to the home page after processing

    return render_template_string(html_template)

@app.route('/stop', methods=['POST'])
def stop():
    global stop_flag
    stop_flag = True
    return redirect(url_for('index'))  # Redirect back to the home page after stopping

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
