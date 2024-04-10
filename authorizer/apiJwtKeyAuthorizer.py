import jwt, os, uuid

def handler(event, context):
    print(f"--> content of event: START {event} END")
    authResponse = { 
        "principalId": uuid.uuid4().hex,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke", 
                    "Resource": event['methodArn'],
                    "Effect": "deny"
                }
            ]
        }
    }
    try:
        authEncodedJWT = event.get('authorizationToken').split()
        authEncType = authEncodedJWT[0]
        authEncToken = authEncodedJWT[1]
        print(f"authencodedjwt: {authEncodedJWT}")

        if authEncType == "Bearer":
            decoded_JWT = jwt.decode(
                authEncToken,
                os.environ.get("JWT_SECRET"),
                algorithms=["HS256"]
            )
            authResponse["policyDocument"]["Statement"][0]["Effect"] = "allow"
            authResponse["context"]= decoded_JWT
            print(f"--> decoded JWT: {decoded_JWT}")
            print(f"authResponse: {authResponse}")
            return authResponse
        return authResponse
    
    except Exception as e:
        print (f"--> Error on JWT decode: {e}")
        if type(e) == jwt.ExpiredSignatureError:
            print("expired token")
            return authResponse
        return authResponse