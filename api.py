import json
import urllib

from flask import Flask, request, session
import requests

from crossdomain import crossdomain


app = Flask(__name__)

try:
    app.config.from_envvar('VIONEL_CONF')
except Exception as e:
    app.config.from_pyfile('conf_dev.py')

api_key = app.config['API_KEY']
new_api = app.config['NEW_API']
old_api = app.config['OLD_API']

import sys
sys.path.append('/home/alden/documents/vionel-content/vionel-data-model')
from vionelement import * 
from vionmeta import get_new_fields
# from header import header
import random

max_tries = 50
page_size = 20

exclude = ['providers', 'years', 'languages']

def build_query_string(query):
	fields = get_new_fields(Query)
	q_string = '|'.join([x for x in [get_query_field_string(query, f) for f in fields] if x])
	return q_string.encode('utf-8')

def build_query_dict(query, size=page_size, page=1):
	return {'size' : str(size), 'page' : str(page), 'tags' : build_query_string(query)}

def get_query_field_string(query, field):
	value = getattr(query, field)
	if not value:
		return None
	if isinstance(value, RangeField):
		if isinstance(value, DateRange):
			return '{0}:range({1}-{2})'.format(field, value.min.year, value.max.year)
		else:
			return '{0}:range({1}-{2})'.format(field, value.min, value.max)
	if isinstance(value, list):
		return '{0}:'.format(field) + ','.join([nm.value for x in value for nm in x.name])

def get_random_tag_pair(response_json):
	cats = [x for x in response_json['response']['availableToQuery']['categories'] if x['filterTerms'] and x['name'] not in exclude]
	if len(cats) <= 2:
		return []
	category_pairs = random.sample(cats, 2)
	tag_pair = [random.choice(x['filterTerms']) for x in category_pairs]
	return tag_pair

def get_random_tag(response_json):
	cats = [x for x in response_json['response']['availableToQuery']['categories'] if x['filterTerms'] and x['name'] not in exclude]
	if len(cats) <= 2:
		return None
	cat = random.choice(cats)
	tag = random.choice(cat['filterTerms'])
	return tag

def get_random_movie_from_result(response_json, size=page_size):
	i = random.randint(0, size)
	movie = response_json['response']['result']['movies'][i]
	return movie

def get_random_movies_from_result(response_json, size=page_size, num_results=3):
	if response_json['totalHits'] <= 2:
		return response_json['response']['result']['movies']
	max_i = response_json['totalHits'] if response_json['totalHits'] < size else size
	idxs = random.sample(xrange(max_i), num_results)
	movies = [response_json['response']['result']['movies'][i] for i in idxs]
	return movies

def add_tag_to_query(query, tag):
	value = {'name': [{'lang': 'en', 'value': tag['keywordFormat']}]}
	attr = getattr(query, tag['type'].lower())
	if attr:
		attr.append(value)
	else:
		setattr(query, tag['type'].lower(), [value])
	return query

# TODO Should be updated to handle ranges
def get_random_tag_pair_with_result(query, response_json, header):
	tag_pair = get_random_tag_pair(response_json)
	new_query = Query(**query.as_dict())
	for tag in tag_pair:
		add_tag_to_query(new_query, tag)
	result = search_get('search', header, build_query_dict(new_query))
	return tag_pair, result, new_query

def get_valid_random_tag_pair(query, response_json, header):
	for i in range(max_tries):
		tag_pair, result, new_query = get_random_tag_pair_with_result(query, response_json, header)
		if result['totalHits']:
			return tag_pair, new_query
	return None, None


def auth(path, headers=None, data=None):
    new_api = app.config['NEW_API']

    url = new_api.format(path)

    api_res = requests.post(url, headers=headers, data=data)

    if api_res.status_code == 200:
        resp = api_res.json()
        session['SessionToken'] = resp['response']['sessionToken']
        return api_res.json()
    else:
        return api_res.json()


def api_newget(path, headers, query=None):
    new_api = app.config['NEW_API']

    if (query):
        new_api += '?' + urllib.urlencode(query).replace('%3A', ':').replace('%7C', '|')

    url = new_api.format(path)

    print url

    api_res = requests.get(url, headers=headers)

    if api_res.status_code == 200:
        return api_res.json()
    else:
        return api_res.json()


def api_newpost(path, headers, query=None):
    new_api = app.config['NEW_API']

    url = new_api.format(path)

    api_res = requests.post(url, headers=headers, data=query)

    if api_res.status_code == 200:
        return api_res.json()
    else:
        return api_res.json()


def api_newdelete(path, headers, query=None):
    new_api = app.config['NEW_API']

    url = new_api.format(path)

    api_res = requests.delete(url, headers=headers, data=query)

    if api_res.status_code == 200:
        return api_res.json()
    else:
        return api_res.json()


def new_api_temp_login():
    base_url = 'http://api.vionel.com/auth/temp/login'

    api_res = requests.post(base_url, headers={'X-Api-Key': api_key})
    print api_res
    if api_res.status_code == 200:
        resp = api_res.json()
        print "200: {0}".format(resp)
        session['SessionToken'] = resp['response']['sessionToken']

        return api_res.json()
    else:
        return api_res.json()


def auth_login(cred):
    base_url = 'http://api.vionel.com/auth/login'

    api_res = requests.post(base_url, data=cred, headers={'X-Api-Key': api_key})
    print api_res
    if api_res.status_code == 200:
        resp = api_res.json()
        print "200: {0}".format(resp)
        session['SessionToken'] = resp['response']['sessionToken']

        return api_res.json()
    else:
        return api_res.json()


def admin_login(cred):
    base_url = 'http://internal-InternalVionelBackend-70710505.eu-west-1.elb.amazonaws.com/api/0.1/{0}.json'

    path = 'auth'
    url = base_url.format(api_key, path)

    api_res = requests.post(url, data=cred)
    response = {}
    if api_res.status_code == 200:
        resp = api_res.json()
        session['userToken'] = resp['response']['credentials']['userToken']
        session['sessionToken'] = resp['response']['credentials']['sessionToken']

    return api_res.json()


def register(path, user, headers=None):
    base_url = 'http://api.foorsee.com/v1/{0}/{1}.json'

    url = base_url.format(api_key, path)

    print url
    print user

    try:
        api_res = requests.post(url, headers=headers, data=user)
        if api_res.status_code == 200:
            resp = api_res.json()
            session['userToken'] = resp['response']['credentials']['userToken']
            session['sessionToken'] = resp['response']['credentials']['sessionToken']

        return api_res.json()

    except Exception as e:
        print "Exception: {0}".format(e)
        return {"Exception": e}


def api_get(path, headers, query=None):
    base_url = app.config['OLD_API']

    if (query):
        base_url += '?' + urllib.urlencode(query).replace('%3A', ':').replace('%7C', '|')

    url = base_url.format(path)
    # print base_url % (api_key, path)
    #url = base_url % (api_key, path)

    print url
    print "h: {0}".format(headers)

    api_res = requests.get(url, headers=headers)

    if api_res.status_code == 200:

        return api_res.json()
    else:
        return {"responseCode": api_res.status_code, "error": {"text": api_res.text}}


def api_post(path, headers, query=None):
    base_url = app.config['OLD_API']
    # if (query):
    #	base_url += '?'+urllib.urlencode(query).replace('%3A', ':')

    #url = base_url % (api_key, path)
    url = base_url.format(path)

    print "url: {0}".format(url)

    api_res = requests.post(url, headers=headers, data=query)

    if api_res.status_code == 200:

        return api_res.json()
    else:
        return {"responseCode": api_res.status_code, "error": {"text": api_res.text}}


def api_freshpost(data):
    fresh_api = app.config['FRESHDESK_API']
    fresh_url = 'https://vionel.freshdesk.com/helpdesk/tickets.json'
    header = {'Content-Type': 'application/json'}

    print "data: {0}".format(data)

    api_res = requests.post(fresh_url, auth=(fresh_api, 'X'), headers=header, data=json.dumps(data))

    if api_res.status_code == 200:

        return api_res.json()
    else:
        return {"responseCode": api_res.status_code, "error": {"text": api_res.text}}


def api_newget1(path, headers, query=None):
    base_url = 'http://api.vionel.com/{0}'
    # base_url = 'http://vionelbackend-1893391943.eu-west-1.elb.amazonaws.com/{0}.json'
    # new = 'http://api.vionel.com/'
    #old = 'http://api.vionel.com/api/0.1/{0}.json'

    # base_url = 'http://internal-InternalVionelBackend-70710505.eu-west-1.elb.amazonaws.com/{0}'

    if (query):
        base_url += '?' + urllib.urlencode(query).replace('%3A', ':').replace('%7C', '|')

    url = base_url.format(path)

    print url

    print "header: {0}".format(headers)

    api_res = requests.get(url, headers=headers)
    # print "api_res: {0}".format(api_res)
    if api_res.status_code == 200:
        return api_res.json()
    else:
        return {"responseCode": api_res.status_code, "error": {"text": api_res.text}}


def api_newpost1(path, headers, query=None):
    base_url = 'http://api.vionel.com/{0}'
    # base_url = 'http://internal-InternalVionelBackend-70710505.eu-west-1.elb.amazonaws.com/{0}'

    url = base_url.format(path)

    # print "url: {0}".format(url)
    # print "headers: {0}".format(headers)
    # print "data: {0}".format(query)


    api_res = requests.post(url, headers=headers, data=query)

    if api_res.status_code == 200:
        return api_res.json()
    else:
        return {"responseCode": api_res.status_code, "error": {"text": api_res.text}}


def search_get(path, headers, query=None):
    base_url = 'http://api.vionel.com/{0}'

    print "query: {0}".format(query)

    if (query):
        base_url += '?' + urllib.urlencode(query).replace('%3A', ':').replace('%7C', '|')

    url = base_url.format(path)

    print url

    print "h1: {0}".format(headers)

    api_res = requests.get(url, headers=headers)

    if api_res.status_code == 200:
        return api_res.json()
    else:
        return {"responseCode": api_res.status_code, "error": {"text": api_res.text}}


def nosession_post(path, query=None):
    # base_url = 'http://api.dev.foorsee.com/v1/{0}/{1}.json'
    base_url = 'http://api.foorsee.com/v1/{0}/{1}.json'

    # if (query):
    #	base_url += '?'+urllib.urlencode(query).replace('%3A', ':')

    #url = base_url % (api_key, path)
    url = base_url.format(api_key, path)

    print "url: {0}".format(url)

    try:
        api_res = requests.post(url, data=query)

        return api_res.json()

    except Exception as e:
        print "Exception: {0}".format(e)
        return {"Exception": e}
    #return {"responseCode": 401}


def headerFixer(headers):
    header = {}
    if 'X-Session-Token' in headers:
        header['X-Session-Token'] = headers['X-Session-Token']
    if 'X-Real-IP' in headers:
        header['X-Forwarded-For'] = headers['X-Real-IP']
    if 'User-Agent' in headers:
        header['User-Agent'] = headers['User-Agent']
        header['X-Session-Token'] = "TushwtZUsz9ufV8x1iDQQoWeLgQYOf"
    return header


@app.route('/api/temp_auth', methods=['POST'])
@crossdomain(origin='*')
def temp_login():
    header = {'X-Api-Key': api_key}
    resp = auth('auth/temp/login', header)
    return json.dumps(resp)


@app.route('/api/test/<name>', methods=['GET'])
def test(name):
    bla = {"name": name}

    return json.dumps(bla)


@app.route('/api/get_timeline/<timeline>', methods=['GET'])
def get_timeline(timeline):
    # resp = api_get("timeline")
    query = {}
    for key in request.args:
        query[key] = request.args.get(key).encode('utf-8')

    header = headerFixer(request.headers)
    resp = api_newget("social/timeline/" + timeline, header, query)
    # print resp

    return json.dumps(resp)


@app.route('/api/get_movie/<movie>', methods=['GET'])
def get_movie(movie):
    # resp = api_get("media/url_friendly/"+movie)
    # print request.headers['X-Session-Token']
    # print request.headers['X-Forwarded-For']
    #print "ip: {0}".format(request.remote_addr)
    #print "head: {0}".format(request.headers)

    # with open('headtest.txt', 'w+') as f:
    # 	for h in request.headers:
    # 		print str(h)
    # 		f.write(str(h)+'\n')
    # 	f.close()

    header = headerFixer(request.headers)
    resp = api_get("media/url_friendly/" + movie, header)
    # print resp
    return json.dumps(resp)


@app.route('/api/me', methods=['GET'])
def get_me():
    header = headerFixer(request.headers)
    resp = api_get('users/me')
    return json.dumps(resp)


@app.route('/api/user/<id>', methods=['GET'])
def get_user(id):
    header = headerFixer(request.headers)
    resp = api_newget("social/profile?publicId=" + id, header)
    # print "res: {0}".format(resp)
    return json.dumps(resp)


@app.route('/api/person/<person>', methods=['GET'])
def get_person(person):
    print "person: {0}".format(person)
    header = headerFixer(request.headers)
    resp = api_get("person/url_friendly/" + person, header)
    return json.dumps(resp)


@app.route('/api/character/<character>', methods=['GET'])
def get_character(character):
    print "charachter: {0}".format(character)
    header = headerFixer(request.headers)
    resp = api_get("character/url_friendly/" + character, header)
    return json.dumps(resp)


@app.route('/api/search', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def search():
    query = {}

    # print request.args
    for key in request.args:
        query[key] = request.args.get(key).encode('utf-8')
    # print "q: {0}".format(query[key])

    header = headerFixer(request.headers)

    # res = api_get('search', query)
    res = search_get('search', header, query)
    return json.dumps(res)


@app.route('/api/user_actions', methods=['POST'])
def user_actions():
    action = json.loads(request.data)
    header = headerFixer(request.headers)
    path = 'social/{0}'.format(action['action'])
    # path = '{0}/url_friendly/{1}/{2}'.format(action['type'],action['media'],action['action'])
    print "path: {0}".format(path)

    resp = api_newpost(path, header, {'targetId': action['targetId'], 'targetType': action['type']})
    return json.dumps(resp)


@app.route('/api/reset_user_actions', methods=['POST'])
def delete_user_actions():
    print "reset"
    action = json.loads(request.data)
    header = headerFixer(request.headers)
    path = 'social/{0}'.format(action['action'])
    # path = '{0}/url_friendly/{1}/{2}'.format(action['type'],action['media'],action['action'])
    print "path: {0}".format(path)
    print "data: {0}".format({'targetId': action['targetId'], 'targetType': action['type']})

    resp = api_newdelete(path, header, {'targetId': action['targetId'], 'targetType': action['type']})
    return json.dumps(resp)


@app.route('/api/get_useractions/<mediaType>/<name>', methods=['GET'])
def get_useractions(mediaType, name):
    header = headerFixer(request.headers)
    path = 'social/profile?targetId={0}'.format(name)
    # path = '{0}/url_friendly/{1}/user_actions'.format(mediaType, name)
    print "path: {0}".format(path)
    # resp = api_get(path)
    resp = api_newget(path, header)

    return json.dumps(resp)


@app.route('/api/follow_state/<publicId>', methods=['GET'])
def get_follow_state(publicId):
    header = headerFixer(request.headers)
    path = 'social/follow?publicId={0}'.format(publicId)
    resp = api_newget(path, header)

    return json.dumps(resp)


@app.route('/api/follow_user', methods=['POST'])
def update_follow_state():
    state = json.loads(request.data)
    header = headerFixer(request.headers)
    path = 'social/follow'
    user = {'publicId': state['publicId']}
    if state['action'] == 'follow':
        resp = api_newpost(path, header, user)
    else:
        resp = api_newdelete(path, header, user)

    return json.dumps(resp)


@app.route('/api/followers_list/<publicId>', methods=['GET'])
def get_followers_list(publicId):
    query = {}
    for key in request.args:
        query[key] = request.args.get(key).encode('utf-8')

    header = headerFixer(request.headers)
    resp = api_newget('/social/followers/' + publicId, header, query)

    return json.dumps(resp)


@app.route('/api/following_list/<publicId>', methods=['GET'])
def get_following_list(publicId):
    query = {}
    for key in request.args:
        query[key] = request.args.get(key).encode('utf-8')

    header = headerFixer(request.headers)
    resp = api_newget('social/following/' + publicId, header, query)

    return json.dumps(resp)


@app.route('/api/collection_list/<collectionType>/<publicId>', methods=['GET'])
def get_collection_list(collectionType, publicId):
    query = {}
    for key in request.args:
        query[key] = request.args.get(key).encode('utf-8')

    header = headerFixer(request.headers)
    resp = api_newget('social/profile/' + collectionType + '/' + publicId, header, query)

    return json.dumps(resp)


@app.route('/api/get_comments/<targetId>', methods=['GET'])
def get_comments(targetId):
    header = headerFixer(request.headers)
    resp = api_newget('social/comment?targetId=' + targetId, header)

    return json.dumps(resp)


@app.route('/api/comment', methods=['POST'])
def post_comment():
    header = headerFixer(request.headers)
    data = json.loads(request.data)

    resp = api_newpost('social/comment', header, data)

    return json.dumps(resp)


@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    query = {}

    for key in request.args:
        query[key] = request.args.get(key).encode('utf-8')

    header = headerFixer(request.headers)

    # res = api_get('search/autocomplete', query)
    res = search_get('search/autocomplete', header, query)
    return json.dumps(res)


@app.route('/api/set_profilepic/<picId>', methods=['POST'])
def set_profilepic(picId):
    header = headerFixer(request.headers)
    resp = api_post("images/" + picId + '/set_as_user_portrait', header)
    if resp['responseCode']:
        refresh = api_newpost('social/refresh', header)
    return json.dumps(refresh)


@app.route('/api/set_backdrop/<picId>', methods=['POST'])
def set_backdrop(picId):
    header = headerFixer(request.headers)
    resp = api_post("images/" + picId + '/set_as_user_backdrop', header)
    if resp['responseCode']:
        bla = api_newpost('social/refresh', header)
    return json.dumps(resp)


@app.route('/api/login', methods=['POST'])
def login():
    cred = json.loads(request.data)
    user = {'username': cred['username'], 'password': cred['password']}

    header = headerFixer(request.headers)
    header['X-Api-Key'] = api_key

    resp = auth('auth/login', header, user)

    # resp = admin_login({'username': cred['username'], 'password': cred['password']})
    return json.dumps(resp)


@app.route('/api/auth/facebook', methods=['POST'])
def facebook_auth():
    accessToken = request.data
    # print "h: {0}".format(request)
    header = headerFixer(request.headers)
    header['X-Api-Key'] = api_key

    resp = api_newpost('auth/facebook/login', header, {'token': accessToken})
    return json.dumps(resp)


@app.route('/api/share', methods=['POST'])
def facebook_share():
    data = json.loads(request.data)
    header = headerFixer(request.headers)
    resp = api_newpost('social/share', header, data)

    return json.dumps(resp)


@app.route('/api/signup', methods=['POST'])
def signup():
    user = json.loads(request.data)
    print user
    # user = request.form
    print "form: {0}".format(user)

    header = headerFixer(request.headers)
    header['X-Api-Key'] = api_key

    resp = api_newpost('auth/signup', header, user)

    print "resp: {0}".format(resp)

    # return json.dumps({"hej": user})
    return json.dumps(resp)


@app.route('/api/verify', methods=['POST'])
def verify_email():
    verify = json.loads(request.data)
    header = headerFixer(request.headers)
    header['X-Api-Key'] = api_key

    resp = api_post('auth/verify_email', header, verify)

    print "resp: {0}".format(resp)

    return json.dumps(resp)


@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    email = json.loads(request.data)

    header = headerFixer(request.headers)
    header['X-Api-Key'] = api_key
    resp = api_newpost('auth/reset/send', header, email)

    print "resp: {0}".format(resp)

    return json.dumps(resp)


@app.route('/api/set_password', methods=['POST'])
def set_password():
    user = json.loads(request.data)

    print "user: {0}".format(user)
    header = headerFixer(request.headers)
    header['X-Api-Key'] = api_key

    resp = api_newpost('auth/reset', header, user)

    print "resp: {0}".format(resp)

    return json.dumps(resp)


@app.route('/api/send_feedback', methods=['POST'])
def send_feedback():
    feedback = json.loads(request.data)
    header = headerFixer(request.headers)
    # print "feed: {0}".format(feedback)

    resp = api_post('user_feedback', header, feedback)

    # print "resp: {0}".format(resp)
    if resp:
        email = ''
        if 'response' in resp and resp['response']:
            email = resp['response']['email']
        if not email or len(email) < 1:
            email = 'anonymous@vionel.com'
        feed = {
        'subject': feedback['subject'],
        'description': feedback['msg'],
        'email': email,
        'priority': 1,
        'status': 2
        }

        freshsend = api_freshpost({'helpdesk_ticket': feed})
    # print "fresh: {0}".format(freshsend)

    return json.dumps(freshsend)


@app.route('/api/logout')
def logout():
    # if 'userToken' in session:
    # session.pop('userToken', None)
    if 'sessionToken' in session:
        session.pop('sessionToken', None)
    return json.dumps({"response": "200"})

@app.route('/api/get_providers', methods=['GET'])
def get_providers():
    header = headerFixer(request.headers)
    resp = api_newget('social/providers', header)

    return json.dumps(resp)

@app.route('/api/initial_question', methods=['POST'])
@crossdomain(origin='*')
def initial_question():
    query = Query()
    header = headerFixer(request.headers)
    print header
    q_response = search_get('search', header, build_query_dict(query))
    tag_pair, new_query = get_valid_random_tag_pair(query, q_response, header)
    response = {'tags' : tag_pair, 'query' : new_query.as_dict()}
    return json.dumps(response)

@app.route('/api/question_results', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def question_results():
    q = json.loads(request.data)
    print "q"
    query = Query(**q)
    header = headerFixer(request.headers)
    q_response = search_get('search', header, build_query_dict(query))
    movies = get_random_movies_from_result(q_response)
    return json.dumps(movies)

@app.route('/api/new_tag', methods=['POST'])
@crossdomain(origin='*')
def new_tag(query, tags):
    q = json.loads(request.data)
    query = Query(**q.query)
    header = headerFixer(request.headers)
    q_response = search_get('search', header, build_query_dict(q.query))
    tag = get_random_tag(q_response)
    add_tag_to_query(q.query, q.tag)
    response = {'tags' : q.tags + [tag], 'query' : q.query.as_dict()}
    return json.dumps(response)

app.secret_key = 'Me secret long time'


# app.debug = True

if __name__ == '__main__':
    app.run(port=3044, debug=True)
