'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Download daily Arxiv papers
Date: 2022-07-15 16:41:41
LastEditTime: 2022-07-16 00:37:54
Author: Aiden Li
'''

import argparse
import json
import os
import sched
from sched import scheduler

from apscheduler.schedulers.blocking import BlockingScheduler

from utils.notion import NotionLogger
from utils.utils import ArxivDownloader, Subscription


def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--sub_path", type=str, default="data/subs.json")
    parser.add_argument("--notion_cred_path", type=str, default="credentials/notion.json")
    parser.add_argument("--feeds_dir", type=str, default="feeds")
    parser.add_argument("--odf_dir", type=str, default="pdf")
    parser.add_argument("--notion", type=bool, default=True)
    parser.add_argument("--gdrive", type=bool, default=False)
    
    return parser.parse_args()

def init(args):
    os.makedirs(args.feeds_basedir, exist_ok=True)

def run(sub_path, notion=False, gdrive=False):
    subscriptions = json.load(open(sub_path, 'r'))['subs']
    subs = [
        Subscription(cat, subcat, keywords)
        for [cat, subcat, keywords] in subscriptions
    ]
    downloader = ArxivDownloader(subs)
    notion_entries = downloader.fetch_papers(get_notion_entries=notion)
    
    if notion:
        notion_creds = json.load(open(args.notion_cred_path, 'r'))
        logger = NotionLogger(notion_creds['token'], notion_creds['db_id'])
        for entry in notion_entries:
            logger.post_paper(entry)
    if gdrive:
        pass
    
if __name__ == '__main__':
    args = get_args()
    # Test run
    run(args.sub_path, args.notion, args.gdrive)
    
    # Runs at 6 AM every day
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run, 'cron', hour=6,
        args=[
            args.sub_path, args.notion, args.gdrive
        ]
    )
    
    scheduler.start()
