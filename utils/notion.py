'''
Author: Aiden Li
Date: 2022-07-15 23:39:24
LastEditors: Aiden Li (i@aidenli.net)
LastEditTime: 2022-07-16 00:43:41
Description: Log to Notion
'''
import requests
from datetime import datetime

class NotionLogger:
    def __init__(self, intergration_token, database_id):
        self.base_url_notion_pages = "https://api.notion.com/v1/pages"
        self.base_url_notion_db = "https://api.notion.com/v1/databases"

        self.intergration_token = intergration_token
        self.database_id = database_id
        
    def post_paper(self, entry):
        headers = {
            'Notion-Version': '2021-05-13',
            'Authorization': 'Bearer ' + self.intergration_token,
        }

        body = {
            "parent": {
                "type": "database_id",
                "database_id": self.database_id
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
                "Check": {
                    "type": "checkbox",
                    "checkbox": False
                }
            },
            "paragraph": {
                "text": entry['abstract']
            }
        }

        try:
            requests.post(f"{ self.base_url_notion_db }", headers=headers, json=body)
        except:
            print(f"Failed to update Notion page for {entry['arxiv_id']}")