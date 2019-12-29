
# *** THIS CODE IS FOR DEMO PURPOSES ONLY ***

# Azure Text Analytics API v3 demo
# https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/overview

# Import Python packages
# pyodbc requires MS SQL Server driver pre-installed on the machine. This can be downloaded from Microsoft website.
import os 
import requests
import simplejson as json
import io
import datetime
import pyodbc
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants
import shutil

def dtStr():
    x=datetime.datetime.now()
    dtTime=x.strftime("%Y")+"-"+x.strftime("%m")+"-"+x.strftime("%d")+" "+x.strftime("%H")+":"+x.strftime("%M")+":"+x.strftime("%S")
    return dtTime

def batchStr():
    # create a unique batchid to tag/identify individual run
    x = datetime.datetime.now()
    batchId = x.strftime("%Y%m%d%H%M%S%f")
    return batchId

# Function to write metadata to Azure SQL DB
def writeMetadataToSQLdb(dbServerName,dbName,dbUser,dbPass,status):
    dbServerName = dbServerName
    dbName = dbName
    dbUser = dbUser
    dbPass = dbPass
    driver= 'ODBC Driver 17 for SQL Server'
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+dbServerName+';PORT=1433;DATABASE='+dbName+';UID='+dbUser+';PWD='+dbPass)
    # Statement to execute against the database
    # Insert job status in Azure SQL DB when file processing starts
    # writing to azure sqldb
    stDtTime=dtStr()
    insertStr="insert into dbo.joblogs values ('"+batchId+"','"+fullFileName+"','"+status+"','"+stDtTime+"')"
    cursor = cnxn.cursor()
    cursor.execute(insertStr)
    cnxn.commit()
    print("Record inserted into Azure SQL DB")

# Function to write to Cosmos DB
def writePiiToCosmos(url,key,databaseId,collectionId,entities):
    url=url
    key=key
    database_id = databaseId
    collection_id = collectionId
    database_link = 'dbs/' + database_id
    collection_link = database_link + '/colls/' + collection_id
    client=cosmos_client.CosmosClient(url,{'masterKey': key})
    client.CreateItem(collection_link,entities)
    print("Record inserted into Cosmos DB")

# Function that calls Text Analytics API and passes the string which has to be checked for presence of PII
def callTextApi(apiEndpoint,subKey,jsonDoc):
    headers = {"Ocp-Apim-Subscription-Key": subKey}
    response = requests.post(apiEndpoint, headers=headers, json=jsonDoc)
    entities = response.json()
    return entities

# Function to redact PII 
# For purpose of this demo, the function simply does a "find and replace" 
def redact(textToRedact,fullFileName,redactedFileName):
    textToRedact=textToRedact
    sourceFile=fullFileName
    destinationFile=redactedFileName

    # Create a copy of the file 
    print("Creating a copy of "+sourceFile)
    dest = shutil.copyfile(sourceFile, destinationFile)

    # Replace PII text in source file
    targetFile = open(destinationFile,'rt')
    data = targetFile.read()
    
    # Loop through elements of array and replace them 
    for element in range(0,len(textToRedact)):
        data = data.replace(textToRedact[element],'')
    targetFile.close()

    # Open target file
    writeToFinal = open(destinationFile,'wt')
    writeToFinal.write(data)
    writeToFinal.close()

    print("Finished redacting file. Redacted version has been saved to the following location - "+ destinationFile)

# Generate unique job ID to tag each time this code is run
batchId=batchStr()
print("Batch ID assigned to this run: "+batchId)

# set variables for Text analytics API
apiEndpoint = "https://eastus.cognitiveservices.azure.com/text/analytics/v3.0-preview.1/entities/recognition/pii"
subKey = <Azure Text Analytics API key goes here>
language = 'en'
id = 1
apiVersion = 'v3 preview'

# Input directory - this is the directory where all the files that must be scanned by Text Analytics API are stored
inDir = "/temp/test"

# Redacted files - files where PII is detected are written to this output directory
newFilePath="/temp/redacted"

# Azure SQLDB details
# Azure SQL DB is used here to store metadata for each run
dbServerName = <Azure SQL DB server name>
dbName = <SQL DB name>
dbUser = <SQL username>
dbPass = <SQL password>

# Azure Cosmos DB parameters
# If PII is detected, then output of Text Analytics API (which is a JSON document) is written to a Cosmos DB collection
url= <Cosmos DB endpoint>
key= <Cosmos DB key>
databaseId = <Cosmos DB database name>
collectionId = <Cosmos DB container name>

# This loop structure does the following:
# 1. Loop through files in the input directory
# 2. For each file, read all the lines and build a JSON structure that can be parsed by Text Analytics API
# 3. If PII is detected, write output of Text Analytics API to Cosmos endpoint 
for file in os.listdir(inDir):

    # initialise counter
    strObj = " "
    # read contents of the file and store it in a variable
    fullFileName=inDir+"/"+file
    redactedFileName=newFilePath+"/"+file+".redacted"
    readFile = open(inDir+"/"+file,"r", encoding="utf8")
    writeMetadataToSQLdb(dbServerName,dbName,dbUser,dbPass,"Started")


    for line in readFile:
        
        # read lines into a string object 
        strObj = strObj + line

    # Text Analytics API requires input in JSON format with the following keys - ID, Language and Text.
    # This step converts input into a format that can be processed by the API.
    jsonDoc = { "documents": [{"language":language,"id":id,"Text":strObj}]}


    entities=callTextApi(apiEndpoint,subKey,jsonDoc)


    #print(entity.keys())
    #print(json.dumps(entities, separators=(',', ':'), sort_keys=True, indent = 4 * ' '))



    # If PII is detected by the API - write output to Cosmos DB container else ignore the entry
    if len(entities['documents'][0]['entities']) != 0:

        print("PII detected")
        print("Initialize new array for storing PII elements")
        textToRedact=[]

        # entities variable is a dictionary
        # Variable x denotes position of array element inside JSON document
        # The JSON output contains array, and we need to loop through every single array element to capture value of PII type
        for x in range(0,len(entities['documents'][0]['entities'])):                     
                       print(entities['documents'][0]['entities'][x]['text'])
                       textToRedact.append(entities['documents'][0]['entities'][x]['text'])
        
        print("Text to redact")
        print(textToRedact)

        # Redact text
        redactedFile=redact(textToRedact,fullFileName,redactedFileName)

        # Add batch ID, source (input) filename and name of the file with redacted data (output) to the JSON document before it gets written to Cosmos DB
        entities.__setitem__('batchid',batchId)
        entities.__setitem__('input data',fullFileName)
        entities.__setitem__('Text analytics version',apiVersion)
        entities.__setitem__('redactedFile',redactedFileName)

        # Write API output to Cosmos DB collection using SQL API
        print('Writing API results to Cosmos DB')
        
        # Write document to Cosmos DB collection
        writePiiToCosmos(url,key,databaseId,collectionId,entities)
        
        # Insert job status into Azure SQL DB
        writeMetadataToSQLdb(dbServerName,dbName,dbUser,dbPass,"Completed - PII detected")
  
    else:
        print("No PII detected. Writing job entry to Azure SQL DB.")
        writeMetadataToSQLdb(dbServerName,dbName,dbUser,dbPass,"Completed - no PII detected")