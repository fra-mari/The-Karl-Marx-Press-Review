'''
This module scrapes the data from the "Marx Engels Archive"
and preprocesses it for the fine-tuning of a gpt2 model
'''

import requests 
import logging
import os 
import re
import time
from tqdm import tqdm, trange
from bs4 import BeautifulSoup as soup

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(message)s')

# Each entry of the dictionary contains a URL and the number of HTML pages of a givent marxist work
marxist_works = {'manifesto':('https://marxists.architexturez.net/archive/marx/works/1848/communist-manifesto/', 4),
                 'civil_war_france':('https://marxists.architexturez.net/archive/marx/works/1871/civil-war-france/',6),
                 'principles_of_communism':('https://marxists.architexturez.net/archive/marx/works/1847/11/prin-com.htm',1),
                 'wage_labour_and_capital':('https://marxists.architexturez.net/archive/marx/works/1847/wage-labour/',9),
                 'pref_crit_pol_economy':('https://marxists.architexturez.net/archive/marx/works/1859/critique-pol-economy/preface-abs.htm',1),
                 'socialism_utopian_scientific':('https://marxists.architexturez.net/archive/marx/works/1880/soc-utop/',3),
                 '18th_brumaire':('https://marxists.architexturez.net/archive/marx/works/1852/18th-brumaire/',7),
                 'estranged_labour':('https://marxists.architexturez.net/archive/marx/works/1844/manuscripts/labour.htm',1),
                 'pr_property_and_communism':('https://marxists.architexturez.net/archive/marx/works/1844/manuscripts/comm.htm',1) 
                }


def text_splitter(raw_work, cleaned_works):
    '''
    Takes a LIST OF STRINGS containing paragraphs of a marxist work,
    and splits them in chunks of 1024 characters (i.e. the max length accepted by gpt2);
    Gets rid of trailing parts of words or sentences that may have remained in each paragraph.
    RETURNS a LIST OF STRINGS containing the new paragraphs.
    '''
    
    no_trunc_sentence_pattern = r'\. (.+\w+\.)'
    no_trunc_initial_sentence_pattern = r"^[A-Z][a-z]+.+\."

    for parag in raw_work:
        if len(parag) > 1024: 
            split_par = re.findall('.{1,1024}', parag)
            for sent in split_par:
                if sent[0].isupper():
                    new_sent = re.findall(no_trunc_initial_sentence_pattern, sent)
                    if len(new_sent) > 0:
                        cleaned_works.append(new_sent[0].strip())                                      
                else:
                    new_sent = re.findall(no_trunc_sentence_pattern, sent)
                    if len(new_sent) > 0:
                        cleaned_works.append(new_sent[0].strip()) 
        else:
            cleaned_works.append(parag)
    
    return cleaned_works
    

def get_marxist_text(works_dictionary):
    '''
    Scrapes marxist works from 'https://marxists.architexturez.net/,
    polishes them,
    and writes them into txt files.
    
    Also produces a LIST OF STRINGS containing text from the input marxist works, already split in
    chunks long enough to be used to fine tune a gpt2 model.
    
    -----------
    ARGUMENT: 
    A dictionary of tuples: the dictionary key is the title of the resulting .txt file for a marxist work,
    the first element of the tuple is the URL of chosen work's page of contents,
    the third is the number of html-pages linked to that page of contents.
    '''
    
    cleaner_marxist_text = []
    counter = 0
    path = 'training_dataset/raw_texts/'
    if not os.path.exists(path):
        os.makedirs(path)
            
    for el in works_dictionary:
        filename = str(el)
        contents_url = works_dictionary[el][0]
        page_num = works_dictionary[el][1]    
        paragraphs = []
        undesirables = []
        
        if page_num == 1:
            html = requests.get(contents_url)
            if html.status_code != 200:
                logging.warning(f"Download of {contents_url} failed with status code {html.status_code}. Please verify that the URL exists.")
            else:
                text = soup(html.text,'html.parser')    

                for par in text.find_all('p'):
                    par_text = par.text.replace('\n',' ').strip()    
                    paragraphs.append(par_text)

                for par in text.find_all('p', class_=['info','information','skip','footer','title','fst','next','inline']):
                    par_text = par.text.replace('\n',' ').strip()
                    undesirables.append(par_text)

                work = [x for x in paragraphs if x not in undesirables]
                if work:
                    cleaner_marxist_text = text_splitter(work, cleaner_marxist_text)
                    with open(f'{path+filename}.txt', 'w') as f:
                        f.writelines(work)
                    for i in trange(1):
                        time.sleep(0.25)
                    logging.info(f'Text from {contents_url} successfully downloaded into "{path+filename}.txt".')
                    counter += 1

        else:
            
            for page in trange(1,page_num+1):
                
                address = f'''{contents_url}ch0{page}.htm'''
                if address == 'https://marxists.architexturez.net/archive/marx/works/1847/wage-labour/ch02.htm': 
                    continue
                elif address == 'https://marxists.architexturez.net/archive/marx/works/1847/wage-labour/ch03.htm':    
                    continue #the HTML of these 2 pages has a faulty nested structure that produces paragraph multiplication while parsing.
                html = requests.get(address)
                if html.status_code != 200:
                    logging.warning(f"Download of {contents_url} failed with status code {html.status_code}. Please verify that the URL exists.")
                    break
                        
                text = soup(html.text,'html.parser')    

                for par in text.find_all('p'):
                    par_text = par.text.replace('\n',' ').strip()    
                    paragraphs.append(par_text)
                    
                for par in text.find_all('p', class_=['info','information','skip','footer','title','fst','next','inline']):
                    par_text = par.text.replace('\n',' ').strip()
                    undesirables.append(par_text)

            work = [x for x in paragraphs if x not in undesirables]
            if work:
                cleaner_marxist_text = text_splitter(work, cleaner_marxist_text)
                with open(f'{path+filename}.txt', 'w') as f:
                    f.writelines(work)
                
                logging.info(f'Text from {contents_url} successfully downloaded into "{path+filename}.txt".')
                counter += 1  
        
    logging.info(f'{counter} works downloaded into the folder "{path}".')
    
    return cleaner_marxist_text
    

def text_cleaner(paragraphs_list):
    '''takes the final LIST of marxist text chunks and cleans it with RegEx.'''
    
    logging.info('Final cleaning starts now...')
    regex = {r"\\'":"’",
        r'\[.+?\]':'',
        r'  [0-9]+.':'',
        r'\(\?\)':'',
        r'\([0-9]{1,2}\)':'',
        r'[<>]':'',
        r'\.+':'.',
        r' \. ':'. ',
        r'\|\|[A-Z]+\|':'',
        r' {2,}':' '}
    
    for key,index in regex.items():
        paragraphs_list = [f"{re.sub(key,index,par)} " for par in tqdm(paragraphs_list)]
        
    logging.info('All cleaning done.')
    return paragraphs_list
    

def marxist_txt(clean_chunks):
    '''creates the final TXT file to be used as a training dataset for the gpt2 model'''
    
    other_path = 'training_dataset/preprocessed/'
    if not os.path.exists(other_path):
        os.makedirs(other_path)
        
    count = 0
    for el in clean_chunks:
        count = count + len(el)
    
    logging.info(f'The training dataset has {len(clean_chunks)} chunks of text:\nThey are all shorter than 1024 characters; the training dataset is {count} characters long in total.')
    

    with open(f'{other_path}marx.txt', 'w') as f:
                    f.writelines(clean_chunks)
    
    logging.info(f'A TXT file containing the training dataset may now be found into the folder "{other_path}".')
    
if __name__=='__main__':

    logging.info('Starting the scraping from the "Marx Engels Archive"')
    final_bits = text_cleaner(get_marxist_text(marxist_works))
    marxist_txt(final_bits)


