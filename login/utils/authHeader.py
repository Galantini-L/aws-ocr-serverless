def getAuthHeader(event):
  authorizationHeader = None
  if 'Authorization' in event['headers']:
      authorizationHeader = event['headers']['Authorization']
  if 'authorization' in event['headers']:
      authorizationHeader = event['headers']['authorization']

  return authorizationHeader