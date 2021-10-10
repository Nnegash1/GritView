from flask import Flask, request, Response
import json
from review import create_review, update_review, read_review, delete_review
from views import get_professor_course, get_professor, get_course
from authentication import handle_user_registration, handle_user_login

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

# example request: http://127.0.0.1:5000/course?course=CMSC202
# example request: http://127.0.0.1:5000/professor?professor=Jeremy Dixon&course=CMSC202&semester=Spring 2019
@app.route('/professor')
def professor():
    professor_name = request.args.get('professor', None)
    course_name = request.args.get('course', None)
    semester = request.args.get('semester', None)
    section = request.args.get('section', None)

    if professor_name == None:
        msg = {"message": "Invalid request: specify all required parameters."}
        return Response(json.dumps(msg), mimetype='application/json')
    elif course_name != None :
        response = get_professor_course(professor_name, course_name, semester, section)
        return Response(json.dumps(response), mimetype='application/json')
    else:
        response = get_professor(professor_name, section, semester)
        return Response(json.dumps(response), mimetype='application/json')


# example request: http://127.0.0.1:5000/course?course=CMSC202
@app.route('/course')
def course():
    course_name = request.args.get('course', None)
    semester = request.args.get('semester', None)
    response = get_course(course_name, semester)
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/login')
def login():
    username = request.args.get('username', None)
    password = request.args.get('password', None)

    if not username or not password:
        msg = {"message": "Invalid request: specify all required parameters."}
        return Response(json.dumps(msg), mimetype='application/json')

    response = handle_user_login(username.lower(), password.encode("utf-8"))
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/signup')
def signup():
    username = request.args.get('username', None)
    password = request.args.get('password', None)
    email = request.args.get('email', None)

    if not username or not password: #
        msg = {"message": "Invalid request: specify all required parameters."}
        return Response(json.dumps(msg), mimetype='application/json')

    response = handle_user_registration(username.lower(), password.encode("utf-8"), email)
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/review',  methods=['GET', 'POST', 'PATCH', 'DELETE'])
def review():
    CREATE = "POST"
    READ = "GET"
    UPDATE = "PATCH"
    DELETE = "DELETE"

    user_id = request.args.get('user_id', None)
    professor_id = request.args.get('professor_id', None)
    course_id = request.args.get('course_id', None)
    review_id = request.args.get('review_id', None)
    expected_grade = request.args.get('expected_grade', None)

    if request.method == CREATE or request.method == UPDATE:
        title = request.args.get('title', None)
        body = request.args.get('body', None)
        rating = request.args.get('rating', None)
        expected_grade = request.args.get('expected_grade', None)
        if request.method == CREATE:
            response = create_review(title, body, rating, expected_grade, professor_id, course_id, user_id)
            return Response(json.dumps(response), mimetype='application/json')
        else:
            response = update_review(title, body, rating, expected_grade, review_id, user_id)
            return Response(json.dumps(response), mimetype='application/json')
    elif request.method == READ:
        response = read_review(professor_id, course_id)
        return Response(json.dumps(response), mimetype='application/json')
    elif request.method == DELETE:
        response = delete_review(review_id, user_id)
        return Response(json.dumps(response), mimetype='application/json')
    else:
        msg = {"message": "Invalid method"}
        return Response(json.dumps(msg), mimetype='application/json')


@app.route('/')
def landing():
    return 'Welcome to Gritview.io'



if __name__ == '__main__':
    FLASK_DEBUG = True
    app.run()
