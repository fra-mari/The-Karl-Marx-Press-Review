"""
This module uses the API of The Guardian to collect the metadata of the most recent articles on various topics,
and stores them into an SQL database. Data older than a week are automatically erased from the database.
"""

import logging
import os
from time import sleep
from sqlalchemy import create_engine
from api_cleaning_functions import get_new_articles, store_article_on_postgres, remove_old_articles_from_postgres
from marxist_text_generator import have_marx_comment_on_article, analyser_of_the_marxist_sentiment


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s: %(message)s")


# ENVIRONMENT VARIABLES
# PostgreSQL

POSTGRES_PSW = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = "postgres"  
HOST = "postgresdb" 
PORT = "5432"  
DATABASE_NAME = "pg_guardian"

SECTIONS = [
    "sport",
    "world",
    "politics",
    "environment",
    "global-development",
    "money",
    "education",
    "business",
    "culture"] 


if __name__ == "__main__":

    pg = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PSW}@{HOST}:{PORT}/{DATABASE_NAME}")
    try:
        pg.connect() 
        logging.info(f"Connected to the postgres server on port {PORT}.")
    except:
        logging.critical(
            f'Could not connect to server: connection refused.\nIs the server running on host "{HOST}"?\nIs it accepting TCP/IP connections on port {PORT}?\n\nExit.\n'
        )
        exit()

    pg.execute(
        """
        CREATE TABLE IF NOT EXISTS guardian_articles (
        date TIMESTAMP,
        section_id VARCHAR(200),
        section_name VARCHAR(200),
        title VARCHAR(500),
        author VARCHAR(500),
        subtitle VARCHAR(1000),
        body VARCHAR(200000),
        img_url VARCHAR(1000),
        img_descr VARCHAR(1000),
        img_cred VARCHAR(1000),
        language VARCHAR(10),
        url VARCHAR(1000),
        short_url VARCHAR(400),
        tags VARCHAR(1000),
        marx_comment VARCHAR(1100),
        sentiment_score NUMERIC,
        marx_judgement VARCHAR(200)      
        );
    """)

    while True:
        remove_old_articles_from_postgres(pg)
        control = [] 
        condition = True
        counter = 0
        logging.info("control list cleaned up.")

        while condition:
            if counter == 7:
                condition = False

            for section in SECTIONS:

                new_articles = get_new_articles(section)
                for article in new_articles:
                    marx_impressions = analyser_of_the_marxist_sentiment(
                        have_marx_comment_on_article(article["subtitle"])
                    )
                    article.update(marx_impressions)

                for article in new_articles:
                    if "<strong>" in article["subtitle"]:
                        continue
                    elif "<strong>" in article["img_descr"]:
                        continue
                    elif article["img_url"] == "NULL":
                        continue
                    elif article["img_descr"] == "NULL":
                        continue
                    elif article["img_cred"] == "NULL":
                        continue
                    elif article["author"] == "":
                        continue
                    elif article["title"] not in control:
                        store_article_on_postgres(article, pg)  # does not work.
                        control.append(article["title"])
                    else:
                        logging.info("Article already in postgres: skipping.")

            sleep(60 * 60 * 23.5)  # the whole process with 9 sections takes more or less 30 mins
            counter += 1
            