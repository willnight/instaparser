import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstagramPost
from instaparser.items import InstagramProfile
from instaparser.items import InstagramComments
from instaparser.items import InstagramUserRelations
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from datetime import datetime


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    scrapped_data = 'posts'  # ['user_bio', 'posts', 'followers', 'subscribers']
    insta_login = 'mayacorn3'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:9:1625926725:AVdQAKP1F93CZEKa3WG22s3mGiSZpHUaFnROC61yamjmwztGpuN/4htGj5e0RXDCAIn8J075u4R5L9/arHWME2CIyZTmdjju0SRKfgvflvCUOBaOjCwkFQl6olhMxixhihGsdfKPZdjLYho6XOvZhAsfCQ=='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    users_to_parse = ['aprilfiit', 'st_bakay', 'kolayuk']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'ea4baf885b60cbf664b34ee760397549'
    comments_hash = 'afa640b520008fccd187e72cd59b5283'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        callback_method = ''
        if self.scrapped_data == 'user_bio':
            callback_method = self.user_profile_parse
        elif self.scrapped_data == 'subscribers':
            callback_method = self.user_subscribers_parse
        elif self.scrapped_data == 'followers':
            callback_method = self.user_followers_parse
        elif self.scrapped_data == 'posts':
            callback_method = self.user_posts_parse

        if j_body['authenticated']:
            for user in self.users_to_parse:
                yield response.follow(
                    f'/{user}',
                    callback=callback_method,
                    cb_kwargs={'username': user}
                )

    # подробности аккаунтов

    def user_profile_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id}
        # url_profile_details = f'/{username}/?__a=1&{urlencode(variables)}'
        url_profile_details = f'https://i.instagram.com/api/v1/users/{user_id}/info/'

        yield response.follow(
            url_profile_details,
            callback=self.user_profile_details_parse,
            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )

    def user_profile_details_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        user_info = j_data.get('user')
        item = InstagramProfile(
                user_id=user_id,
                photo=user_info.get('hd_profile_pic_url_info').get('url'),
                user_profile=username,
                full_name=user_info.get('full_name'),
                profile_description=user_info.get('biography'),
                is_verified=user_info.get('is_verified'),
                category=user_info.get('category'),
                is_business=user_info.get('is_business'),
                is_private=user_info.get('is_private'),
                public_email=user_info.get('public_email'),
                city_name=user_info.get('city_name'),
                created='',
                updated=datetime.now()
        )
        yield item  # В пайплайн

    # сбор подписок юзеров

    def user_followers_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id}
        url_subscribers = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12&{urlencode(variables)}'
        print(url_subscribers)
        yield response.follow(
            url_subscribers,
            callback=self.user_followers_users_parse,
            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )

    def user_followers_users_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)

        if j_data.get('next_max_id'):
            variables['max_id'] = j_data.get('next_max_id')
            url_subscribers = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12&{urlencode(variables)}'
            yield response.follow(
                url_subscribers,
                callback=self.user_followers_users_parse,
                headers={'User-Agent': 'Instagram 64.0.0.14.96'},
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        print(f'user {username} id {user_id} max_id {j_data.get("next_max_id")}')
        users = j_data.get('users')
        for user in users:
            item = InstagramUserRelations(
                user_id_to=user['pk'],
                user_name_to=user['username'],
                user_id_from=user_id,
                user_name_from=username,
                relation_type='follower',
                photo=user.get('profile_pic_url'),
                updated=datetime.now()
            )
            yield item

    # сбор подписчиков юзеров

    def user_subscribers_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id}
        url_subscribers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&{urlencode(variables)}'
        yield response.follow(
            url_subscribers,
            callback=self.user_subscribers_users_parse,
            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )

    def user_subscribers_users_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)

        if j_data.get('next_max_id'):
            variables['max_id'] = j_data.get('next_max_id')
            url_subscribers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&{urlencode(variables)}'
            yield response.follow(
                url_subscribers,
                callback=self.user_subscribers_users_parse,
                headers={'User-Agent': 'Instagram 64.0.0.14.96'},
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        print(f'user {username} id {user_id} max_id {j_data.get("next_max_id")}')
        users = j_data.get('users')
        for user in users:
            item = InstagramUserRelations(
                user_id_from=user['pk'],
                user_name_from=user['username'],
                user_id_to=user_id,
                user_name_to=username,
                relation_type='subscriber',
                photo=user.get('profile_pic_url'),
                updated=datetime.now()
            )
            yield item

    # сбор постов и комментов

    def user_posts_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 12}
        url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
        yield response.follow(
            url_posts,
            callback=self.user_posts_details_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )

    def user_posts_details_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_details_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        variables_comm = {'shortcode': ''}
        for post in posts:
            # variables_comm['shortcode'] = post.get('node').get('shortcode')
            # variables_comm['child_comment_count'] = 5
            # variables_comm['fetch_comment_count'] = 40

            vars = '{%22shortcode%22%3A%22' + post.get('node').get('shortcode') + '%22%2C%22child_comment_count%22%3A3%2C%22fetch_comment_count%22%3A20}'
            url_post = f'{self.graphql_url}query_hash={self.comments_hash}&variables={vars}'

            yield scrapy.Request(
                url_post,
                callback=self.one_posts_details_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables_comm)}
            )

    def one_posts_details_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        post = j_data.get('data').get('shortcode_media')
        comments = j_data.get('data').get('shortcode_media').get('edge_media_to_comment').get('edges')
        item = InstagramPost(
            user_id=user_id,
            resource_url=post.get('display_url'),
            resource_type=post.get('__typename'),
            user_profile=username,
            is_video=post.get('is_video'),
            shortcode=post.get('shortcode'),
            description=post.get('edge_media_to_caption').get('edges')[0].get('node').get('text'),
            post_id=post.get('id'),
            comments=post.get('edge_media_to_comment').get('edges'),
            likes=post.get('edge_media_preview_like').get('count'),
            date=datetime.fromtimestamp(post.get('taken_at_timestamp')),
            updated=datetime.now()
        )
        yield item

        for comment in comments:
            item = InstagramComments(
                comment_id=comment.get('node').get('id'),
                resource_id=post.get('shortcode'),
                comment=comment.get('node').get('text'),
                author_profile=comment.get('node').get('owner').get('username'),
                author_id=comment.get('node').get('owner').get('id'),
                date=datetime.fromtimestamp(comment.get('node').get('created_at')),
                updated=datetime.now()
            )
            yield item


    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
