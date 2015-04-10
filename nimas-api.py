import json
import urllib

from flask import Flask, request, session
import requests


app = Flask(__name__)

API_KEY = 'XHJK73jsad753dGKNLCUWD6D57dx'
NEW_API = 'http://api.vionel.com/{0}' 

def auth(path, headers=None, data=None):
    new_api = NEW_API

    url = new_api.format(path)

    print "url: {0}".format(url)

    api_res = requests.post(url, headers=headers, data=data)

    if api_res.status_code == 200:
        resp = api_res.json()
        session['SessionToken'] = resp['response']['sessionToken']
        return api_res.json()
    else:
        return api_res.json()

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
        
@app.route('/api/temp_auth', methods=['POST'])
def temp_login():
    header = {'X-Api-Key': API_KEY}
    resp = auth('auth/temp/login', header)
    return json.dumps(resp)

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

app.secret_key = 'Me secret long time'

if __name__ == '__main__':
    app.run(port=3044, debug=True)
