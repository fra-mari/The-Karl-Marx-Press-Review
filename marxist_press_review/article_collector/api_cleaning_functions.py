"""
This module contains the functions to extract clean and prepare the text of an json
dictionary extracted from the API of the Guardian.
The functions are then used by the module guardian_collector.
"""

import re
import logging
import os
import datetime as dt
import requests
import pandas as pd
from sqlalchemy.sql import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s: %(message)s")


# The Guardian
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")

# RESEARCH PARAMETERS for the API
PARAMETERS = {
    "order-by": "newest",
    "page-size": 20,
    "show-fields": ["all"],
    "show-tags": ["keyword"],
    "api-key": f"{GUARDIAN_API_KEY}"}


def extract_img_and_tag(entry_main, entry_tag):
    """
    Extracts features about an article's main image (3) and tags (1) from the API dictionary
    and returns them: 4 variables returned.
    ------
    ARGUMENTS:
    The API dictionary entries for the main image ('result->field->main') and tags ('result->tags')
    """

    img_path = re.findall(r"<img src=\"(.+?)\"", entry_main)
    if len(img_path) != 0:
        img_url = img_path[0]
    else:
        img_url = "NULL"

    img_descr = re.findall(r"<span class=\"element-image__caption\">(.+?)<", entry_main)
    if len(img_descr) != 0:
        img_capt = img_descr[0]
    else:
        img_capt = "NULL"

    img_credits = re.findall(r"<span class=\"element-image__credit\">(.+?)<", entry_main)
    if len(img_credits) != 0:
        img_cred = img_credits[0]
    else:
        img_cred = "NULL"

    tags = None
    for el in entry_tag:
        if el["type"] == "keyword":
            if tags is None:
                tags = el["webTitle"].lower()
            else:
                tags = f'{tags},{el["webTitle"].lower()}'

    return img_url, img_capt, img_cred, tags


def get_new_articles(section):
    """
    Get new articles on a certain topic via the API of The Guardian
    and writes their data into separate dictionaries,
    which are returned into a LIST
    ----------
    ARGUMENT:
    A STRING linking to the desired SECTION of THE Guardian.
    """

    guardian_endpoint = f"https://content.guardianapis.com/search?section={section}"
    resp = requests.get(guardian_endpoint, PARAMETERS)
    if resp.status_code == 200:
        logging.info(f"Successfully connected to {guardian_endpoint} : scraping...")
        respjson = resp.json()
        many_results = respjson["response"]["results"]

        articles = []
        counter = 0
        for results in many_results:

            try:
                fields = results["fields"]

                img_url, img_capt, img_cred, tags = extract_img_and_tag(fields["main"], results["tags"])

                article = {
                    "date": f"{pd.to_datetime(re.sub(r'[T,Z]',' ', results['webPublicationDate']))}",
                    "section_id": f"{results['sectionId']}",
                    "section_name": f"{results['sectionName']}",
                    "title": f"{results['webTitle']}",
                    "author": f"{fields['byline']}",
                    "subtitle": f"{fields['trailText']}",
                    "body": f"{fields['bodyText']}",
                    "img_url": f"{img_url}",
                    "img_descr": f"{img_capt}",
                    "img_cred": f"{img_cred}",
                    "language": f"{fields['lang']}",
                    "url": f"{results['webUrl']}",
                    "short_url": f"{fields['shortUrl']}",
                    "tags": f"{tags}",
                }

                articles.append(article)
                counter = counter + 1

            except:
                logging.warning(
                    "Inconsistent fields in API response with regard to an article: skipping."
                )
        logging.info(
            f"Section {section.upper()}: {counter} article(s) successfully scraped. Now producing Marx's comments about them."
        )

    else:
        logging.warning(
            f"There is a PROBLEM: {guardian_endpoint} has answered with {resp.status_code}")
        articles = []

    return articles


def store_article_on_postgres(article_data, postrges_connection):
    """
    Writes an item from the data collected by get_new_articles( ) into the PostgreSQL database.
    ---------
    ARGUMENTS:
    1) a dictionary from the list of articles produced by the function get_new_articles( ).
    2) the connected postgres engine
    """

    try:
        postrges_connection.execute(
            text("INSERT INTO guardian_articles VALUES (:a,:b,:c,:d,:e,:f,:g,:h,:i,:j,:k,:l,:m,:n,:o,:p,:q);"),
            a=article_data["date"],
            b=article_data["section_id"],
            c=article_data["section_name"],
            d=article_data["title"],
            e=article_data["author"],
            f=article_data["subtitle"],
            g=article_data["body"],
            h=article_data["img_url"],
            i=article_data["img_descr"],
            j=article_data["img_cred"],
            k=article_data["language"],
            l=article_data["url"],
            m=article_data["short_url"],
            n=article_data["tags"],
            o=article_data["marx_comment"],
            p=article_data["sentiment_score"],
            q=article_data["judgement"],
        )
        logging.info("New article written into postgres.")
    except:
        logging.warning(
            "Encountered a problem while attempting to store an article into postgres. Skipping.")


def remove_old_articles_from_postgres(postrges_connection):
    """
    Removes all the articles older than a week form the the PostgreSQL database.
    ARGUMENT: the connected postgres engine.
    """

    today = pd.to_datetime(dt.date.today())
    a_week_ago = today - pd.Timedelta(days=7)

    postrges_connection.execute(
        f"""DELETE from guardian_articles
            WHERE date < '{a_week_ago}'
            ;
    """)

    logging.info("Records older than a week erased from postgres.")
