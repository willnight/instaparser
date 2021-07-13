from pprint import pprint

import pymongo
import scrapy
from scrapy.pipelines.images import ImagesPipeline

from instaparser.items import InstagramComments
from instaparser.items import InstagramPost
from instaparser.items import InstagramProfile
from instaparser.items import InstagramUserRelations


class InstaparserPipeline:
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        self.mongodb = client['instagram_db']

    def process_item(self, item, spider):
        if isinstance(item, InstagramProfile):
            collection_user = self.mongodb['users']
            collection_user.find_and_modify({"user_id": item['user_id']}, {"$set": item}, upsert=True)
            return item
        elif isinstance(item, InstagramPost):
            collection_post = self.mongodb['posts']
            collection_post.find_and_modify({"post_id": item['post_id']}, {"$set": item}, upsert=True)
            return item
        elif isinstance(item, InstagramComments):
            collection_post = self.mongodb['comments']
            collection_post.find_and_modify({"comment_id": item['comment_id']}, {"$set": item}, upsert=True)
            return item
        elif isinstance(item, InstagramUserRelations):
            collection_post = self.mongodb['user_relations']
            collection_post.find_and_modify({"$and": [{"user_id_from": item['user_id_from']},
                                                      {"user_id_to": item['user_id_to']}]}, {"$set": item}, upsert=True)
            return item
        else:
            return None


class InstaparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if isinstance(item, InstagramPost):
            user_photo = item['resource_url']
            pprint(user_photo)
            try:
                yield scrapy.Request(user_photo)
            except TypeError as e:
                print(e)
        elif isinstance(item, InstagramUserRelations):
            user_photo = item['photo']
            pprint(user_photo)
            try:
                yield scrapy.Request(user_photo)
            except TypeError as e:
                print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        if isinstance(item, InstagramPost):
            user_name = item['user_profile']
            item_name = item['shortcode']
            return f'full/{user_name}/posts/{item_name}.jpg'
        elif isinstance(item, InstagramUserRelations):
            user_name = 'noname'
            item_name = 'noname'
            if item['relation_type'] == 'subscriber':
                user_name = item['user_name_to']
                item_name = item['user_name_from']
            elif item['relation_type'] == 'follower':
                user_name = item['user_name_from']
                item_name = item['user_name_to']

            return f'full/{user_name}/{item["relation_type"]}/{item_name}.jpg'
