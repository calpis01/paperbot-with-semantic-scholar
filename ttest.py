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
from urllib.request import Request, urlopen
from datetime import datetime

config = configparser.ConfigParser()
config.read('.config')

webhook_url = config.get('discord_webhook', 'url')
openai.api_key = os.getenv("OPENAI_API_KEY")
ss_url = 'http://api.semanticscholar.org/graph/v1/paper/search?'
# QUERY PARAMETERS(https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/post_graph_get_papers)
fields = (
    'paperId', 'title','url',  'venue','authors', 'abstract', 'year', 'externalIds', 'influentialCitationCount',
    'citationCount', 'publicationDate', 'isOpenAccess', 'openAccessPdf', 'fieldsOfStudy', 'publicationVenue', 'tldr', 's2FieldsOfStudy'
)

query_list = ('indoor scene')

limit = 100 #queryで検索をかけた際に返ってくる論文の数（期間はランダムだと思われ）
# year range will be randomly chosen from here
# range_classic = np.arange(1990, 2025, 10)


def summarize_paper(paper):
    system = """
    論文を以下の制約に従って要約して出力してください。

    [制約]
    タイトルは日本語で書く
    要点は3つにまとめる
    目的と結果の比較をする

    [出力]
    タイトルの日本語訳
    目的：この論文が属している研究範囲とその背景を踏まえた，この論文の目的を表示
    使用カメラ：単眼かステレオか，その理由を表示
    ・要点1
    ・要点2
    ・要点3
    結果：論文の結果を表示，目的に即した結果がでているかを確認
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
    filtered_data = [paper for paper in json_papers_data['data'] if paper.get(sort_key_) is not None]
    sorted_data_ = sorted(filtered_data, key=lambda x: x[sort_key_], reverse=True)
    return sorted_data_

def post_discord(message: str, webhook_url: str):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (private use) Python-urllib/3.10",
    }
    data = {"content": message}
    request = Request(
        webhook_url,
        data=json.dumps(data).encode(),
        headers=headers,
    )

    with urlopen(request) as res:
        assert res.getcode() == 204

if __name__ == "__main__":
    sema_url = generate_url(ss_url, query_list, fields, limit, 0)
    sorted_data = get_sorted_papers_data(sema_url, 'publicationDate')
    for d in sorted_data[0:10]:
        #fields_of_study_str = ', '.join(d['fieldsOfStudy']) if d['fieldsOfStudy'] else 'N/A'

        contents = f"タイトル: {d['title']}\n引用数: {d['citationCount']}\n発行日: {d['publicationDate']}\n カテゴリ1 {d['fieldsOfStudy']}\n venue: {d['publicationVenue']['name'], d['publicationVenue']['']}\nss_url: {d['url']}\n"
        print(contents)
        if d['isOpenAccess'] == True:
            contents += f"open_accesss_url: {d['openAccessPdf']['url']}\n"
            print(contents)
        #post_discord(contents, webhook_url)
        #print(d)
        #print(summarize_paper(d))