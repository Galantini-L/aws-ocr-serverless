import boto3, os
from json import loads, dumps
from converter.toText_convert.converter_OCR import image_to_text
from converter.adapters.mongo_db_adapter import FSMongoDBAdapter

try:
    fsClient = FSMongoDBAdapter()
    print('fsClient created')
except Exception as err:
    print(f'Error trying to create fs instance: {err}')

def consumer(event, context):

    success_return = {
            'statusCode':200,
            'body': 'Processed messages from SQS queue'
        }
    
    error_return = {
                'statusCode':500,
                'body': 'Error processing messages from SQS queue'
            }


    for record in event['Records']:
        #convert ocr
        try:
            print('content of body records:')
            print(str(record['body']))
            message_body = loads(record['body'])
            if message_body['invoked_service'] == 'ocr_text_converter':
                img = fsClient.get_image(message_body["image_fid"])
                user = message_body["username"].partition('@')[0]
                text_result = image_to_text(img, user)
        except Exception as err:
            print(f'error coverting image to text: {err}')
            return error_return
        
        #upload to mongo
        try:
            text_fid = fsClient.upload_text(text_result)
            print(f'uploaded text {text_fid} to mongo')

        except Exception as err:
            print(f'error uploading to mongo: {err}')
            return error_return

        #upload message to SQS queue
        try:
            message_body['text_fid'] = str(text_fid)
            message_attribute = {}
            sqsClient =  boto3.resource("sqs")
            queue = sqsClient.get_queue_by_name(QueueName = os.environ.get('SQS_QUEUE_NAME'))
            response = queue.send_message(
                MessageBody = dumps(message_body),
                MessageAttributes = message_attribute
            )
            print(f"--> Message sent to SQS queue: {response.get('MessageId')}")

        except Exception as err:
            print(f'error inserting message into queue: {err}')
            fsClient.delete_text(text_fid)
            print(f'text file was deleted. fid:{text_fid}')
            return error_return

        return success_return