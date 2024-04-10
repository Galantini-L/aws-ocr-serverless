import json
import boto3
import os
from botocore.exceptions import ClientError
from base64 import b64decode

def upload(file, fs, access, service):
    """ 
        Upload the given file to mongodb using the given gridFS instance. 
        After uploading to mongo, inserts a messagge to SQS queue.

        Arguments:
            file {_type_} -- file to be updated\n
            fs {_type_} -- gridFS Instance\n
            access {obj} -- user access information
    """

    try:
        print(f'file in upload : {file}')
        fid = fs.put((file))
        print(f'uploaded image {fid} to mongo')
    except Exception as e:
        print(e)
        return "Internal server error", 501
    
    message = {
        "image_fid":str(fid),
        "text_fid":None,
        "username":access["username"],
        "invoked_service": service
    }

    message_attribute = {}

    try:
        sqsClient =  boto3.resource("sqs")
        queue = sqsClient.get_queue_by_name(QueueName = os.environ.get('SQS_QUEUE_NAME'))
        response = queue.send_message(
            MessageBody = json.dumps(message),
            MessageAttributes = message_attribute
        )
        print(f"--> Message sent to SQS queue: {response.get('MessageId')}")

        #uploadRegister(message['image_fid'], response.get('MessageId'))
    except ClientError as err:
        fs.delete(fid)
        return err