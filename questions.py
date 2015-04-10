import sys
sys.path.append('/home/alden/documents/vionel-content/vionel-data-model')
from vionelement import * 
from vionmeta import get_new_fields
from api import search_get
from header import header
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
	idxs = random.sample(xrange(size), num_results)
	movies = [response_json['response']['result']['movies'][i] for i in idxs]
	return movies


# TODO Should be updated to handle ranges
def get_random_tag_pair_with_result(query, response_json, header=header):
	tag_pair = get_random_tag_pair(response_json)
	new_query = Query(**query.as_dict())
	for tag in tag_pair:
		value = {'name': [{'lang': 'en', 'value': tag['keywordFormat']}]}
		attr = getattr(new_query, tag['type'].lower())
		if attr:
			attr.append(value)
		else:
			setattr(new_query, tag['type'].lower(), [value])
	result = search_get('search', header, build_query_dict(new_query))
	return tag_pair, result, new_query

def get_valid_random_tag_pair(query, response_json, header=header):
	for i in range(max_tries):
		tag_pair, result, new_query = get_random_tag_pair_with_result(query, response_json, header)
		if result['totalHits']:
			return tag_pair, new_query
	return None, None

