import logging
import requests

logger = logging.getLogger(__name__)

API_VERSION='v0'

ITEM_INFO_API=f'https://hacker-news.firebaseio.com/{API_VERSION}/item/%d.json'
MAX_ITEM_API=f'https://hacker-news.firebaseio.com/{API_VERSION}/maxitem.json'

def get_item_info(item_id):
    logger.info(f'get item info with id ${item_id}')
    res = requests.get(ITEM_INFO_API % item_id)
    if res.ok:
        return res.json()
    else:
        raise Exception(f'{item_id} item info request fail!')
    
def get_maxitem_num():
    res = requests.get(MAX_ITEM_API)
    if res.ok:
        return res.json()
    else:
        raise Exception('max item num request fail!')
    
