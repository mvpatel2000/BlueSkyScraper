import praw
import pandas as pd
import datetime as dt
import numpy as np
from tqdm import tqdm
import json
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

def get_date(created):
    return dt.datetime.fromtimestamp(created)

def scrape_reddit(client):
    reddit = praw.Reddit(client_id='4BVKWUfa63EwBg', \
                         client_secret='0XI3VmcquT5NO6qaax3GNL9Ktxs', \
                         user_agent='BlueSkyScraper', \
                         username='mvpat123', \
                         password='mihirkavya')

    # Update limit as needed. Max is 1000, but there is a workaround?
    #. hot, .new, .controversial, .top, and .gilded
    # .search("SEARCH_KEYWORDS")

    topics_dict = { "title":[], \
                    "score":[], \
                    "id":[], "url":[], \
                    "comms_num": [], \
                    "created": [], \
                    "body":[], \
                    "ent_score":[], \
                    "ent_magn":[], \
                    "overall_score":[], \
                    "overall_magn":[]}

    rjetblue = reddit.subreddit('jetblue')
    raviation = reddit.subreddit('aviation')
    rflying = reddit.subreddit('flying')
    search_rs = [raviation, rflying]
    for submission in rjetblue.top(limit=1000):
        topics_dict["title"].append(submission.title)
        topics_dict["score"].append(submission.score)
        topics_dict["id"].append(submission.id)
        topics_dict["url"].append(submission.url)
        topics_dict["comms_num"].append(submission.num_comments)
        topics_dict["created"].append(submission.created)
        topics_dict["body"].append(submission.selftext)
    print("Scraped r/jetblue, total size:",len(topics_dict["title"]))
    for subreddit in search_rs:
        for submission in subreddit.search("jetblue"):
            topics_dict["title"].append(submission.title)
            topics_dict["score"].append(submission.score)
            topics_dict["id"].append(submission.id)
            topics_dict["url"].append(submission.url)
            topics_dict["comms_num"].append(submission.num_comments)
            topics_dict["created"].append(submission.created)
            topics_dict["body"].append(submission.selftext)
        print("Scraped r/"+str(subreddit.title)+", total size:",len(topics_dict["title"]))

    for i in tqdm(range(len(topics_dict["title"]))):
        ent_score, ent_magnitude, doc_score, doc_magnitude = analyze_text(client, text=topics_dict["body"][i])
        topics_dict["ent_score"].append(ent_score)
        topics_dict["ent_magn"].append(ent_magnitude)
        topics_dict["overall_score"].append(doc_score)
        topics_dict["overall_magn"].append(doc_magnitude)

    metrics = ["ent_score","ent_magn","overall_score","overall_magn"]
    for metric in metrics:
        metric_score = np.asarray(topics_dict[metric])
        print(metric,"Mean:",np.mean(metric_score),"St Dev:",np.std(metric_score))

    with open('./csvs/reddit-jetblue-sentiment.json', 'w') as fp:
        json.dump(topics_dict, fp)

    # topics_data = pd.DataFrame(topics_dict)
    # _timestamp = topics_data["created"].apply(get_date)
    # topics_data = topics_data.assign(timestamp = _timestamp)
    # topics_data.to_csv('csvs/reddit-jetblue.csv', index=False, sep = '|') 

def analyze_text(client, text="Hello, world! I love Kavya!"):
    # The text to analyze
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    doc_sentiment = client.analyze_sentiment(document=document).document_sentiment # .score, .magnitude
    ent_sentiments = client.analyze_entity_sentiment(document=document).entities

    ent_score = 0
    ent_magnitude = 0
    for ent in ent_sentiments:
        if ent.name == "jetblue" or "JetBlue" or "Jetblue" or "jet blue" or "Jet Blue":
            ent_score += ent.sentiment.score
            ent_magnitude += ent.sentiment.magnitude
    # print("Entity (Jet Blue) sentiment. Score:", ent_score, "Magnitude:", ent_magnitude)
    # print("Overall sentiment. Score:", doc_sentiment.score, "Magnitude:", doc_sentiment.magnitude)
    return ent_score, ent_magnitude, doc_sentiment.score, doc_sentiment.magnitude

def postprocess_reddit():
    with open('./csvs/reddit-jetblue-sentiment.json', 'r') as fp:
        topics_dict = json.load(fp)

    metrics = ["ent_score","ent_magn","overall_score","overall_magn"]
    for metric in metrics:
        metric_score = np.asarray(topics_dict[metric])
        print(metric,"Mean:",np.mean(metric_score),"St Dev:",np.std(metric_score))

if __name__ == "__main__":
    # Instantiates a client
    client = language.LanguageServiceClient()
    
    #scrape_reddit(client)
    postprocess_reddit()