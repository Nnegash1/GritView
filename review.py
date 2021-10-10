import psycopg2
import time
from psycopg2.extras import RealDictCursor
from views import connect_db, DATABASE_NAME

#Test Value
#http://127.0.0.1:5000/review?title=This is the title &body=postman test&rating=5&expected_grade=A&course_id=1111&professor_id=1111&user_id=2
def create_review(title, body, rating, expected_grade, professor_id, course_id, user_id):
    second = time.time()
    timestamp =  time.ctime(second)
    try:
        if not user_id or not professor_id or not course_id:
            return {'message': 'Specify all required parameters.'}

        if not title or not body or not rating or not timestamp:
            return {'message': 'Specify all required parameters.'}

        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        add_review = "INSERT INTO \"Review\" (title, body, rating, expected_grade, course_id, user_id, professor_id, timestamp) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);"
        cursor.execute(add_review, (title, body, rating, expected_grade, course_id, user_id, professor_id, timestamp))
        connection.commit()
        return {'message': 'Successfully posted'}

    except (Exception, psycopg2.Error) as error:
        print(error)
        return{'message': 'Something went wrong'}


def update_review(title, body, rating, expected_grade, review_id, user_id):
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        if not review_id or not user_id:
            return {'message': 'Specify all required parameters.'}

        update_review = "UPDATE \"Review\" SET title=%s, body=%s, rating=%s, expected_grade=%s WHERE id=%s AND user_id=%s;"
        cursor.execute(update_review, (title, body, rating, expected_grade, review_id, user_id))
        connection.commit()
        return {"message": "Successfully Updated"}

    except (Exception, psycopg2.Error) as error:
        print(error)
        return{"message": "Invalid request"}


def delete_review(review_id, user_id):
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        if not review_id or not user_id:
            return {'message': 'Specify all required parameters.'}

        delete_review = "DELETE FROM \"Review\" WHERE id=%s and user_id=%s;"
        cursor.execute(delete_review, (review_id, user_id))
        connection.commit()
        return {'message': 'Successfully Deleted'}

    except (Exception, psycopg2.Error) as error:
        print(error)
        return{'message': 'Something went wrong'}


def read_review(professor_id, course_id):
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        resp = {}
        if professor_id and course_id:
            read_review = "SELECT * FROM \"Review\" WHERE professor_id=%s AND course_id=%s" % (str(professor_id), str(course_id))
        elif professor_id:
            read_review = "SELECT * FROM \"Review\" WHERE professor_id=%s" % (str(professor_id))
        elif course_id:
            read_review = "SELECT * FROM \"Review\" WHERE course_id='%s'" % (str(course_id))
        else:
            return {'message': 'Something went wrong, please specify all required parameters'}

        cursor.execute(read_review)
        review_resp = cursor.fetchall()
        resp['reviews'] = review_resp
        return resp

    except (Exception, psycopg2.Error) as error:
        print(error)
        return{'message': 'Something went wrong, please check the user_id and try again!!'}

