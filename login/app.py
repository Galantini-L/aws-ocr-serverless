from flask import Flask, request, jsonify, make_response
import jwt, os, datetime
import serverless_wsgi
import pymysql.cursors
from base64 import b64decode, decode

server = Flask(__name__)

connection = pymysql.connect(host = os.environ.get("MYSQL_HOST"),
                            user = os.environ.get("MYSQL_USER"),
                            password = os.environ.get("MYSQL_PASSWORD"),
                            database = os.environ.get("MYSQL_DB")
                            )

@server.route("/accounts/pylogin", methods = ["POST"])
def pylogin():

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT email, password FROM user WHERE email= %s"
            res = cursor.execute(sql,('galantini@gmail.com'))

    if res > 0:
        result = cursor.fetchone()
        print(f"querry result pylogin {result}")
        email = result[0]
        password = result[1]

    return 'hello world', 200


@server.route("/accounts/login", methods=["POST"])
def login():
    event = request.environ.get('serverless.event')
    authorizationHeader = None
    if 'Authorization' in event['headers']:
        authorizationHeader = event['headers']['Authorization']
    if 'authorization' in event['headers']:
        authorizationHeader = event['headers']['authorization'] 
        
    print(f'content of authorization {authorizationHeader}')

    if not authorizationHeader:
        return "missing credentials", 401

    encodedAuth = authorizationHeader.split()[1]
    encodedAuth = b64decode(encodedAuth).decode('utf-8').split(':')
    dictAuth = {
        'username': encodedAuth[0],
        'password': encodedAuth[1]
    }
    print(f'dictAuth: {dictAuth}')
    try: 
        with connection.cursor() as cursor:
            sql = "SELECT email, password FROM user WHERE email= %s"
            print(f'sql query: {sql}')
            res = cursor.execute(sql,(dictAuth['username']))
            print(f"query response: {res}")
    except Exception as er:
        print(f'error in user query: {er}')
        print(f"error username:{dictAuth['username']}")
        return "Incorrect username or password", 401
        
    if res > 0:
        credentials_row = cursor.fetchone()
        print(f'credentials_row: {credentials_row}')
        email = credentials_row[0]
        password = credentials_row[1]

        if dictAuth['username'] == email and dictAuth['password'] == password:
            try:
                jwtCreated =  createJWT(email,os.environ.get("JWT_SECRET"),True)
                return jsonify(token= jwtCreated), 200
            except Exception as exc:
                print(f'error trying to return token:\n {exc}')
                return "Internal server error", 501
        return "Invalid credentials", 401
    return "Invalid credentials", 401

def createJWT(username, secret, authz):
    return jwt.encode({
        "username":username,
        "exp":datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(days=1),
        #issue at
        "iat":datetime.datetime.now(datetime.timezone.utc),
        "admin":authz
    },secret,algorithm="HS256")


#error handlers
@server.errorhandler(404)
def resource_not_found(e):
    print(f"error 404: {e}")
    return make_response(jsonify(error='Not found'), 404)
@server.errorhandler(500)
def resource_not_found(e):
    print(f"error 500: {e}")
    return make_response(jsonify(error='Internal server error'), 500)

def handler(event, context):
    return serverless_wsgi.handle_request(server, event, context)