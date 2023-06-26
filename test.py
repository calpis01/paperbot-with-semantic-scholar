#!/usr/bin/env python3
import openai
import configparser
import arxiv
import random
import argparse
import pathlib
import os
def post_obsidian(message, file_path, file_name):
    dout = pathlib.Path(file_path)
    filename = '{}.md'.format(file_name)
    mdfile_path = os.path.join(dout, filename)

    with open(mdfile_path, 'at') as f:
        f.write(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='--paper_id is arxiv paper id')
    parser.add_argument('--obsidian', default='/mnt/c/Users/takuo/OneDrive/ドキュメント/Obsidian Vault/paperbank/', help='where is your Obsidian root.')
    args = parser.parse_args()
    message = str(args.obsidian) +'\n'*3
    file_path = args.obsidian
    file_name = "test"
    post_obsidian(message, file_path, file_name)