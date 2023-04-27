import sqlite3


def adduser(id, nick):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    #add user to waitlist
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (id, nick, 0,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False


def removeuser(id, nick):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    #remove user from waitlist
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (id, nick, 1,))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False


def getusers():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    #get all users from waitlist
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def getuseridvianick(nick):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    #get user id from waitlist
    try:
        cursor.execute("SELECT * FROM users WHERE nick = (?)", (nick,))
        user = cursor.fetchone()
        conn.close()
        return user[0]
    except:
        conn.close()
        return False
    


def removeuseradmin(nick):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE nick = (?)", (nick,))
    conn.commit()
    conn.close()