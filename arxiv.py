'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Arxiv Manager
Date: 2022-07-15 16:46:22
LastEditTime: 2022-07-15 17:47:45
Author: Aiden Li
'''

import json
import os
import sqlite3
from datetime import datetime

import arxiv_downloader
import feedparser
from tqdm import tqdm
import requests

def connect_db(db_name):
    db = sqlite3.connect(db_name)
    db.cursor().execute('CREATE TABLE IF NOT EXISTS arxiv_id (id INTEGER PRIMARY KEY, arxiv_id TEXT, title TEXT)')
    db.commit()
    return db

class Subscription:
    def __init__(self, cat, subcat, keywords):
        self.cat = cat
        self.subcat = subcat
        self.keywords = keywords

class Arxiv:
    def __init__(self, subs: list(Subscription), feeds_basedir="feeds", pdfs_basedir="pdf", db_name="arxiv.db"):
        self.subs = subs
        self.feeds_basedir = feeds_basedir
        self.pdfs_basedir = pdfs_basedir
        self.timetag = datetime.now().strftime("%Y/%m-%d")
        self.db = connect_db(db_name)

    def db_add_article(self, id, title):
        # TODO: Anti-Injection
        
        # Check whether collided
        get_all_query = 'SELECT ids FROM arxiv_id'
        for (ids,) in self.db.cursor().execute(get_all_query).fetchall():
            if ids is not None and id in ids:
                return False
            
        # No collision, insert
        add_script = "INSERT INTO arxiv_id, title (arxiv_id, title) VALUES (%s, %s)" % (id, title,)
        self.db.cursor().execute(add_script)
        self.db.commit()
        
        return True
        
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
            if keyword not in entry['title']:
                return False
        return True
    
    def append_keywords(self, keywords: list):
        self.keywords += keywords

    def remove_keywords(self, keywords: list):
        self.keywords = [keyword for keyword in self.keywords if keyword not in keywords]
    
    def feeds_local_path(self, sub: Subscription, filename: str, mkdir=True):
        path = os.path.join(self.feeds_basedir, sub.cat, sub.subcat, self.timetag)
        if mkdir:
            os.makedirs(path, exist_ok=True)
        return os.path.join(path, filename)
    
    def build_paper_pdf_path(self, sub: Subscription, id: str, mkdir=True):
        path = os.path.join(self.pdfs_basedir, sub.cat, sub.subcat, self.timetag, )
        if mkdir:
            os.makedirs(path, exist_ok=True)
        return os.path.join(path, f"{id}.pdf")
    
    def fetch_papers(self):
        self.timetag = datetime.now().strftime("%Y/%m-%d")
        for sub in self.subs:
            tqdm.write(f"Loading paper list from {sub.cat}:{sub.subcat} with keywords: {sub.keywords}")
            feeds = feedparser.parse(Arxiv.build_rss_url(sub))
            json.dump(feeds, open(self.feeds_local_path(sub, "raw.json"), "w"))
            
            entries = feeds['entries']
            targets = []
            succ = []
            for entry in entries:
                if self.entry_filter(entry):
                    arxiv_id = Arxiv.parse_id(entry['id'])
                    colli = self.db_add_article(arxiv_id, entry['title'])
                    if colli:
                        break
                    
                    targets.append(entry)
                    link = self.build_paper_pdf_url(arxiv_id)
                    try:
                        open(self.build_paper_pdf_path(sub), 'wb').write(requests.get(link).content)
                        succ.append(True)
                    except:
                        succ.append(False)
                    
            json.dump({ "targets": targets, "succ": succ }, open(self.feeds_local_path(sub, "target.json"), "w"))
