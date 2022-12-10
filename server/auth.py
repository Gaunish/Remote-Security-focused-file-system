import sqlite3
import bcrypt
import random
import hmac, hashlib

class User:

    # connect to database
    def __init__(self):
        self.username = ""
        self.dbname = "user.db"
        self.connection = sqlite3.connect(self.dbname)
        self.cursor = self.connection.cursor()

    # Register user, password to db
    def DBregister(self, name, password):
        try:
            # generate salt, encrypt password with it
            count = random.randint(5, 15)
            salt = bcrypt.gensalt(rounds=count)
            passwd = bcrypt.hashpw(str(password).encode('utf-8'), salt)
            # execute query
            query = "insert into user(username, password, salt) values('" + name + "','" + passwd.decode() + "','" + salt.decode() +"')"
            self.cursor.execute(query)
            self.connection.commit()

        except sqlite3.Error as error:
            print('Error:', error)
            return False
        # indicates user has logged in
        self.username = name 
        return True
    
    # Method to retrieve salt for username
    def getSalt(self, name):
        try:
            query = "select * from user where username = '" + name + "';"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            # Username is invalid
            if len(result) != 1:
                return None
                
            return result[0][3]

        except sqlite3.Error as error:
            print('Error: ', error)
        return None

    # Method to login, given username, HMAC password, combined Nonce
    def DBlogin(self, name, password, nonce):
        try:
            # retrieve user info based on username
            query = "select * from user where username = '" + name + "';"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            # invalid username
            if len(result) != 1:
                return False

            # Generate HMAC from details
            h = hmac.new(nonce.encode('utf-8'), result[0][2].encode('utf-8'), hashlib.sha256)
            passwd = h.hexdigest()

            # Check if password is correct
            if password == passwd:
                # indicates user has logged in
                self.username = name
                return True
        
        except sqlite3.Error as error:
            print('Error: ', error)
        
        return False
    
    # Return username, if user is logged in
    # else empty string
    def getUser(self):
        return self.username

    def __del__(self):
        try:
            self.cursor.close()
            self.connection.close()
        except sqlite3.Error as error:
            print('Error: ', error)

#----Tester Code----
#user = User()
#out = user.login("test", 123e4)
#print(out)