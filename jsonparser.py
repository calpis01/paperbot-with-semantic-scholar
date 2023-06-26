import numpy as np
import requests
import re
import pickle
import os
from datetime import datetime 
import time
import calendar
import argparse
import pathlib
import os
# import pdb # for debug

#-------------------[HEADER] USER DEFINED PARAMETERS START-----------------------------------
# Slack API url to your channel. Modify here!
slack_url = ''

# SemanticScholar API url for searching
ss_url = 'http://api.semanticscholar.org/graph/v1/paper/search?'
#API_key = 'sjTQHQoGMQ1XLIWZKctN65uxxXakd78w1h0elXon'

# Number of papers to be displayed per search
Npapers_to_display = 1
Nclassic_to_display = 1

# Nuber of papers that are analyzed per a loop
Npapers_batch_size = 100 # max 100

# information to be acquired
fields = ('authors', 'paperId', 'externalIds', 'url', 'title', 'abstract', 'venue', 'year', \
          'referenceCount', 'citationCount', 'influentialCitationCount', \
          'isOpenAccess', 'fieldsOfStudy', )

# query for latest papers on daily basis
query_list = ('spherical+camera+estimation')

# query for classic papers, one will be randomly chosen
classic_query_list = ('neuroscience',
                      'machine+learning')
ifClassic = True

# year range will be randomly chosen from here
range_classic = np.arange(1935, 2025, 10)

# The time when you want the result (under the periodic execution mode)
posting_hour = 7

# If you have kid(s), shouldn't work on weekends perhaps
day_off = ('Tuesday', 'Thursday', 'Saturday', 'Sunday')

#------------------[HEADER] USER DEFINED PARAMETERS END------------------------------------


def generate_ss_url(ss_url_, query_, fields_, batch_size_, start_):

    # Compile Semantic Scholar API url
    fullfields = ''
    for targfield in fields_:
        fullfields += targfield + ','
        
    return ss_url_ + 'query={}&fields={}&limit={}&offset={}'.format(
                query_, fullfields[:-1], batch_size_, start_)
        

def entry_splitter(data_):
    
    # Split the returned entry into papers
    pattern = '(\"paperId[\s\S]*?}]})'
    return re.findall(pattern, data_)

def entry_parser(data_, fields_):

    # Parse the paper text data into subfields
    datapool = []
    for targentry in data_:
        strpool = []

        for targfield in fields_:
            if 'externalids' in targfield.lower():
                pattern = '\"' + targfield + '\": ({[\s\S]*?})'
            elif 'authors' in targfield.lower() or 'fieldsofstudy' in targfield.lower():
                pattern = '\"' + targfield + '\": \[([\s\S]*?)\]'
            elif 'title' in targfield.lower() or 'abstract' in targfield.lower():
                pattern = '\"' + targfield + '\": \"([\s\S]*?)\"'
            else:
                pattern = '\"' + targfield + '\": ([\s\S]*?),'
                
            tmpstr = re.findall(pattern, targentry)
        
            if 'count' in targfield.lower() or 'year' in targfield.lower():
                if 'null' not in tmpstr[0]:
                    tmpstr = int(tmpstr[0])
            elif 'authors' in targfield.lower():
                pattern = '\"name\": \"([\s\S]*?)\"'
                tmpstr = re.findall(pattern, targentry)
                tmpstr2 = ''
                for targ in tmpstr:
                    tmpstr2 += targ + ', '
                tmpstr = tmpstr2[:-2]
            else:
                if not tmpstr:
                    tmpstr = 'none'
                else:
                    tmpstr = tmpstr[0].replace('"', '').strip('[').strip(']')

            strpool.append(tmpstr)
        datapool.append(strpool)
    return np.array(datapool)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='This is a Semantic Scholar crawler that search papers with custom keywords.')
    parser.add_argument('-q', '--query', nargs='*')
    parser.add_argument('-N', '--Npapers', type=int, default=1)
    parser.add_argument('-o', '--once', action='store_true')
    parser.add_argument('--obsidian', default='/mnt/c/Users/takuo/OneDrive/ドキュメント/Obsidian Vault/paperbank/', help='where is your Obsidian root.')
    parser.add_argument('--name', default='sema', help='your Slack webhook URL.')
    args = parser.parse_args()