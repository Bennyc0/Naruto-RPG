import sqlite3

database_link = "./static/data/database.db"

# User Log In
def validate_user(email, password):
    connect = sqlite3.connect(database_link)
    cursor = connect.cursor()

    result = cursor.execute('SELECT * FROM userbase WHERE email = ? AND password = ?', (email, password))
    information = {
        "username": ""
    }
    
    for item in result:
        information = {
            "username": item[0],
            "email": item[1],
            "password": item[2]
        }

    connect.close()
    return information['username']


# User Sign Up
def sign_up_user(username, email, password):
    connect = sqlite3.connect(database_link)
    cursor = connect.cursor()

    cursor.execute('INSERT INTO userbase(username, email, password) VALUES (?, ?, ?)', (username, email, password))

    connect.commit()
    connect.close()