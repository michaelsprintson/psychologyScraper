import config
import requests
import json
import csv
import TextAnalyzer
import time

## General information: This piece of code sends requests to twitter about the desired keywords. If found, it is written in a csv file.

# Creates the url reference to the api and the variables
def create_url(keyword):
    search_url = "https://api.twitter.com/2/tweets/search/recent" 

    query_params = {'query': keyword,
                    # 'start_time': start_date,
                    'max_results': 100,
                    'user.fields': 'id,name,username',
                    'expansions' : 'author_id',
                    'next_token': {}}
    return (search_url, query_params)

# Runs the api request
def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# Creates Search Strings (Search string limit 128 chars)
def createSearchStrings():
    searchStrings = []
    currentString = ""
    for keyword in TextAnalyzer.textValuesDict:
        next_search = f'({keyword.replace(" ", "%20")})'
        if len(currentString) + len(next_search) + 6 > 128: 
            searchStrings.append(currentString)
            currentString = ""
        if currentString != "":
            currentString += "OR"
        currentString += next_search
    searchStrings.append(currentString)
    return searchStrings

def runTwitterScraper():
    valid_responses = []
    responseCount = 1
    for searchString in createSearchStrings():
        url = create_url(searchString)
        continueFlag = True
        nextToken = {}
        while continueFlag:
            time.sleep(5)
            json_response = connect_to_endpoint(url[0], {"Authorization": "Bearer {}".format(config.twitter_bearer_token)}, url[1], nextToken)
            print(f'Response page: ${responseCount}')
            print(f'Response metadata: ${json_response["meta"]}')
            if "data" in json_response:
                for response in json_response["data"]:
                    if (TextAnalyzer.textPasses(response["text"])):
                        valid_responses.append(response)
            if "next_token" not in json_response["meta"]:
                continueFlag = False
            else:
                nextToken = json_response["meta"]["next_token"] 

    csvFile = open("data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    for validResponse in valid_responses:
        csvWriter.writerow(validResponse)
    
    csvFile.close()