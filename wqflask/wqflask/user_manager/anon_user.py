import datetime
import simplejson as json
import redis # used for collections
from flask import Flask, request, g, session
from utility.logger import getLogger
from utility import after
from utility.tools import LOG_SQL_ALCHEMY

from .util_functions import create_signed_cookie, verify_cookie

Redis = redis.StrictRedis()
logger = getLogger(__name__)

class AnonUser(object):
    """Anonymous user handling"""
    cookie_name = 'anon_user_v1'

    def __init__(self):
        self.cookie = request.cookies.get(self.cookie_name)
        if self.cookie:
            logger.debug("ANON COOKIE ALREADY EXISTS")
            self.anon_id = verify_cookie(self.cookie)

        else:
            logger.debug("CREATING NEW ANON COOKIE")
            self.anon_id, self.cookie = create_signed_cookie()

        self.key = "anon_collection:v1:{}".format(self.anon_id)

    def add_collection(self, new_collection):
        collection_dict = dict(name = new_collection.name,
                               created_timestamp = datetime.datetime.utcnow().strftime('%b %d %Y %I:%M%p'),
                               changed_timestamp = datetime.datetime.utcnow().strftime('%b %d %Y %I:%M%p'),
                               num_members = new_collection.num_members,
                               members = new_collection.get_members())

        Redis.set(self.key, json.dumps(collection_dict))
        Redis.expire(self.key, 60 * 60 * 24 * 5)

    def delete_collection(self, collection_name):
        existing_collections = self.get_collections()
        updated_collections = []
        for i, collection in enumerate(existing_collections):
            if collection['name'] == collection_name:
                continue
            else:
                this_collection = {}
                this_collection['id'] = collection['id']
                this_collection['name'] = collection['name']
                this_collection['created_timestamp'] = collection['created_timestamp'].strftime('%b %d %Y %I:%M%p')
                this_collection['changed_timestamp'] = collection['changed_timestamp'].strftime('%b %d %Y %I:%M%p')
                this_collection['num_members'] = collection['num_members']
                this_collection['members'] = collection['members']
                updated_collections.append(this_collection)

        Redis.set(self.key, json.dumps(updated_collections))

    def get_collections(self):
        json_collections = Redis.get(self.key)
        if json_collections == None or json_collections == "None":
            return []
        else:
            collections = json.loads(json_collections)
            for collection in collections:
                collection['created_timestamp'] = datetime.datetime.strptime(collection['created_timestamp'], '%b %d %Y %I:%M%p')
                collection['changed_timestamp'] = datetime.datetime.strptime(collection['changed_timestamp'], '%b %d %Y %I:%M%p')
            return collections

    def import_traits_to_user(self):
        result = Redis.get(self.key)
        collections_list = json.loads(result if result else "[]")
        for collection in collections_list:
            collection_exists = g.user_session.get_collection_by_name(collection['name'])
            if collection_exists:
                continue
            else:
                g.user_session.add_collection(collection['name'], collection['members'])

    def display_num_collections(self):
        """
        Returns the number of collections or a blank string if there are zero.

        Because this is so unimportant...we wrap the whole thing in a try/expect...last thing we
        want is a webpage not to be displayed because of an error here

        Importand TODO: use redis to cache this, don't want to be constantly computing it
        """
        try:
            num = len(self.get_collections())
            if num > 0:
                return num
            else:
                return ""
        except Exception as why:
            print("Couldn't display_num_collections:", why)
            return ""
