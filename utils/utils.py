'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Arxiv Manager
Date: 2022-07-15 16:46:22
LastEditTime: 2022-07-16 00:35:22
Author: Aiden Li
'''

import json
import os
import sqlite3
from datetime import datetime
import threading

import feedparser
from tqdm import tqdm
import utils.utils as utils
import requests


def connect_db(db_name):
    db = sqlite3.connect(db_name)
    db.cursor().execute(
        'CREATE TABLE IF NOT EXISTS papers (id INTEGER PRIMARY KEY, arxiv_id TEXT, title TEXT)'
    )
    db.commit()
    return db

# Thanks to https://github.com/Tachyu/Arxiv-download
def Handler(start, end, url, filename):
    # specify the starting and ending of the file
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    # request the specified part and get into variable
    r = requests.get(url, headers=headers, stream=True)
    # open the file and write the content of the html page
    # into file.
    with open(filename, "r+b") as fp:
        fp.seek(start)
        var = fp.tell()
        fp.write(r.content)

def download_file(url_of_file, name, number_of_threads):
    r = requests.head(url_of_file)
    if name:
        file_name = name
    else:
        file_name = url_of_file.split('/')[-1]
    try:
        file_size = int(r.headers['content-length'])
    except:
        print("Invalid URL")
        return

    part = int(file_size) / number_of_threads
    fp = open(file_name, "wb")
    # fp.write('\0' * file_size)
    fp.close()
    for i in range(number_of_threads):
        start = int(part * i)
        end = int(start + part)
        # create a Thread with start and end locations
        t = threading.Thread(target=Handler,
                             kwargs={
                                 'start': start,
                                 'end': end,
                                 'url': url_of_file,
                                 'filename': file_name
                             })
        t.setDaemon(True)
        t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()


class Subscription:

    def __init__(self, cat, subcat, keywords):
        self.cat = cat
        self.subcat = subcat
        self.keywords = [str.lower(kw) for kw in keywords]

    def append_keywords(self, keywords: list):
        self.keywords += [str.lower(kw) for kw in keywords]

    def remove_keywords(self, keywords: list):
        kws = [str.lower(kw) for kw in keywords]
        self.keywords = [
            keyword for keyword in self.keywords if keyword not in kws
        ]


class ArxivDownloader:

    def __init__(self,
                 subs,
                 feeds_basedir="feeds",
                 pdfs_basedir="pdf",
                 db_name="data/arxiv.db"):
        self.subs = subs
        self.feeds_basedir = feeds_basedir
        self.pdfs_basedir = pdfs_basedir
        self.timetag = datetime.now().strftime("%Y/%m-%d")
        self.db = connect_db(db_name)

    def db_check_article(self, id):
        # TODO: Anti-Injection
        # TODO: Beter database IO
        get_all_query = 'SELECT arxiv_id FROM papers'
        for (ids, ) in self.db.cursor().execute(get_all_query).fetchall():
            if ids is not None and id in ids:
                return True
        return False

    def db_add_article(self, id, title):
        # TODO: Anti-Injection
        # TODO: Beter database IO
        add_script = "INSERT INTO papers (arxiv_id, title) VALUES ('%s', '%s')" % (
            id,
            title,
        )
        self.db.cursor().execute(add_script)
        self.db.commit()

    @staticmethod
    def build_rss_url(sub: Subscription):
        return f"https://arxiv.org/rss/{sub.cat}.{sub.subcat}"

    @staticmethod
    def build_paper_pdf_url(id: str):
        return f"https://arxiv.org/pdf/{ id }.pdf"

    @staticmethod
    def parse_id(id: str):
        return id.split('/')[-1]

    def entry_filter(self, entry: dict):
        for keyword in self.keywords:
            if keyword in str.lower(entry['title']):
                return True
        return False

    def feeds_local_path(self, sub: Subscription, filename: str, mkdir=True):
        path = os.path.join(self.feeds_basedir, sub.cat, sub.subcat,
                            self.timetag)
        if mkdir:
            os.makedirs(path, exist_ok=True)
        return os.path.join(path, filename)

    def build_paper_pdf_path(self, sub: Subscription, title: str, mkdir=True):
        path = os.path.join(
            self.pdfs_basedir,
            sub.cat,
            sub.subcat,
            self.timetag,
        )
        if mkdir:
            os.makedirs(path, exist_ok=True)
        title = str.lower(title)
        title = title.replace(' ', '-').replace(':', '-').replace('?', '-')
        title = title.replace('/', '-').replace('\\', '-').replace('|', '-')
        title = title.replace('"', '-').replace('*', '-')
        title = title.replace('<', '-').replace('>', '-')
        return os.path.join(path, f"{title}.pdf")

    def fetch_papers(self, get_notion_entries=False):
        self.timetag = datetime.now().strftime("%Y/%m-%d")
        
        if get_notion_entries:
            notion_entries = []
            
        for sub in self.subs:
            tqdm.write(
                f"Loading paper list from {sub.cat}:{sub.subcat} with keywords: {sub.keywords}"
            )
            feeds = feedparser.parse(ArxivDownloader.build_rss_url(sub))
            json.dump(feeds, open(self.feeds_local_path(sub, "raw.json"), "w"))

            entries = feeds['entries']
            targets = []
            succ = []
            for entry in entries:
                self.keywords = sub.keywords
                if self.entry_filter(entry):
                    arxiv_id = ArxivDownloader.parse_id(entry['id'])
                    if self.db_check_article(arxiv_id):
                        continue

                    targets.append(entry)
                    link = self.build_paper_pdf_url(arxiv_id)
                    try:
                        pdf_path = self.build_paper_pdf_path(sub, entry['title'])
                        download_file(link, pdf_path, 16)
                        self.db_add_article(arxiv_id, entry['title'])
                        print(f"Downloaded arxiv {arxiv_id} Title: {entry['title']}")
                        notion_entries.append(self.parse_notion_entry(
                            sub, entry['title'], arxiv_id, entry['summary'][3:-4]
                        ))
                        succ.append(True)
                    except:
                        succ.append(False)

            json.dump({
                "targets": targets,
                "succ": succ
            }, open(self.feeds_local_path(sub, "target.json"), "w"))
            
            if get_notion_entries:
                return notion_entries
            
            # TODO: Log to Notion

    def parse_notion_entry(self, sub, title, arxiv_id, abstract):
        return {
            'arxiv_id': arxiv_id,
            'title': title,
            'cat': f"{sub.cat}.{sub.subcat}",
            'abstract': abstract
        }