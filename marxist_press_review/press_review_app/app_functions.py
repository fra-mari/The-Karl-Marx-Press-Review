"""
This module contains:
1) the function that feeds the webapp page for the user to generate marxist text given a prompt; 
2) A function that generates sql queries for the different pages of the webapp.
"""

import re
import logging
from aitextgen import aitextgen

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s")


ai = aitextgen(model_folder="trained_model")

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

def text_generator(prompt):
    """Generates marxist text based on a textual input.
    ----
    ARGUMENT: A string of max 4 words.
    """
    prompt_words = prompt.split()
    if prompt == "":
        marx_comment = "GPT-2-Marx could not generate any text from this prompt. Try something else."
    elif len(prompt_words) > 5:
        marx_comment = "Uh...we had said no more than FIVE words, right? 😅 "
    elif len(prompt_words) <= 5:
        marx_statement = ai.generate_one(
            prompt=prompt.capitalize(),
            min_length=10,
            max_length=70,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            no_repeat_ngram_size=2,
        )

        for key, index in REGEX.items():
            sentence = re.sub(key, index, marx_statement)

        marx_statement_clean = re.findall(NO_TRUNC_INITIAL_SENTENCE_PATTERN, sentence)

        if len(marx_statement_clean) == 0:
            marx_comment = "GPT-2-Marx could not generate any text from this prompt. Try something else."
        else:
            marx_comment = marx_statement_clean[0]

    return marx_comment

def select_articles_from_section(section):
    """
    Takes a STRING matching one possible value for the "section_id" column of the Guardian SQL database
    and completes the query accordingly.
    """
    query = f"""SELECT date,
                              title,
                              author,
                              body,
                              img_url,
                              img_descr,
                              img_cred,
                              short_url,
                              marx_comment,
                              marx_judgement 
                        FROM guardian_articles
                        WHERE section_id = '{section}'
                        ORDER BY date DESC
                        LIMIT 5
                        ;"""

    return query
