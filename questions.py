import json

API_KEY = 'XHJK73jsad753dGKNLCUWD6D57dx'
NEW_API = 'http://api.vionel.com/{0}' 

def search_get(path, headers, query=None):
	base_url = 'http://api.vionel.com/{0}'
	if (query):
		base_url += '?' + urllib.urlencode(query).replace('%3A', ':').replace('%7C', '|')
		url = base_url.format(path)
		print url
		api_res = requests.get(url, headers=headers)
		if api_res.status_code == 200:
			return api_res.json()
	else:
		return {"responseCode": api_res.status_code, "error": {"text": api_res.text}}
		
@app.route('/api/search', methods=['GET'])
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

def headerFixer(headers):
	header = {}
	if 'X-Session-Token' in headers:
		header['X-Session-Token'] = headers['X-Session-Token']
	if 'X-Real-IP' in headers:
		header['X-Forwarded-For'] = headers['X-Real-IP']
	if 'User-Agent' in headers:
		header['User-Agent'] = headers['User-Agent']
	return header

