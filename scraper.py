import json
from pathlib import Path
import argparse

import pandas as pd


SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_PATH = SCRIPT_DIR / "data.json"
OUTPUT_PATH = SCRIPT_DIR / "output.csv"


def get_id(url:str):
    sections = url.split("/")
    for section in sections:
        if "article" in section:
            return section.split("-")[1]


def get_comments_url(article_id, max_comments:int=500) -> str:
    url = f"https://www.dailymail.co.uk/reader-comments/p/asset/readcomments/{article_id}?max={max_comments}&order=desc"
    return url


def read_json() -> dict:
    try:
        with open(DATA_PATH) as f:
            data = json.load(f)
    except:
        print(f"Couldn't read data from {DATA_PATH}.")
    return data


def flatten_comments(comment, data_list:list) -> None:
    # Add the comment to the data_list
    data_list.append({
        'userAlias': comment['userAlias'],
        'assetHeadline': comment['assetHeadline'],
        'userLocation': comment['userLocation'],
        'formattedDateAndTime': comment['formattedDateAndTime'],
        'assetId': comment['assetId'],
        'voteCount': comment['voteCount'],
        'id': comment['id'],
        'userIdentifier': comment['userIdentifier'],
        'hasProfilePicture': comment['hasProfilePicture'],
        'voteRating': comment['voteRating'],
        'dateCreated': comment['dateCreated'],
        'assetCommentCount': comment['assetCommentCount'],
        'assetUrl': comment['assetUrl'],
        'message': comment['message'],
    })

    # Recursively add replies
    if 'replies' in comment and 'comments' in comment['replies']:
        for reply in comment['replies']['comments']:
            flatten_comments(reply, data_list)


def comments_parser(json_data:dict) -> pd.DataFrame:
    page_data = json_data['payload']['page']
    data_list = []
    for comment in page_data:
        flatten_comments(comment, data_list)

    df = pd.DataFrame(data_list)
    df.drop(columns=['assetHeadline', 'assetId', 'assetUrl', 'assetCommentCount'], inplace=True)
    return df


def main():
    parser = argparse.ArgumentParser(description="Get comments from Daily Mail articles.")
    parser.add_argument("-u", "--url", type=str, required=True, help="URL of the article")
    args = parser.parse_args()
    myurl: str = args.url
    id = get_id(myurl)
    if id is not None:
        comm_url = get_comments_url(id, 1000)
        print(f"\n{comm_url}\n")
        print("Go to this url and select raw data. Copy and paste all the data into \"data.json\".")
        input("Then press Enter to continue...")
        data = read_json()
        mydf = comments_parser(data)
        print(f"Data preview:\n{mydf.head()}")
        print(f"Comments parsed: {mydf.shape[0]}")
        try:
            mydf.to_csv(OUTPUT_PATH, index=False)
            print(f"Data written to \"{OUTPUT_PATH}\".")
        except:
            print(f"Couldn't write data to \"{OUTPUT_PATH}\".")
    else:
        print("Couldn't find Article ID")


if __name__ == "__main__":
    main()