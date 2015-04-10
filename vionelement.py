from enum import Enum
from vionmeta import *
import sys

PerformanceType = Enum('PerformanceType', 'NARRATOR PUPPETEER CAMEO MOTION_CAPTURE BODY_DOUBLE PLAYBACK_SINGER DELETED_SCENE HIM_HERSELF VOICE ARCHIVE_FOOTAGE')
ImageType = Enum('ImageType', 'PORTRAIT LANDSCAPE THUMBNAIL')


''' This is the base class for things that can go in a media collection.
'''
class Collectable(BehavioralType):
	dateCollected = Datetime

''' For things that can be tagged in a Tagged Element '''
class Taggable(BehavioralType):
	pass

''' These are things that can be shared and should thus have a url '''
class Shareable(BehavioralType):
    pass

class Followable(BehavioralType):
    pass

''' ISOField types should contain only one ISOType and any number of FieldTypes'''

''' Ensures text fields have language tags '''
class TextField(ISOField):
	value = Unicode
	lang = ISOLanguage 
	isPrimary = bool

''' Ensures monetary values have a currency '''
class CostField(ISOField):
	value = Float
	currency = ISOCurrency

''' For country-specific dates '''
class NationalDatetime(ISOField):
	value = Datetime
	country = ISOCountry

''' For all other external ids '''
class IDSuite(VionGroup):
	oldRowNumber = Integer
	freebaseID = Unique
	imdbID = Unique
	tmdbID = TMDBID
	rottenTomatoesID = Unique
	tvdbID = Unique
	tvRageID = Unique
	zap2itID = Unique
	netflixID = Unique
	wikiPageID = ISOLangID
	wikiArticleName = ISOLangID

''' I alone am best! '''
class RatingSuite(VionGroup):
	imdb = Float
	rottenTomatoes = Float

''' Metadata about this json '''
class MetaData(VionGroup):
	timeCreated = Datetime
	lastUpdated = Datetime
	version = Unicode
	instantiatedFrom = Unicode 

''' Minimum fields that make up an entity. Corresponds to a node in the graph. '''
class VionBase(VionGroup, Shareable):
	vionelID = VionelID 
	externalIDs = IDSuite
	metaData = MetaData
	description = [TextField]

''' Base with a name '''
class VionNamedBase(VionBase):
    name = [TextField]
    aliases = [TextField]

class Keyword(VionNamedBase):
	pass

class Genre(VionNamedBase):
	pass

''' Tag elements '''

class TaggedElement(VionBase):
	tags = [Taggable]

class WebElement(TaggedElement, Saturatable):
	url = Url

class Image(WebElement):
	imageType = ImageType
	height = Integer
	width = Integer

class WebVideo(WebElement):
	pass

class Trailer(WebVideo):
	pass

''' 
TinyVion objects are interelement links and should pretty much only show up in Mediators.
If you think an element should directly link to another element,
you should probably consider whether or not it would be better in a mediator.
'''

class TinyVion(VionNamedBase):
	urlFriendly = Unicode
	images = [Image]

''' Base class for all of the main entities '''
''' These are the kind of things you'd expect to have a profile page of their own in the service '''
class VionElement(TinyVion, Saturatable):
	videos = [WebVideo]

''' Mediator objects are for links to other elements where
	additional information should be provided or for
	situations where multiple elements logically make up their own entity
	like the performance of an actor playing a character in a film '''
class Mediator(TinyVion, Saturatable):
	pass

''' Mediators '''
class UserAction(Mediator):
	like = Boolean
	dislike = Boolean
	bookmarked = Boolean
	item = Collectable
	user = Tiny('User')

# TODO:: Adapt this for any VionElement with inherited fields
# instead of hardcoded for Media
class Query(Mediator):
	years = DateRange
	runtime = IntRange
	ratings = FloatRange
	genres = [Genre]
	people = [Tiny('Person')]
	languages = [ISOLanguage]
	keywords = [Keyword]
	characters = [Tiny('Character')]
	

class Performance(Mediator):
	production = Tiny('Production')
	person = Tiny('Artist')
	character = Tiny('Character')
	parentMedia = [Tiny('Media')]
	performanceType = Unicode

class Provision(Mediator):
	provider = Tiny('Provider')
	production = Tiny('Production')
	hd = bool
	priceRental = CostField
	pricePurchase = CostField
	availableWithSubscription = bool 
	sourceUrl = Url
	availableIn = [ISOCountry]
	firstCrawled = Datetime
	expires = Datetime
	

''' Extended media objects '''
''' These are media related things that would have a profile.
This includes seasons, series, trilogies, etc '''
class Media(VionElement):
	themeSong = Tiny('Track')

class MediaSeries(Media, Collectable):
	contents = [Collectable]

''' These are things that can be physically watched, i.e. movies and episodes '''
class Production(VionElement, Collectable):
	performances = [Performance]
	languages = [ISOLanguage]
	countries = [ISOCountry]
	provisions = [Provision]
	releaseDate = Datetime
	trailers = [Trailer]
	releaseDates = [NationalDatetime]
	runtime = Integer
	soundtrack = Tiny('Soundtrack')

class Movie(Production, Media):
	pass

class Episode(Production):
	pass

class Season(MediaSeries):
	pass

class UserCollection(MediaSeries):
    pass

''' Other Extended objects '''

class Track(Production):
	pass

class Soundtrack(MediaSeries):
	pass

class Provider(VionElement):
	pass

class Person(VionElement, Followable):
    pass

class User(Person):
    collections = [UserCollection]

class Artist(User):
    performances = [Performance]


class Character(VionElement, Followable):
	performances = [Performance]




#### Leave all the junk down here alone ####

module = sys.modules[__name__]

# This is interlinking class magic for connecting class fields to classes that have yet to be defined via the Tiny class
for klass in module.__dict__.values():
	if isinstance(klass, VionMeta):
		for field, value in klass._class_fields.items():
			if isinstance(value, Tiny) or isinstance(value, list) and isinstance(value[0], Tiny):
				islist = isinstance(klass._class_fields.pop(field), list)
				name = value[0].class_name if islist else value.class_name
				if not hasattr(module, name):
					raise AttributeError("vionelement module does not contain class {0}. Check the spelling of {1}'s Tiny {2} attribute".format(name, klass.__name__, field))
				klass._fields[field] = [getattr(module, name)] if islist else getattr(module, name)


