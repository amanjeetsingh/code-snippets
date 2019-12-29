# **** THIS CODE IS FOR DEMO PURPOSES ONLY ***
# This sample code reads data from Twitter feed and writes it to Azure Event Hubs. Data is then read from Event Hubs and sent to Azure Text Analytics API for PII detection.
# Twitter Feed -> Event Hub -> Text Analytics API v2 (GA)

import tweepy
from azure.eventhub import EventHubClient, Sender, EventData, Receiver, Offset
import simplejson as json
import requests

def callTextApi(apiEndpoint,subKey,jsonDoc):
    headers = {"Ocp-Apim-Subscription-Key": subKey}
    response = requests.post(apiEndpoint, headers=headers, json=jsonDoc)
    entities = response.json()
    return entities

print("************* Starting Demo - Twitter -> Event Hub -> Text Analytics API **************")

# API endpoint for Text Analytics
# For this demo, we are using Text Analytics v21

apiEndpoint="https://eastus.api.cognitive.microsoft.com/text/analytics/v2.1/entities"
subKey = <Key issued by Azure Text Analytics>
language = 'en'
id = 1


# Eventhub variables
address = <event hub address goes here>
user = <user>
key = <key issued by Azure Event Hubs>
client = EventHubClient(address, debug=False, username=user, password=key)
sender = client.add_sender(partition="1")
client.run()

# Twitter variables
consumer_key = <insert key issued by Twitter>
consumer_secret = <secret associated with Twitter key goes here>
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

# In this code, we specify text to search. In this sample, we are looking for Tweets with the word 'Microsoft'.
# We limit number of Tweets to return to 10. 
for tweet in tweepy.Cursor(api.search, q='microsoft').items(10):
    #print(tweet.text)
    print("Sending data to eventhub ...")
    data = EventData(tweet.text)
    sender.send(data)

client.stop()


print("*********************** READING DATA FROM EVENT HUB******************************")

# Declare variables for receiving / reading from Eventhub

consumerGroup = "$default"
offset = Offset("-1")
partition = "1"

total = 0
last_sn = -1
last_offset = "-1"
client = EventHubClient(address, debug=False, username=user, password=key)

receiver = client.add_receiver(consumerGroup, partition, prefetch=5000, offset=offset)
client.run()
batch = receiver.receive(timeout=5000)

while batch:
    for event_data in batch:
        last_offset = event_data.offset
        last_sn = event_data.sequence_number
        #print("Received: {}, {}".format(last_offset.value, last_sn))
        #print("***********************************************")
        #print(event_data.body_as_str())
        #print("***********************************************")
        jsonDoc = { "documents": [{"language":language,"id":id,"Text":event_data.body_as_str()}]}
        entities=callTextApi(apiEndpoint,subKey,jsonDoc)
        print(json.dumps(entities, separators=(',', ':'), sort_keys=True, indent = 4 * ' '))
        total += 1
    batch = receiver.receive(timeout=5000)