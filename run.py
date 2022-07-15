'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Download daily Arxiv papers
Date: 2022-07-15 16:41:41
LastEditTime: 2022-07-15 23:41:29
Author: Aiden Li
'''

import json
from sched import scheduler
import sched

from utils.utils import Subscription, Arxiv
from apscheduler.schedulers.blocking import BlockingScheduler

import argparse

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--sub_path", type=str, default="data/subs.json")
    parser.add_argument("--notion", type=bool, default=False)
    parser.add_argument("--gdrive", type=bool, default=False)
    
    return parser.parse_args()

def run(sub_path, notion=False, GDrive=False):
    subscriptions = json.load(open(sub_path, 'r'))['subs']
    subs = [
        Subscription(cat, subcat, keywords)
        for [cat, subcat, keywords] in subscriptions
    ]
    server = Arxiv(subs)
    server.fetch_papers()
    
    if notion:
        server.log_to_notion()
    if gdrive:
        server.upload_to_gdrive()

if __name__ == '__main__':
    args = get_args()
    # Test run
    # run(sub_path)
    
    # Runs at 6 AM every day
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run, 'cron', hour=6,
        args=[
            args.sub_path, args.notion, args.gdrive
        ]
    )
    
    scheduler.start()
