'''
LastEditors: Aiden Li (i@aidenli.net)
Description: Download daily Arxiv papers
Date: 2022-07-15 16:41:41
LastEditTime: 2022-07-15 16:49:57
Author: Aiden Li
'''

from tqdm import tqdm, trange

from arxiv import Subscription, Arxiv

subscriptions = [
    [
        'cs', 'CV',
        [ "Human", "Object", "Point Cloud", "Grasp", "Pose", "NeRF" ]
    ],
    [
        'cs', 'RO',
        [ "Object", "Grasp", "Pose" ]
    ],
]

subs = [
    Subscription(cat, subcat, keywords) for idx, [cat, subcat, keywords] in tqdm(enumerate(subscriptions)) 
]
    
    
