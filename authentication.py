import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
from views import connect_db, DATABASE_NAME


# resource: https://pythonise.com/categories/python/python-password-hashing-bcrypt
# Registers a user in the database if requirements are met
#Test: http://127.0.0.1:5000/signup?username=user105&password=password2
def handle_user_registration(username, password, email):
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12)).decode('utf-8')
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        username_query = "SELECT * FROM \"User\" WHERE username='%s'" % (username)
        cursor.execute(username_query)
        username_resp = cursor.fetchone()

        email_resp = None
        if email is not None:
            email_query = "SELECT * FROM \"User\" WHERE email='%s'" % (email)
            cursor.execute(email_query)
            email_resp = cursor.fetchone()

        if username_resp is not None or email_resp is not None:
            return {'message': 'The username or email is already in use. Please try again with a different username or email.'}

        add_user = "INSERT INTO \"User\" (username, email, password) VALUES(%s, %s, %s);"
        cursor.execute(add_user, (username, email, hashed_password))
        connection.commit()
        return {'message': 'Successfully created user.'}

    except (Exception, psycopg2.Error) as error:
        print(error)
        return {'message': 'Error creating a user. Please try again!'}

    finally:
        if connection:
            cursor.close()
            connection.close()


# Authenticates a user
#test : http://127.0.0.1:5000/signup?username=user103&password=password&email=email_3
def handle_user_login(username, password):
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        user_password_query = "SELECT password FROM \"User\" WHERE username='%s'" % (username)
        cursor.execute(user_password_query)
        user_resp = cursor.fetchone()

        if(user_resp is None):
            return {'message': 'User account does not exist'}

        hashed_password = user_resp['password'].encode("utf-8")

        if bcrypt.checkpw(password, hashed_password):
            return {'message': 'Successfully logged in.'}
        else:
            return {'message': 'Please Check your password and username again!!'}

    except (Exception, psycopg2.Error) as error:
        print(error)
        return {'message': 'Error authenticating the user. Please try again!'}

    finally:
        if connection:
            cursor.close()
            connection.close()
