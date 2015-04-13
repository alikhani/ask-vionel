
def get_question(tags):
	base = 'Do you like'
	types = {x['type'].lower(): x for x in tags}
	if 'genres' in types:
		base += ' ' + types['genres']['keywordFormat']
	base += ' movies'
	if 'people' in types:
		base += ' starring {0}'.format(types['people']['keywordFormat'])
	if 'characters' in types:
		base += ' with the character {0}'.format(types['characters']['keywordFormat'])
	if 'keywords' in types:
		base += ' involving {0}'.format(types['keywords']['keywordFormat'])
	base += '?'
	return base
