'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Download daily Arxiv papers
Date: 2022-07-15 16:41:41
LastEditTime: 2023-01-09 16:36:37
Author: Aiden Li
'''

import argparse
import json
import os
import sched
import shutil
from sched import scheduler
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from utils.notion import NotionLogger
from utils.utils import ArxivDownloader, Subscription
from datetime import datetime
from utils.s3 import S3Uploader
from utils.utils import get_yaml_data

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--max_amount", type=str, default=None)
    parser.add_argument("--sub_path", type=str, default="data/subs.json")
    parser.add_argument("--notion_cred_path", type=str, default="credentials/notion.json")
    parser.add_argument("--feeds_dir", type=str, default="feeds")
    parser.add_argument("--odf_dir", type=str, default="pdf")
    parser.add_argument("--logdir", type=str, default="logs")
    parser.add_argument("--credentials_path", type=str, default="credentials/credentials.yaml")
    parser.add_argument("--notion", action='store_true')
    parser.add_argument("--s3", action='store_true')
    parser.add_argument("--s3_bucket", type=str, default="my-assets")
    parser.add_argument("--s3_remote_dir", type=str, default="arxiv-daily")
    parser.add_argument("--s3_endpoint", type=str, default=None)
    parser.add_argument("--s3_baseurl", type=str, default=None)
    
    return parser.parse_args()

def init(args):
    # TODO: Complete logging logics
    os.makedirs(args.feeds_dir, exist_ok=True)
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=f'{args.logdir}/run-{ str(datetime.now().timestamp()) }.log', format=LOG_FORMAT)
    
def run(args):
    cred = get_yaml_data(args.credentials_path)
    subscriptions = json.load(open(args.sub_path, 'r'))['subs']
    subs = [
        Subscription(cat, subcat, keywords)
        for [cat, subcat, keywords] in subscriptions
    ]
    downloader = ArxivDownloader(subs)
    notion_paper_entries, zip_pairs = downloader.fetch_papers(get_notion_entries=args.notion, get_zip_pairs=True, max_amount=args.max_amount)
    
    if args.s3:
        paths = []
        notion_archive_entries = []
        os.makedirs("dispatch", exist_ok=True)
        for [folder, filename_noext] in zip_pairs:
            archive_path = os.path.join("dispatch", filename_noext)
            shutil.make_archive(archive_path, 'zip', folder)
            paths.append(f"{archive_path}.zip")
        
        # If not specified (passing None), boto3 will look for credentials in ~/.aws/credentials
        s3_cred = cred['s3']
        s3_uploader = S3Uploader(args.s3_bucket, args.s3_remote_dir, s3_cred['aws_access_key_id'], s3_cred['aws_secret_access_key'], args.s3_baseurl, args.s3_endpoint)
        for i, archive_path in enumerate(paths):
            object_url = s3_uploader.upload(archive_path)
            if args.notion:
                notion_archive_entries.append({
                    "filename": os.path.basename(archive_path),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "size": round(os.path.getsize(archive_path) / (2**20), 2),
                    "cat": f"{subscriptions[i][0]}.{subscriptions[i][1]}"
                })
            logging.info(f"Uploaded {archive_path} to S3: {object_url}")
        
    # TODO: Fix bugs
    # if args.notion:
    #     notion_cred = cred['notion']
    #     if 'archive_dbid' in notion_cred:
    #         notion_logger = NotionLogger(notion_cred['token'], notion_cred['paper_list_dbid'], notion_cred['archive_dbid'])
    #     else:
    #         notion_logger = NotionLogger(notion_cred['token'], notion_cred['paper_list_dbid'])
            
    #     for entry in notion_paper_entries:
    #         notion_logger.post_paper(entry)
    #     if args.s3:
    #         for entry in notion_archive_entries:
    #             notion_logger.post_archive(entry)
            
if __name__ == '__main__':
    args = get_args()
    init(args)
    
    # Test run
    run(args)
    
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run, 'cron', hour = 8,
        args=[args]
    )
    
    # scheduler.start()
