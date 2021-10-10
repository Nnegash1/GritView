import psycopg2

# Queries all reviews of a professor given a professor_id
def _query_reviews(cursor, professor_id):
    try:
        review_query = "SELECT * FROM \"Review\" WHERE professor_id=%s" % (str(professor_id))
        cursor.execute(review_query)
        return cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries a professor given the professor_name
def _query_professor(cursor, professor_name):
    try:
        professor_name_parsed = tuple(professor_name.split())
        if len(professor_name_parsed) == 3:
            first_name, middle_name, last_name = professor_name_parsed
            professor_query = "SELECT * FROM \"Instructor\" WHERE first_name='%s' AND middle_name='%s' AND last_name='%s'" % (first_name, middle_name, last_name)
        elif len(professor_name_parsed) == 2:
            first_name, last_name = professor_name_parsed
            professor_query = "SELECT * FROM \"Instructor\" WHERE first_name='%s' AND last_name='%s'" % (first_name, last_name)
        elif len(professor_name_parsed) == 1:
            first_name = professor_name_parsed
            professor_query = "SELECT * FROM \"Instructor\" WHERE first_name='%s'" % (first_name)
        else:
            return None

        cursor.execute(professor_query)
        return cursor.fetchone()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries a professor given the professor_name
def _query_professors_by_subject(cursor, subject_id, semester):
    try:
        if subject_id:
            if semester:
                professor_query = "SELECT professor_id FROM \"Course\" WHERE subject_id=%s AND semester='%s'" % (str(subject_id), semester)
            else:
                professor_query = "SELECT professor_id FROM \"Course\" WHERE subject_id=%s" % (subject_id)
        else:
            return None

        cursor.execute(professor_query)
        professors = cursor.fetchall()
        professors_list = []
        for professor in professors:
            professor_id = professor['professor_id']
            professor_query = "SELECT * FROM \"Instructor\" WHERE id=%s" % (str(professor_id))
            cursor.execute(professor_query)
            professor_res = cursor.fetchone()
            professors_list.append(professor_res)
        return professors_list

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries courses
def _query_course(cursor, subject_id, professor_id, section, semester):
    try:
        # Queries by professor_id
        if subject_id is None and professor_id:
            if semester and section:
                course_query = "SELECT * FROM \"Course\" WHERE professor_id=%s AND section='%s' AND semester='%s' " % (str(professor_id), section, semester)
            elif semester:
                course_query = "SELECT * FROM \"Course\" WHERE professor_id=%s AND semester='%s'" % (str(professor_id), semester)
            elif section:
                course_query = "SELECT * FROM \"Course\" WHERE professor_id=%s AND section='%s'" % (str(professor_id), section)
            else:
                course_query = "SELECT * FROM \"Course\" WHERE professor_id=%s" % (str(professor_id))

        # Queries by subject_id and/or semester only
        elif professor_id is None:
            if semester is None:
                course_query = "SELECT * FROM \"Course\" WHERE subject_id=%s" % (str(subject_id))
            else:
                course_query = "SELECT * FROM \"Course\" WHERE subject_id=%s AND semester='%s'" % (str(subject_id), semester)

        # Queries by professor_id, subject_id, section and semester
        else:
            if section is not None and semester is not None:
                course_query = "SELECT * FROM \"Course\" WHERE subject_id='%s' AND section='%s' AND semester='%s' AND professor_id=%s" % (subject_id, str(section), semester, str(professor_id))
            elif section is not None:
                course_query = "SELECT * FROM \"Course\" WHERE subject_id='%s' AND section='%s' AND professor_id=%s" % (subject_id, str(section), str(professor_id))
            elif semester is not None:
                course_query = "SELECT * FROM \"Course\" WHERE subject_id='%s' AND semester='%s' AND professor_id=%s" % (subject_id, semester, str(professor_id))
            else:
                course_query = "SELECT * FROM \"Course\" WHERE subject_id='%s' AND professor_id=%s" % (subject_id, str(professor_id))

        cursor.execute(course_query)
        return cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries subject by subject_id
def _query_subject_by_id(cursor, subject_id):
    try:
        subject_query = "SELECT * FROM \"Subject\" WHERE id=%s" % (str(subject_id))
        cursor.execute(subject_query)
        return cursor.fetchone()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries subject by name and catalog_number
def _query_subject(cursor, name, catalog_number):
    try:
        subject_query = "SELECT * FROM \"Subject\" WHERE name='%s' AND catalog_number='%s'" % (name, str(catalog_number))
        cursor.execute(subject_query)
        return cursor.fetchone()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries grades
def _query_grades(cursor, professor_id, course_id):
    try:
        if professor_id and course_id:
            grade_query = "SELECT * FROM \"Grade\" WHERE professor_id=%s AND course_id=%s" % (str(professor_id), str(course_id))
        elif professor_id:
            grade_query = "SELECT * FROM \"Grade\" WHERE professor_id=%s" % (str(professor_id))
        elif course_id:
            grade_query = "SELECT * FROM \"Grade\" WHERE course_id=%s" % (str(course_id))
        else:
            return None

        cursor.execute(grade_query)
        return cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries evaluations by professor_id or professor_id and course_id
def _query_evaluations(cursor, professor_id, course_id):
    try:
        if professor_id and course_id:
            evaluation_query = "SELECT * FROM \"Evaluation\" WHERE professor_id=%s AND course_id=%s" % (str(professor_id), str(course_id))
            cursor.execute(evaluation_query)
            return cursor.fetchone()
        elif professor_id:
            evaluation_query = "SELECT * FROM \"Evaluation\" WHERE professor_id=%s" % (str(professor_id))
        elif course_id:
            evaluation_query = "SELECT * FROM \"Evaluation\" WHERE course_id=%s" % (str(course_id))
        else:
            return None

        cursor.execute(evaluation_query)
        return cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None


# Queries evaluation score
def _query_evaluation_score(cursor, evaluation_score_id):
    try:
        if evaluation_score_id:
            evaluation_score_query = "SELECT * FROM \"EvaluationScore\" WHERE id=%s" % (str(evaluation_score_id))
        else:
            return None

        cursor.execute(evaluation_score_query)
        return cursor.fetchone()

    except (Exception, psycopg2.Error) as error:
        print(error)
        return None
