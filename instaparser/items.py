import scrapy


class InstagramPost(scrapy.Item):
    user_id = scrapy.Field()
    post_id = scrapy.Field()
    shortcode = scrapy.Field()
    user_profile = scrapy.Field()
    resource_id = scrapy.Field()
    resource_url = scrapy.Field()
    resource_type = scrapy.Field()
    likes = scrapy.Field()
    comments = scrapy.Field()
    date = scrapy.Field()
    updated = scrapy.Field()
    is_video = scrapy.Field()
    description = scrapy.Field()


class InstagramProfile(scrapy.Item):
    user_id = scrapy.Field()
    photo = scrapy.Field()
    user_profile = scrapy.Field()
    full_name = scrapy.Field()
    profile_description = scrapy.Field()
    created = scrapy.Field()
    updated = scrapy.Field()
    is_verified = scrapy.Field()
    is_private = scrapy.Field()
    category = scrapy.Field()
    is_business = scrapy.Field()
    public_email = scrapy.Field()
    city_name = scrapy.Field()


class InstagramUserRelations(scrapy.Item):
    user_id_from = scrapy.Field()
    user_name_from = scrapy.Field()
    user_id_to = scrapy.Field()
    user_name_to = scrapy.Field()
    relation_type = scrapy.Field()
    photo = scrapy.Field()
    updated = scrapy.Field()


class InstagramComments(scrapy.Item):
    user_id = scrapy.Field()
    comment_id = scrapy.Field()
    resource_id = scrapy.Field()
    comment = scrapy.Field()
    author_id = scrapy.Field()
    author_profile = scrapy.Field()
    date = scrapy.Field()
    updated = scrapy.Field()
