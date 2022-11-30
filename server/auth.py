import sqlite3
import bcrypt
import random

class User:

    def __init__(self):
        self.username = ""
        self.dbname = "user.db"
        self.connection = sqlite3.connect(self.dbname)
        self.cursor = self.connection.cursor()

    def register(self, name, password):
        try:
            count = random.randint(5, 15)
            salt = bcrypt.gensalt(rounds=count)
            passwd = bcrypt.hashpw(str(password).encode('utf-8'), salt)
            query = "insert into user(username, password, salt) values('" + name + "','" + passwd.decode() + "','" + salt.decode() +"')"
            print(query)
            self.cursor.execute(query)
            self.connection.commit()

        except sqlite3.Error as error:
            print('Error:', error)
            return False

        self.username = name 
        return True

    def login(self, name, password):
        try:
            query = "select * from user where username = '" + name + "';"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if len(result) != 1:
                return False

            passwd = bcrypt.hashpw(str(password).encode('utf-8'), result[0][3].encode('utf-8'))
            if result[0][2] == passwd.decode():
                self.username = name
                return True
        
        except sqlite3.Error as error:
            print('Error: ', error)
        
        return False
    
    def getUser(self):
        return self.username

    def __del__(self):
        try:
            self.cursor.close()
            self.connection.close()
        except sqlite3.Error as error:
            print('Error: ', error)

#user = User()
#out = user.login("test", 123e4)
#print(out)