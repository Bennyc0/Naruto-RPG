import sqlite3

database_link = "./static/data/database.db"

# ---------- Login/Signup ----------
# Verify User
def verify_user(username, password):
    connect = sqlite3.connect(database_link)
    cursor = connect.cursor()

    result = cursor.execute('SELECT * FROM userbase WHERE username = ? AND password = ?', (username, password,))
        
    information = {
        "username": ""
    }
    
    for item in result:
        information = {
            "username": item[0]
        }

    connect.close()
    return information['username']

# Sign Up
def signup_user(username, email, password):
    connect = sqlite3.connect(database_link)
    cursor = connect.cursor()

    cursor.execute('INSERT INTO userbase(username, email, password) VALUES (?, ?, ?)', (username, email, password,))

    connect.commit()
    connect.close()


# ---------- Get User Information ----------
# Gets stats related to the user
# Can also be used to prevent duplicate usernames (if nothing is found, returns blank, meaning email not in use yet)
def get_user_information(username):
    connect = sqlite3.connect(database_link)
    cursor = connect.cursor()

    result = cursor.execute('SELECT * FROM user_stats WHERE username = ?', (username,))
        
    information = {
        'username': "",
        'level': 0,
        'health': 0,
        'attack': 0,
        'defence': 0,
        'skills': []
    }
    
    for item in result:
        information = {
            'username': item[0],
            'level': item[1],
            'health': item[2],
            'attack': item[3],
            'defence': item[4],
            'skills': item[5]
        }

    connect.close()
    return information