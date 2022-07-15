'''
Author: Aiden Li
Date: 2022-07-15 23:39:24
LastEditors: Aiden Li (i@aidenli.net)
LastEditTime: 2022-07-15 23:39:35
Description: Log to Notion
'''
import requests
from datetime import datetime

class NotionLogger():

    def __init__(self, intergration_token):
        self.base_url_notion_pages = "https://api.notion.com/v1/pages"
        self.base_url_notion_db = "https://api.notion.com/v1/databases"

        self.intergration_token = intergration_token

    def post_wiki_backup_log(
        self,
        db_id: str,
        back_name: str,
        date: str,
        db_res: bool,
        data_res: bool,
        message: str,
        done=None,
    ):
        """
        Post a SNS Wiki backup log to SNS TechGr Notion Workspace.

        Args:
            back_name (str): [description]
            date (str): [description]
            db_res (bool): [description]
            data_res (bool): [description]
            message (str): [description]
        """
        if done is None:
            done = (db_res is True) and (data_res is True)

        if message is None:
            message = "No message left."

        headers = {
            'Notion-Version': '2021-05-13',
            'Authorization': 'Bearer ' + self.intergration_token,
        }

        body = {
            "parent": {
                "type": "database_id",
                "database_id": db_id
            },
            "properties": {
                "备份名称": {
                    "id":
                    "title",
                    "type":
                    "title",
                    "title": [{
                        "type": "text",
                        "text": {
                            "content": str(back_name)
                        },
                        "plain_text": str(back_name)
                    }]
                },
                "备份日期": {
                    "type": "date",
                    "date": {
                        "start": date,
                        "end": None
                    }
                },
                "数据库备份结果": {
                    "type": "select",
                    "select": {
                        "name": ["异常", "成功"][db_res is True]
                    }
                },
                "应用数据备份结果": {
                    "type": "select",
                    "select": {
                        "name": ["异常", "成功"][data_res is True]
                    }
                },
                "完成": {
                    "type": "checkbox",
                    "checkbox": done
                }
            },
            "paragraph": {
                "text": message
            }
        }

        log_res = requests.post(f"{ self.base_url_notion_pages }",
                                headers=headers,
                                json=body)

        return {log_res.status_code, log_res.text}
