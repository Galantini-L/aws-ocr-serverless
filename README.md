# Python Flask API OCR service backend AWS Serverless Framework

This template demostrate how make a OCR API service with Python using Flask running on AWS Lambda containers images, API Gateway and AWS SQS. 
For storage images and texts use MongoDB with Gridfs and for users storage MySql.

This is a microservices-based API which includes a login service, authorizer token, upload and download service and the ocr-converter service.
The login service provides you a JWT token that will be validated every time you use the other services.

The coverter service (or consumer) is trigger by a SQS queue and it use Tesseract OCR.



## Lambda Layer

The converter service is the only one that is not working on a container image. Using images for lambda functions consumes to much space but solves the problem of dependencies needed by the code (in this case tesseract). I tried to create the converter service without containers by installing the necessary dependencies in lambda layers and, after many headaches, I was finally able to get it working.

I followed bweigel's [tutorial](https://github.com/bweigel/aws-lambda-tesseract-layer) to create the layer, additionally, I installed some python dependencies inside the layer to avoid dependencies problems.

## Contacts
* [Linkedin](https://www.linkedin.com/in/lautaro-galantini-a97125212/)
* galantini99@gmail.com