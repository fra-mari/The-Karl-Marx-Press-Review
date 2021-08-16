"""
This module contains the functions to:
1) generate marxist comments based on the trailing test of newspaper articles.
2) run some basic sentiment analysis on them, just for the fun of doing it. 
The functions are then used by the module guardian_collector.
"""

import re
from aitextgen import aitextgen
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(levelname)s: %(message)s")


ai = aitextgen(model_folder="trained_model")
s = SentimentIntensityAnalyzer()


NO_TRUNC_INITIAL_SENTENCE_PATTERN = r"^[A-Z][a-z]+.+\."
REGEX = {
    r"\n": " ",
    r"\\'": "’",
    r"\[.+?\]": "",
    r"\[.+?\.": ".",
    r"  [0-9]+.": "",
    r"\(\?\)": "",
    r"\([0-9]{1,2}\)": "",
    r"[<>]": "",
    r"\.+": ".",
    r" \. ": ". ",
    r"\|\|[A-Z]+\|": "",
    r"(\.)[A-Za-z0-9]+": ". ",
    r" {2,}": " ",
    r'''(.\")[A-Za-z0-9]''':'. "'
}


def have_marx_comment_on_article(prompt):
    """Reworks the trailing text of an article
    and uses it as a prompt to generate a marxist short text.
    ----
    ARGUMENT: the trailing text of an article.
    """
    prompt_words = prompt.split()
    if len(prompt_words) >= 10:
        truncated_prompt = prompt_words[0].capitalize()
        for word in prompt_words[1:10]:
            truncated_prompt += f" {word}"
    else:
        truncated_prompt = prompt_words[0].capitalize()
        for word in prompt_words[1:]:
            truncated_prompt += f" {word}"

    marx_statement = ai.generate_one(
        prompt=truncated_prompt,
        min_length=15,
        max_length=70,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.1,
        no_repeat_ngram_size=2)

    for key, index in REGEX.items():
        sentence = re.sub(key, index, marx_statement)

    marx_statement_clean = re.findall(NO_TRUNC_INITIAL_SENTENCE_PATTERN, sentence)
    if len(marx_statement_clean) == 0:
        marx_comment = "Karl Marx has nothing to say about this."  # can be improved
        logging.warning(
            "The gpt2 model could not produce a meaningful text for an article.")
        return marx_comment
    else:
        marx_comment = marx_statement_clean[0]
        logging.info("The gpt2 has produced a marxist comment on an article!")
        return marx_comment


def analyser_of_the_marxist_sentiment(comment):
    """
    This function takes a marxist comment
    runs some basic sentiment analysis on it,
    and returns the comment and the analyis wrapped in a python dictionary.
    ----
    ARGUMENT:
    A STRING: the marxist comment gerated by the have_marx_comment_on_article( ) function.
    """
    comment_and_analyis = {}
    comment_and_analyis["marx_comment"] = comment

    scores = s.polarity_scores(comment)
    comment_analysis = scores["compound"]
    if comment == "Karl Marx has nothing to say about this.":
        comment_and_analyis["sentiment_score"] = 0.0
        comment_and_analyis["judgement"] = "🤷🏼‍♂️ Don’t blame him. He’s a man of the 19th century, after all!"
    else:
        comment_and_analyis["sentiment_score"] = comment_analysis
        if comment_analysis > 0.7:
            comment_and_analyis["judgement"] = "🤩     Karl Marx loves this news!"
        elif comment_analysis > 0.2:
            comment_and_analyis["judgement"] = "👍🏻     Karl Marx likes this news!"
        elif comment_analysis < -0.7:
            comment_and_analyis["judgement"] = "🤬     Karl Marx has read this news and is about to start a Revolution!"
        elif comment_analysis < -0.2:
            comment_and_analyis["judgement"] = "👎🏻     Karl Marx dislikes this news!"
        else:
            comment_and_analyis["judgement"] = "😶     Karl Marx does not seem particularly interested."

    return comment_and_analyis
