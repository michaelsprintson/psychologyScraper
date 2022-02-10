import config
import requests
import json
import csv
import TextAnalyzer
import time
import datetime as DT
from dateutil import parser
from tqdm import tqdm
import ast
from nltk.corpus import stopwords
import pandas as pd

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

def runTwitterScraper(location = 'test.txt'):
    
    today = DT.datetime.now(DT.timezone.utc)
    # week_ago = today - DT.timedelta(days=7)
    current_oldest_date = today

    responseCount = 1
    counter = 0
    tweets_processed = 0
    with tqdm(total=604800) as pbar:
        for searchString in createSearchStrings():
            url = create_url(searchString)
            continueFlag = True
            nextToken = {}
            while continueFlag:
                time.sleep(1)
                counter += 1
                #grab json response
                json_response = connect_to_endpoint(url[0], {"Authorization": "Bearer {}".format(config.twitter_bearer_token[counter % 5])}, url[1], nextToken)
                # calculate progress bar update
                tweets_processed += json_response['meta']['result_count']
                page_oldest_date = parser.parse(([i for i in json_response['data'] if i['id'] == json_response['meta']['oldest_id']][0]['created_at']))
                if page_oldest_date < current_oldest_date: #if its older
                    current_oldest_date = page_oldest_date
                final_val = (today - current_oldest_date).total_seconds()
                pbar.update(int(final_val) - pbar.n)
                pbar.desc = f"processed {tweets_processed} tweets - "
                
                #process each response, write to file if within spec
                if "data" in json_response:
                    for response in json_response["data"]:
                        if (TextAnalyzer.textPasses(response["text"])):
                            # print(response, '\n\n')
                            with open(location, "a") as myfile:
                                #in response data, correct all quotations to be not excepted
                                myfile.write(response.__repr__() + "\n")
                            responseCount += 1
                #
                if "next_token" not in json_response["meta"]:
                    print("stopped, no next token")
                    continueFlag = False
                else:
                    # if responseCount > 10:
                    #     continueFlag = False
                    nextToken = json_response["meta"]["next_token"] 

    

    # for validResponse in valid_responses:
    #     csvWriter.writerow(validResponse)

def write_to_csv(location = 'test.txt', output = "output.csv"):
    keys = ['id', 'author_id', 'created_at', 'text']
    with open(location) as file:
        responses = file.readlines()
    to_pd = [ast.literal_eval(res) for res in responses]
    a_file = open(output, "w")
    dict_writer = csv.DictWriter(a_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(to_pd)
    a_file.close()
    print(f"wrote {location} to {output}")
    return to_pd

def get_relevant_words(to_pd):
    tdf = pd.DataFrame(to_pd)
    twitter_stops = stopwords.words('english') + ['RT', 'I', 'if','&amp;', 'if', 'it\'s', '\r', '\t', '\n', '-']
    words = [i.lower().replace(',', '').replace('\'', '') for j in [i.split(' ') for i in tdf['text'].values] for i in j if i not in twitter_stops]
    return words

def filter_by_word(tdf, word):
    return tdf[tdf['text'].apply(lambda s: word in s)]