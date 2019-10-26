import praw
import pandas as pd
import datetime as dt

def get_date(created):
    return dt.datetime.fromtimestamp(created)

reddit = praw.Reddit(client_id='4BVKWUfa63EwBg', \
                     client_secret='0XI3VmcquT5NO6qaax3GNL9Ktxs', \
                     user_agent='BlueSkyScraper', \
                     username='mvpat123', \
                     password='mihirkavya')

subreddit = reddit.subreddit('jetblue')

# Update limit as needed. Max is 1000, but there is a workaround?
#. hot, .new, .controversial, .top, and .gilded
# .search("SEARCH_KEYWORDS")
top_subreddit = subreddit.top(limit=500) 

for submission in subreddit.top(limit=1):
    print(submission)

topics_dict = { "title":[], \
                "score":[], \
                "id":[], "url":[], \
                "comms_num": [], \
                "created": [], \
                "body":[]}

for submission in top_subreddit:
    topics_dict["title"].append(submission.title)
    topics_dict["score"].append(submission.score)
    topics_dict["id"].append(submission.id)
    topics_dict["url"].append(submission.url)
    topics_dict["comms_num"].append(submission.num_comments)
    topics_dict["created"].append(submission.created)
    topics_dict["body"].append(submission.selftext)

topics_data = pd.DataFrame(topics_dict)
_timestamp = topics_data["created"].apply(get_date)
topics_data = topics_data.assign(timestamp = _timestamp)
topics_data.to_csv('csvs/reddit-jetblue.csv', index=False) 
