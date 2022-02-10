from . import config
import requests
import json
import csv
from . import TextAnalyzer
import time
import datetime as DT
from dateutil import parser
from tqdm import tqdm

## General information: This piece of code sends requests to twitter about the desired keywords. If found, it is written in a csv file.

# Creates the url reference to the api and the variables
def create_url(keyword):
    search_url = "https://api.twitter.com/2/tweets/search/recent" 

    query_params = {'query': keyword,
                    # 'start_time': start_date,
                    'max_results': 100,
                    'user.fields': 'id,name,username',
                    'tweet.fields': 'created_at',
                    'expansions' : 'author_id',
                    'next_token': {}}
    return (search_url, query_params)

# Runs the api request
def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token
    response = requests.request("GET", url, headers = headers, params = params)
    # print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# Creates Search Strings (Search string limit 128 chars)
def createSearchStrings():
    searchStrings = []
    currentString = ""
    for keyword in TextAnalyzer.textValuesDict:
        next_search = f'({keyword.replace(" ", "%20")})'
        if len(currentString) + len(next_search) + 6 > 450: 
            searchStrings.append(currentString)
            currentString = ""
        if currentString != "":
            currentString += "OR"
        currentString += next_search
    searchStrings.append(currentString)
    return searchStrings

def runTwitterScraper():

    today = DT.datetime.now(DT.timezone.utc)
    # week_ago = today - DT.timedelta(days=7)

    responseCount = 1
    with tqdm(total=604800) as pbar:
        for searchString in createSearchStrings():
            url = create_url(searchString)
            continueFlag = True
            nextToken = {}
            while continueFlag:
                time.sleep(5)
                json_response = connect_to_endpoint(url[0], {"Authorization": "Bearer {}".format(config.twitter_bearer_token)}, url[1], nextToken)
                page_oldest_date = parser.parse(([i for i in json_response['data'] if i['id'] == json_response['meta']['oldest_id']][0]['created_at']))
                final_val = (today - page_oldest_date).total_seconds()
                pbar.update(int(final_val) - pbar.n)

                rc = json_response['meta']['result_count']
                if int(rc) < 90:
                    print(f"Response page: {responseCount}, {rc}")
                
                if "data" in json_response:
                    for response in json_response["data"]:
                        if (TextAnalyzer.textPasses(response["text"])):
                            # print(response, '\n\n')
                            with open("test.txt", "a") as myfile:
                                myfile.write(response.__repr__() + "\n")
                            responseCount += 1
                if "next_token" not in json_response["meta"]:
                    print("stopped, no next token")
                    continueFlag = False
                else:
                    if responseCount > 10:
                        continueFlag = False
                    nextToken = json_response["meta"]["next_token"] 

    

    # for validResponse in valid_responses:
    #     csvWriter.writerow(validResponse)
    
    