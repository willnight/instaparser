from pprint import pprint
import pymongo

client = pymongo.MongoClient('localhost', 27017)
mongodb = client['instagram_db']
collection_post = mongodb['user_relations']
collection_comments = mongodb['comments']

username = 'kolayuk'

surscribers = collection_post.find({"$and": [{"relation_type": 'subscriber'}, {"user_name_to": username}]}
                                   , {'user_name_from': 1, 'photo': 1, 'user_id_from': 1, '_id': False})

folowers = collection_post.find({"$and": [{"relation_type": 'follower'}, {"user_name_from": username}]}
                                , {'user_name_to': 1, 'photo': 1, 'user_id_to': 1, '_id': False})
# top 10
comments = collection_comments.aggregate([{"$group": {'_id': "$author_profile", 'count': {"$sum": 1}}},
                                          {"$sort": {'count': -1}}, {"$limit": 10}])

print(f'У пользователя {username} {surscribers.count()} подписчиков, и он подписан на {folowers.count()} пользователей')

print('*'*100)
print('Подписчики:')
for user in surscribers:
    pprint(user)

print('*'*100)
print('Подписан на:')
for user in folowers:
    pprint(user)

print('*'*100)
print('Топ 10 самых активных комментаторов:')
for user in comments:
    pprint(user)
