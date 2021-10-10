import psycopg2

from psycopg2.extras import RealDictCursor
from model import _query_reviews, _query_professor, _query_course, _query_subject, _query_grades, _query_evaluations, \
    _query_evaluation_score, _query_professors_by_subject, _query_subject_by_id
from utils import split_alphanumeric

DATABASE_NAME = 'UMBC_S20'

# Connects to a database and returns connection
# pre-condition: name of database
# resource: https://stackabuse.com/working-with-postgresql-in-python/
def connect_db(database_name):
    connection = psycopg2.connect(database=database_name, user="postgres", password="", host="127.0.0.1", port="5432")
    return connection


# returns all professors details that teach the course, and all of the grades and (subject & courses) available by semester/sections.
# PreConditions: req: course_name | optional: semester
# example request: http://127.0.0.1:5000/course?course=ENGL100
def get_course(course_name, semester=None):
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        resp = {}

        # Parses course_name to (name, catalog_number)
        name_catalog_num = split_alphanumeric(course_name)
        if name_catalog_num is None:
            return None
        name, catalog_number = name_catalog_num

        # Queries Subject
        subject_resp = _query_subject(cursor, name, catalog_number)
        if subject_resp == None:
            resp["subject"] = resp["courses"] = resp["professors"] = resp["grades"] = []
            return resp
        resp['subject'] = subject_resp

        # Queries Courses
        subject_id = subject_resp['id']
        course_resp = _query_course(cursor, subject_id, None, None, semester)
        if course_resp is None or course_resp == []:
            resp["courses"] = resp["professors"] = resp["grades"] = []
            return resp
        resp["courses"] = course_resp

        # Queries Professors
        professor_resp = _query_professors_by_subject(cursor, subject_id, semester)
        if professor_resp is None:
            resp["professors"] = resp["grades"] = []
            return resp
        # Removes duplicate professors
        unique_professors = []
        visited = set()
        for professor in professor_resp:
            if not professor['id'] in visited:
                visited.add(professor['id'])
                unique_professors.append(professor)
        resp["professors"] = unique_professors

        # Queries grades
        grades = []
        for course in course_resp:
            course_id = course["id"]
            grade_resp = _query_grades(cursor, None, course_id)
            if grade_resp is not None:
                grades.append(grade_resp)
        resp["grades"] = grades

        return resp

    except (Exception, psycopg2.Error) as error:
        print(error)
        return {'message': 'Error querying results for %s' % (course_name)}

    finally:
        if connection:
            cursor.close()
            connection.close()



# returns professor details, reviews, and all of the (subjects & courses) available by sections.
# PreConditions: req: professor_name | optional: none
# example request: http://127.0.0.1:5000/professor?professor=Shane Moritz
def get_professor(professor_name, section, semester):
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        resp = {}

        # Queries professor
        professor_resp = _query_professor(cursor, professor_name)
        if professor_resp is None:
            return {"message": "No results found for %s." % (professor_name)}
        resp["professor"] = professor_resp

        # Queries reviews
        professor_id = professor_resp["id"]
        review_resp = _query_reviews(cursor, professor_id)
        if review_resp is None:
            resp["reviews"] = []
        resp["reviews"] = review_resp

        # Queries courses
        course_resp = _query_course(cursor, None, professor_id, None, None)
        if course_resp is None or course_resp == []:
            esp["courses"] = resp['subjects'] = resp['evaluations'] = []
            return resp
        resp['courses'] = course_resp

        # Queries all unique subjects
        subjects = []
        subject_ids = set([course['subject_id'] for course in course_resp])
        for subject_id in subject_ids:
            subjects.append(_query_subject_by_id(cursor, subject_id))
        resp['subjects'] = subjects

        # Queries evaluations
        evaluation_resp = _query_evaluations(cursor, professor_id, None)
        for index, evaluation in enumerate(evaluation_resp):
            for column in evaluation:
                if column[0] == 'Q':
                    evaluation_resp[index][column] = _query_evaluation_score(cursor, evaluation[column])
        resp['evaluations'] = evaluation_resp

        return resp
 
    except (Exception, psycopg2.Error) as error:
        print(error)
        return {'message': 'Error querying results for %s' % (professor_name)}

    finally:
        if connection:
            cursor.close()
            connection.close()


# returns professor details, reviews, evaluations, and all of the grades and (subject & courses) available by sections.
# PreConditions: req: professor_name, course_name | optional: semester, section
# example request: http://127.0.0.1:5000/professor?professor=Shane Moritz&course=ENGL100
def get_professor_course(professor_name, course_name, semester=None, section=None):
    try:
        connection = connect_db(DATABASE_NAME)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        resp = {}

        # Queries professor details
        professor_resp = _query_professor(cursor, professor_name)
        if professor_resp is None:
            return {"message": "No results found for %s." % (professor_name)}
        resp["professor"] = professor_resp

        # Queries all reviews given to the professor
        professor_id = professor_resp["id"]
        review_resp = _query_reviews(cursor, professor_id)
        if review_resp is None:
            resp["reviews"] = []
        resp["reviews"] = review_resp

        # Parses course_name to name and catalog_number
        # ENGL100 -> ('ENGL', '100')
        name_catalog_num = split_alphanumeric(course_name)
        if name_catalog_num is None:
            resp["subject"] = resp["courses"] = resp["grades"] = resp["evaluations"] = []
            return resp
        name, catalog_number = name_catalog_num

        # Queries Subject
        subject_resp = _query_subject(cursor, name, catalog_number)
        if subject_resp == None:
            resp["subject"] = resp["courses"] = resp["grades"] = resp["evaluations"] = []
            return resp
        resp['subject'] = subject_resp

        # Queries Courses
        subject_id = subject_resp['id']
        course_resp = _query_course(cursor, subject_id, professor_id, section, semester)
        if course_resp is None or course_resp == []:
            resp["courses"] = resp["grades"] = resp["evaluations"] = []
            return resp
        resp["courses"] = course_resp

        # Queries grades and evaluations
        grades = []
        evaluations = []
        for course in course_resp:
            course_id = course["id"]
            grade_resp = _query_grades(cursor, professor_id, course_id)
            evaluation_resp = _query_evaluations(cursor, professor_id, course_id)
            if grade_resp is not None:
                grades.append(grade_resp)
            if evaluation_resp is not None:
                # Queries evaluation score for questions 1-32
                for column in evaluation_resp:
                    if column[0] == 'Q':
                        evaluation_resp[column] = _query_evaluation_score(cursor, evaluation_resp[column])
                evaluations.append(evaluation_resp)
        resp["grades"] = grades
        resp["evaluations"] = evaluations

        return resp

    except (Exception, psycopg2.Error) as error:
        print(error)
        return {'message': 'Error querying results for %s and %s' % (professor_name, course_name)}

    finally:
        if connection:
            cursor.close()
            connection.close()
