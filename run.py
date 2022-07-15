'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Download daily Arxiv papers
Date: 2022-07-15 16:41:41
LastEditTime: 2022-07-15 23:22:01
Author: Aiden Li
'''

import json
from sched import scheduler
import sched

from utils import Subscription, Arxiv
from apscheduler.schedulers.blocking import BlockingScheduler

import argparse

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--sub_path", type=str, default="data/subs.json")

def run(sub_path):
    subscriptions = json.load(open(sub_path, 'r'))['subs']
    subs = [
        Subscription(cat, subcat, keywords)
        for [cat, subcat, keywords] in subscriptions
    ]
    server = Arxiv(subs)
    server.fetch_papers()

if __name__ == '__main__':
    sub_path = "data/subs.json"
    
    # Test run
    # run(sub_path)
    
    # Runs at 6 AM every day
    scheduler = BlockingScheduler()
    scheduler.add_job(run, 'cron', hour=6, args=[sub_path])
    
    scheduler.start()
