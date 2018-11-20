import redis # used for collections
from flask import request
from utility.logger import getLogger
from utility.elasticsearch_tools import (get_elasticsearch_connection,
                                         get_user_by_unique_column)

from .util_functions import (cookie_name, verify_cookie)

Redis = redis.StrictRedis()
logger = getLogger(__name__)
THREE_DAYS = 60 * 60 * 24 * 3

class UserSession(object):
    """Logged in user handling"""

    cookie_name = cookie_name

    def __init__(self):
        cookie = request.cookies.get(self.cookie_name)
        if not cookie:
            logger.debug("NO USER COOKIE")
            self.logged_in = False
            return
        else:
            session_id = verify_cookie(cookie)

            self.redis_key = self.cookie_name + ":" + session_id
            logger.debug("self.redis_key is:", self.redis_key)
            self.session_id = session_id
            self.record = Redis.hgetall(self.redis_key)

            if not self.record:
                # This will occur, for example, when the browser has been left open over a long
                # weekend and the site hasn't been visited by the user
                self.logged_in = False

                ########### Grrr...this won't work because of the way flask handles cookies
                # Delete the cookie
                #response = make_response(redirect(url_for('login')))
                #response.set_cookie(self.cookie_name, '', expires=0)
                #flash(
                #   "Due to inactivity your session has expired. If you'd like please login again.")
                #return response
                return

            if Redis.ttl(self.redis_key) < THREE_DAYS:
                # (Almost) everytime the user does something we extend the session_id in Redis...
                logger.debug("Extending ttl...")
                Redis.expire(self.redis_key, THREE_DAYS)

            logger.debug("record is:", self.record)
            self.logged_in = True

    @property
    def user_id(self):
        """Shortcut to the user_id"""
        if 'user_id' in self.record:
            return self.record['user_id']
        else:
            return ''

    @property
    def es_user_id(self):
        """User id from ElasticSearch (need to check if this is the same as the id stored in self.records)"""

        es = get_elasticsearch_connection()
        user_email = self.record['user_email_address']

        #ZS: Get user's collections if they exist
        response = es.search(
                       index = "users", doc_type = "local", body = {
                       "query": { "match": { "email_address": user_email } }
                   })

        user_id = response['hits']['hits'][0]['_id']
        return user_id

    @property
    def user_name(self):
        """Shortcut to the user_name"""
        if 'user_name' in self.record:
            return self.record['user_name']
        else:
            return ''

    @property
    def user_collections(self):
        """List of user's collections"""

        es = get_elasticsearch_connection()

        user_email = self.record['user_email_address']

        #ZS: Get user's collections if they exist
        response = es.search(
                       index = "users", doc_type = "local", body = {
                       "query": { "match": { "email_address": user_email } }
                   })
        user_info = response['hits']['hits'][0]['_source']
        if 'collections' in user_info.keys():
            if len(user_info['collections']) > 0:
                return json.loads(user_info['collections'])
            else:
                return []
        else:
            return []

    @property
    def num_collections(self):
        """Number of user's collections"""

        es = get_elasticsearch_connection()

        user_email = self.record['user_email_address']

        #ZS: Get user's collections if they exist
        response = es.search(
                       index = "users", doc_type = "local", body = {
                       "query": { "match": { "email_address": user_email } }
                   })

        user_info = response['hits']['hits'][0]['_source']
        logger.debug("USER NUM COLL:", user_info)
        if 'collections' in user_info.keys():
            if user_info['collections'] != "[]" and len(user_info['collections']) > 0:
                collections_json = json.loads(user_info['collections'])
                return len(collections_json)
            else:
                return 0
        else:
            return 0

###
# ZS: This is currently not used, but I'm leaving it here commented out because the old "set superuser" code (at the bottom of this file) used it
###
#    @property
#    def user_ob(self):
#        """Actual sqlalchemy record"""
#        # Only look it up once if needed, then store it
#        # raise "OBSOLETE: use ElasticSearch instead"
#        try:
#            if LOG_SQL_ALCHEMY:
#                logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
#
#            # Already did this before
#            return self.db_object
#        except AttributeError:
#            # Doesn't exist so we'll create it
#            self.db_object = model.User.query.get(self.user_id)
#            return self.db_object

    def add_collection(self, collection_name, traits):
        """Add collection into ElasticSearch"""

        collection_dict = {'id': unicode(uuid.uuid4()),
                           'name': collection_name,
                           'created_timestamp': datetime.datetime.utcnow().strftime('%b %d %Y %I:%M%p'),
                           'changed_timestamp': datetime.datetime.utcnow().strftime('%b %d %Y %I:%M%p'),
                           'num_members': len(traits),
                           'members': list(traits) }

        es = get_elasticsearch_connection()

        user_email = self.record['user_email_address']
        response = es.search(
                       index = "users", doc_type = "local", body = {
                       "query": { "match": { "email_address": user_email } }
                   })

        user_id = response['hits']['hits'][0]['_id']
        user_info = response['hits']['hits'][0]['_source']

        if 'collections' in user_info.keys():
            if user_info['collections'] != [] and user_info['collections'] != "[]":
                current_collections = json.loads(user_info['collections'])
                current_collections.append(collection_dict)
                self.update_collections(current_collections)
                #collections_json = json.dumps(current_collections)
            else:
                self.update_collections([collection_dict])
                #collections_json = json.dumps([collection_dict])
        else:
            self.update_collections([collection_dict])
            #collections_json = json.dumps([collection_dict])

        return collection_dict['id']

    def delete_collection(self, collection_id):
        """Remove collection with given ID"""

        updated_collections = []
        for collection in self.user_collections:
            if collection['id'] == collection_id:
                continue
            else:
                updated_collections.append(collection)

        self.update_collections(updated_collections)

        return collection['name']

    def add_traits_to_collection(self, collection_id, traits_to_add):
        """Add specified traits to a collection"""

        this_collection = self.get_collection_by_id(collection_id)

        updated_collection = this_collection
        updated_traits = this_collection['members'] + traits_to_add

        updated_collection['members'] = updated_traits
        updated_collection['num_members'] = len(updated_traits)
        updated_collection['changed_timestamp'] = datetime.datetime.utcnow().strftime('%b %d %Y %I:%M%p')

        updated_collections = []
        for collection in self.user_collections:
            if collection['id'] == collection_id:
                updated_collections.append(updated_collection)
            else:
                updated_collections.append(collection)

        self.update_collections(updated_collections)

    def remove_traits_from_collection(self, collection_id, traits_to_remove):
        """Remove specified traits from a collection"""

        this_collection = self.get_collection_by_id(collection_id)

        updated_collection = this_collection
        updated_traits = []
        for trait in this_collection['members']:
            if trait in traits_to_remove:
                continue
            else:
                updated_traits.append(trait)

        updated_collection['members'] = updated_traits
        updated_collection['num_members'] = len(updated_traits)
        updated_collection['changed_timestamp'] = datetime.datetime.utcnow().strftime('%b %d %Y %I:%M%p')

        updated_collections = []
        for collection in self.user_collections:
            if collection['id'] == collection_id:
                updated_collections.append(updated_collection)
            else:
                updated_collections.append(collection)

        self.update_collections(updated_collections)

        return updated_traits

    def get_collection_by_id(self, collection_id):
        for collection in self.user_collections:
            if collection['id'] == collection_id:
                return collection

    def get_collection_by_name(self, collection_name):
        for collection in self.user_collections:
            if collection['name'] == collection_name:
                return collection

        return None

    def update_collections(self, updated_collections):
        es = get_elasticsearch_connection()

        collection_body = {'doc': {'collections': json.dumps(updated_collections)}}
        es.update(index='users', doc_type='local', id=self.es_user_id, refresh='wait_for', body=collection_body)

    def delete_session(self):
        # And more importantly delete the redis record
        Redis.delete(self.cookie_name)
        logger.debug("At end of delete_session")
