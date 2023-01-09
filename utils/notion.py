'''
Author: Aiden Li
Date: 2022-07-15 23:39:24
LastEditors: Aiden Li (i@aidenli.net)
LastEditTime: 2023-01-09 15:37:55
Description: Log to Notion
'''
import requests
from datetime import datetime

class NotionLogger:
    def __init__(self, intergration_token, paper_list_dbid, archive_dbid=None):
        self.base_url_notion_pages = "https://api.notion.com/v1/pages"
        self.base_url_notion_db = "https://api.notion.com/v1/databases"

        self.intergration_token = intergration_token
        self.paper_list_dbid = paper_list_dbid
        self.archive_dbid = archive_dbid
        
        self.headers = {
            'Notion-Version': '2022-06-28',
            'Authorization': 'Bearer ' + self.intergration_token,
        }
        
    def post_archive(self, entry):
        assert(self.archive_dbid is not None)
        body = {
            "parent": {
                "type": "database_id",
                "database_id": self.archive_dbid
            },
            "properties": {
                "File": {
                    "id": "title",
                    "type": "text",
                    "title": [{
                        "type": "text",
                        "text": {
                            "content": entry['filename']
                        },
                    }]
                },
                "Date": {
                    "type": "date",
                    "date": { "start": entry['date'] }
                },
                # "Size": {
                #     "type": "number",
                #     "number": entry['size']
                # },
                # "Category": {
                #     "type": "title",
                #     "title": [{
                #         "type": "text",
                #         "text": {
                #             "content": entry['cat']
                #         },
                #         "plain_text": entry['cat']
                #     }]
                # },
            },
        }
        
        try:
            requests.post(f"{ self.base_url_notion_db }", headers=self.headers, json=body)
        except:
            print(f"Failed to update Notion page for {entry['arxiv_id']}")
        
    def post_paper(self, entry):
        body = {
            "parent": {
                "type": "database_id",
                "database_id": self.paper_list_dbid
            },
            "properties": {
                "Arxiv ID": {
                    "id": "title",
                    "type": "title",
                    "title": [{
                        "type": "text",
                        "text": {
                            "content": entry['arxiv_id']
                        },
                        "plain_text": entry['arxiv_id']
                    }]
                },
                "Title": {
                    "type": "title",
                    "title": [{
                        "type": "text",
                        "text": {
                            "content": entry['title']
                        },
                        "plain_text": entry['title']
                    }]
                },
                "Date": {
                    "type": "date",
                    "date": { "start": entry['date'] }
                },
                "Category": {
                    "type": "title",
                    "title": [{
                        "type": "text",
                        "text": {
                            "content": entry['cat']
                        },
                        "plain_text": entry['cat']
                    }]
                },
            },
            "paragraph": {
                "text": entry['abstract']
            }
        }

        try:
            requests.post(f"{ self.base_url_notion_db }", headers=self.headers, json=body)
        except:
            print(f"Failed to update Notion page for {entry['arxiv_id']}")