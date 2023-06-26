#!/usr/bin/env python3
import openai
import numpy as np
import configparser
import requests
import re
import argparse
import pathlib
import os
import json
import operator
config = configparser.ConfigParser()
config.read('.config')


openai.api_key = config.get('open_api_key', 'key')
ss_url = 'http://api.semanticscholar.org/graph/v1/paper/search?'
# QUERY PARAMETERS(https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/post_graph_get_papers)
fields = (
    'paperId', 'title', 'venue','authors', 'abstract', 'year', 'externalIds', 'influentialCitationCount',
    'citationCount', 'publicationDate', 'isOpenAccess', 'openAccessPdf', 'fieldsOfStudy'
)

query_list = ('spherical+camera+estimation')

# year range will be randomly chosen from here
# range_classic = np.arange(1990, 2025, 10)


def summarize_paper(paper):
    system = """
    論文を以下の制約に従って要約して出力してください。

    [制約]
    タイトルは日本語で書く
    要点は3つにまとめる


    [出力]
    タイトルの日本語訳

    ・要点1
    ・要点2
    ・要点3
    """

    text = f"title: {paper['title']}\nbody: {paper['abstract']}"
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': text}
                ],
                temperature=0.2,
            )

    summary = response['choices'][0]['message']['content']
    message = f"発行日: {paper['publicationDate']}\n{paper['title']}\n{summary}\n"
    return message

def generate_url(ss_url_, query_list_, fields_, limit_, offset_):
    all_fields = ''
    for field in fields_:
        all_fields += field + ','
    url = ss_url_ + 'query=' + query_list_ + '&fields=' + all_fields[:-1] + '&limit=' + str(limit_) + '&offset=' + str(offset_)
    return url

def get_sorted_papers_data(url_, sort_key_):
    textdata = requests.Session().get(url_).text
    json_papers_data = json.loads(textdata)
    sorted_data_ = sorted(json_papers_data['data'], key=lambda x: x[sort_key_], reverse=True)
    return sorted_data_


if __name__ == "__main__":
    limit = 5
    sema_url = generate_url(ss_url, query_list, fields, limit, 0)
    sorted_data = get_sorted_papers_data(sema_url, 'citationCount')
    for d in sorted_data:
        print(d['title']+"\n", d['citationCount'], "\n", d['publicationDate'])
        #print(d)
        if d['isOpenAccess'] == True:
            print(d['openAccessPdf']['url'])
        #print(summarize_paper(d))
        
    
    #for i in range(0,limit):
    #   print(data["data"][i]["title"], data["data"][i]["citationCount"], data["data"][i]["influentialCitationCount"])
        
    #papers = split_papers(textdata)
    #info = get_paper_info(papers, fields)
    #print(info)

    #print(len(papers))