'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Download daily Arxiv papers
Date: 2022-07-15 16:41:41
LastEditTime: 2022-07-16 05:35:14
Author: Aiden Li
'''

import argparse
import json
import os
import sched
import shutil
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
    
    parser.add_argument("--dispatch_dir", type=str, default=None)
    
    return parser.parse_args()

def init(args):
    os.makedirs(args.feeds_basedir, exist_ok=True)

def run(sub_path, notion=False, dispatch_dir=None):
    subscriptions = json.load(open(sub_path, 'r'))['subs']
    subs = [
        Subscription(cat, subcat, keywords)
        for [cat, subcat, keywords] in subscriptions
    ]
    downloader = ArxivDownloader(subs)
    notion_entries, zip_pairs = downloader.fetch_papers(get_notion_entries=notion, get_zip_pairs=True)
    
    if notion:
        notion_creds = json.load(open(args.notion_cred_path, 'r'))
        logger = NotionLogger(notion_creds['token'], notion_creds['db_id'])
        for entry in notion_entries:
            logger.post_paper(entry)
    if dispatch_dir is not None:
        try:
            os.makedirs("dispatch", exist_ok=True)
            os.makedirs(dispatch_dir, exist_ok=True)
            paths = []
            for [folder, filename_noext] in zip_pairs:
                archive_path = os.path.join("dispatch", filename_noext)
                paths.append(archive_path)
                shutil.make_archive(archive_path, 'zip', folder)
                shutil.move(f"{archive_path}.zip", os.path.join(dispatch_dir, f"{filename_noext}.zip"))
            
        except:
            print(f"Failed to dispatch the archive.")
            
if __name__ == '__main__':
    args = get_args()
    # Test run
    run(args.sub_path, args.notion, args.dispatch_dir)
    
    # Runs at 6 AM every day
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run, 'cron', hour=6,
        args=[
            args.sub_path, args.notion, args.dispatch_dir
        ]
    )
    
    scheduler.start()
