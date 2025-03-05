from patternFinder import getImageFromWebsite, searchFabrics
import os
import boto3
from dotenv import load_dotenv
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from databaseQueries import fabricQuery, patternQuery, joinQuery, createMutationInput, createJoinInput, findFabric, createFilterInput


load_dotenv()
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_APPSYNC_ENDPOINT = os.getenv("APPSYNC_ENDPOINT")
AWS_COGNITO_USER_POOL_ID = os.getenv("AWS_COGNITO_USER_POOL_ID")
AWS_COGNITO_CLIENT_ID = os.getenv("AWS_COGNITO_CLIENT_ID")


USERNAME = os.getenv("LOCAL_USERNAME")
PASSWORD = os.getenv("LOCAL_PASSWORD")

cognito_client = boto3.client(
    "cognito-idp",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def authenticate_user(username, password):
    try:
        response = cognito_client.initiate_auth(
            ClientId=AWS_COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        return response["AuthenticationResult"]["AccessToken"]
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

transport = RequestsHTTPTransport(
    url=AWS_APPSYNC_ENDPOINT,
    use_json=True,
    headers={},
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

def createAccessToken(username, password):
    access_token = authenticate_user(username, password)
    if access_token:
        return access_token
    else:
        print("Authentication required to run the query.")

def queryDatabase(access_token, query, input):
    if access_token:
        transport.headers = {"Authorization": access_token}
        try:
            return client.execute(query,variable_values=input)
        except Exception as e:
            print(f"Query execution failed: {e}")

access_token = createAccessToken(USERNAME,PASSWORD)

def parseFabrics(fabrics, patternNumber):
  uniqueFabrics = list(set(fabrics))
  patternResult = queryDatabase(access_token,patternQuery,createMutationInput(name=patternNumber))

  
  for fabric in uniqueFabrics:
    fabricResult = queryDatabase(access_token, findFabric,createFilterInput(fabric))

    if len(fabricResult["listWebFabricItems"]["items"]) == 0: 
      fabricResult = queryDatabase(access_token, fabricQuery,createMutationInput(name=fabric))
      fabricId = fabricResult["createWebFabricItems"]["id"]
    else:
       fabricId = fabricResult["listWebFabricItems"]["items"][0]["id"]
       
    joinResult = queryDatabase(access_token,joinQuery,createJoinInput(fabricId=fabricId,patternId=patternResult["createWebPatternItems"]["id"]))
    print(joinResult)


def getResultsByBrand(brandUrl, firstPatternNumber, lastPatternNumber):
  count = 0
  patternNumber = firstPatternNumber
  
  while (count < 1):
    url = brandUrl + str(patternNumber)
    didGetImage = getImageFromWebsite(url,  "cropped.png")
    print(url)
    if (didGetImage):
      count +=1
      getImageFromWebsite(url,  "cropped.png")
      listFabrics, _ = searchFabrics("cropped.png")
      brand = "s" + str(patternNumber)
      parseFabrics(listFabrics,brand)
    patternNumber += 1


print("Simplicity")
url = "https://simplicity.com/simplicity/s"

getResultsByBrand(url,1021,9977)