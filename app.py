from flask import Flask, jsonify, make_response, request, send_file
from flask_pymongo import PyMongo
from werkzeug.exceptions import Unauthorized
from store import utils
from base64 import b64decode
import serverless_wsgi, json, os, gridfs
from bson.objectid import ObjectId

app = Flask(__name__)

try:
    mongo_image = PyMongo(app, os.environ.get("MONGO_IMAGES"))
    mongo_text = PyMongo(app, os.environ.get("MONGO_TEXTS"))
    
    fs_image= gridfs.GridFS(mongo_image.db)
    fs_text= gridfs.GridFS(mongo_text.db)

except Exception as err:
    print (f' error while connecting to mongodb: {err}')

@app.route("/")
def homePage():
    print('/home endpoint')
    return 'Wellcome to home page!', 200


@app.route("/uploadTest",methods = ["POST"])
def uploadTest():
    print('/uploadTest endpoint')
    print(f'keys environ en upload  route: {request.environ.keys()}')
    contexObj = request.environ.get('serverless.event')
    # print(f"-- CONTEXT dir: {dir(contexObj)}")
    # print(f"-- CONTEXT vars: {vars(contexObj)}")
    print(f"-- EVENT vars: {contexObj}")
    contexObj = request.environ.get('serverless.authorizer')
    print(f"-- AUTHORIZER vars: {contexObj}")
    

    return "testing upload :D", 200

@app.route("/upload", methods=["POST"])
def upload():
    print('/upload endpoint')
    access = request.environ.get('serverless.authorizer')

    if access["admin"]:
        sls_event = request.environ.get('serverless.event')
        print(f'conten of event: {sls_event}')

        # upload image to mongo and insert message in SQS queue
        print(f'content of context: {request.environ.get("serverless.context")}')

        if sls_event['body'] == None:
            print(f'body is empty. User: {access["username"]}')
            return 'Not acceptable, file was not selected. You have to select a valid file.', 406
        
        file = b64decode(sls_event['body'])
        err = utils.upload(file,fs_image,access, 'ocr_text_converter')
        print(f'uploaded by user :{access["username"]}')
        if err:
            print(f'Error while uploading file. \n  Error:{err}')
            return 'error uploading image. Please try again', 503
        return "Successful upload!", 200
    
    return "Not authorized", 401

@app.route("/download", methods=["GET"])
def download():
    print('/download endpoint')

    access = request.environ.get('serverless.authorizer')
    print(f'content of event: {request.environ.get("serverless.event")}')
    try:
        fid_string_parameter = request.environ.get('serverless.event')['queryStringParameters']
        print(f'fid_str_type {type(fid_string_parameter)}')
    except Exception as err:
        print(f'error getting string paramenters: {err}')
        return 'string parameter missing', 400
    
    if access["admin"]:
        if not fid_string_parameter or not fid_string_parameter['text_fid']:
            print('fid paramenter is missing')
            return 'fid paramenter is missing', 400
        
        try:
            out_text_file = fs_text.get(ObjectId(fid_string_parameter['text_fid']))
            return send_file(out_text_file,download_name=f'{fid_string_parameter["text_fid"]}.txt')
        except Exception as err:
            print(err)
            return "Internal server error", 500
        
    return 'Not authorized', 401

@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify(error='Not found!'), error.code)

@app.errorhandler(501)
def resource_not_found(error):
    return make_response(jsonify(error='An error occurred while uploading queue message. Please try again.'), error.code)

@app.errorhandler(Unauthorized)
def unauthorized(error):
    response = jsonify(error='Unathorized user. Please login again')
    response.code_code = error.code
    return make_response(response, 401)

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)