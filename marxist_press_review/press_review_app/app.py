"""
This module manages the webapp of the marxist press review.
"""

import logging
import os
import pandas as pd
from flask import Flask
from flask import render_template
from flask import request
from sqlalchemy import create_engine
from app_functions import select_articles_from_section, text_generator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

# ENVIRONMENT VARIABLE
# PostgreSQL
POSTGRES_PSW = os.getenv("POSTGRES_PASSWORD")


POSTGRES_USER = "postgres"  
HOST = "postgresdb" 
PORT = "5432"  
DATABASE_NAME = "pg_guardian"

app = Flask(__name__)

pg = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PSW}@{HOST}:{PORT}/{DATABASE_NAME}')
try:
    pg.connect()
    logging.info(f'Connected to the postgres server on port {PORT}.')
except:
    logging.critical(f'Could not connect to server: connection refused.\nIs the server running on host "{HOST}"?\nIs it accepting TCP/IP connections on port {PORT}?\n\nExit.\n') 
    exit()

@app.route('/')
def start_page():
    
    return render_template('start.html')

@app.route('/world')     
def world_press_review():

    articles = pg.execute(select_articles_from_section('world'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('world.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/education')     
def education_press_review():

    articles = pg.execute(select_articles_from_section('education'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('education.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/politics')     
def politics_press_review():

    articles = pg.execute(select_articles_from_section('politics'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('politics.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/environment')     
def environment_press_review():

    articles = pg.execute(select_articles_from_section('environment'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('environment.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/global-development')     
def glob_dev_press_review():

    articles = pg.execute(select_articles_from_section('global-development'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('global-development.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/money')     
def money_press_review():

    articles = pg.execute(select_articles_from_section('money'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('money.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/sport')     
def sport_press_review():

    articles = pg.execute(select_articles_from_section('sport'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('sport.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/business')     
def business_press_review():

    articles = pg.execute(select_articles_from_section('business'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('business.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])

@app.route('/culture')     
def culture_press_review():

    articles = pg.execute(select_articles_from_section('culture'))
    df = pd.DataFrame(articles, columns=articles.keys())
    
    return render_template('culture.html', ar1=df.loc[0],ar2=df.loc[1],ar3=df.loc[2],ar4=df.loc[3],ar5=df.loc[4])


@app.route('/about')     
def about():
    return render_template('about.html')

@app.route('/custom-generator')
def custom_generator():
    if request.args:
        html_data = dict(request.args)
        prompt = html_data['prompt']
        result = text_generator(prompt)
        return render_template('speak.html',result=result)
    else:
        return render_template('speak.html')

