from datetime import datetime
from enum import Enum, EnumMeta
from copy import deepcopy
from dateutil import parser
import json

class VionDefinitionError(Exception):
	pass

# Meta classes

class VionMetaBase(type):
	def __new__(mcs, class_name, bases, attrs):
		cls = super(VionMetaBase, mcs).__new__(mcs, class_name, bases, attrs)
		return cls

class VionMeta(VionMetaBase):

	def __new__(mcs, class_name, bases, attrs):
		fields = {}
		class_fields = {}
		for n, v in attrs.iteritems():
			# These will be initialized on a per instance basis
			if is_instance_field(v):
				fields[n] = v
			# These are instantiated in the class scope
			else:
				class_fields[n] = v

		# Instantiate metaclass (instance is a class)
		cls = super(VionMeta, mcs).__new__(mcs, class_name, bases, attrs)
		# Set fields to uninstantiated class types 
		# (so that subfields can later be instantiated on a per instance basis)
		cls._fields = cls._fields.copy()
		cls._fields.update(fields)
		# Set class field values (shared among all instances of the class)
		cls._class_fields = cls._class_fields.copy()
		cls._class_fields.update(class_fields)
		cls._types = [c.__name__ for c in cls.mro() if isinstance(c, VionMeta)][:-2]
		return cls
		
	def __call__(cls, *args, **kwargs):
		instance = super(VionMeta, cls).__call__()
		# Instantiate fields just so they're there (visible)
		for field, subcls in instance._fields.items():
			if isinstance(subcls, list):
				instance.__setattr__(field, [])
			else:
				instance.__setattr__(field, None)
		# Set field values from constructor parameters
		instance._setattrs(kwargs)
		return instance

class VionISOMeta(VionMetaBase):
	pass

class VionISOFieldMeta(VionMeta):
	def __new__(mcs, class_name, bases, attrs):
		cls = super(VionISOFieldMeta, mcs).__new__(mcs, class_name, bases, attrs)
		for n, v in attrs.iteritems():
			if isinstance(v, VionISOMeta):
				if hasattr(cls, '_iso_field'):
					raise VionDefinitionError("ISOField Types may only have one field of a type ISOType")
				cls._iso_field = n
				cls._iso_type = v.__name__
		return cls

def is_instance_field(v):
	is_list_field = isinstance(v, list) and len(v) == 1 and isinstance(v[0], VionMetaBase)
	return isinstance(v, VionMetaBase) or is_list_field or isinstance(v, EnumMeta)

''' This is just a placeholder object for the model definitions '''
class Tiny(object):
	def __init__(self, class_name):
		self.class_name = class_name

# Base Classes

class Vion(object):
	__metaclass__ = VionMetaBase

# Classes that give their progeny a new behavior
class BehavioralType(Vion):
	pass

''' The immediate progeny of this class will be the classes specified by JSON's type field '''
class Saturatable(BehavioralType):
	pass


# Simple Field classes
class FieldType(Vion):
	pass

'''For, you know, dates and times'''
# TODO:: This should be updated so that it returns an object of type Datetime instead of type datetime for consistency's sake
class Datetime(FieldType, datetime):
	def __new__(cls, date):
		if isinstance(date, datetime):
			return date
		else:
			new = parser.parse(date)
		#new.__class__ = cls
			return new

''' Strings should be unicode mostly '''
class Unicode(FieldType, unicode):
	pass

''' These lead somewhere. On the internets. '''
class Url(FieldType, str):
	pass

class Integer(FieldType, int):
	pass

''' Cause why should points stay in the same place? '''
class Float(FieldType, float):
	pass

class Boolean(FieldType):
	def __new__(self, boolean):
		if boolean is True:
			return True
		elif boolean is False:
			return False
		else:
			raise TypeError("Boolean types must be either True or False")

# Classes for ids
class IDType(Vion):
	pass

'''Intended for an id-like field with a unique value'''
class Unique(IDType, str):
	pass

class VionelID(IDType, str):
	def __init__(self, string):
		if not string.startswith('vnl.'):
			raise AttributeError("vionelID {0} does not begin with Vionel prefix vnl.".format(string))
		splits = string.split('.')
		if not len(splits) == 2 or not splits[1].isalnum():
			raise AttributeError("{0} is not a valid vionelID format".format(string))

class TMDBID(IDType, str):
	def __init__(self, string):
		if '.' not in string:
			raise AttributeError("TMDBIDs must be of the form (MOVIE|TV).123456. {0} does not match this format".format(string))
		prefix = string.split('.')[0]
		if prefix not in ['TV', 'MOVIE']:
			raise AttributeError("TMDBIDs must be of the form (MOVIE|TV).123456. {0} does not match this format".format(string))

class ISOLangID(IDType, str):
	pass
		
# Classes whose instances have an iso name convention
class ISOType(Vion):
	__metaclass__ = VionISOMeta

class ISOLanguage(ISOType, str):
	pass

class ISOCountry(ISOType, str):
	pass

class ISOCurrency(ISOType, str):
	pass


# Multi-field base class

class VionContainer(Vion):
	sourceUrl = Url

	__metaclass__ = VionMeta

	_fields = {}
	_class_fields = {}

	def _get_attr_value(self, name, value, attr_class):
		if value is None:
			return None
		if isinstance(value, attr_class):
			return value
		elif isinstance(value, dict):
			return attr_class(**value)
		raise TypeError("{0} field {1} can only be set with a dict or an object of type {2}. Type {3} found.".format(self.__class__.__name__, name, attr_class.__name__, type(value).__name__))

	def _get_list_attr(self, name, value):
		attr_class = self._fields[name][0]
		attr = VionList(attr_class)
		if value is None or value is []:
			return attr
		if not isinstance(value, list):
			raise TypeError("{0} field {1} should be list but type {2} found".format(self.__class__.__name__, name, type(value)))
		for v in value:
			attr.append(self._get_attr_value(name, v, attr_class))
		return attr

	def _get_nonlist_attr(self, name, value):
		attr_class = self._fields[name]
		return self._get_attr_value(name, value, attr_class)

	# Attributes can be set from dicts or from already instantiated field objects
	def __setattr__(self, name, value):
		if name.startswith('_'):
			return
		if name not in self._fields:
			raise KeyError("{0} does not support field: {1}".format(self.__class__.__name__, name))
		islist = isinstance(self._fields[name], list)
		attr_class = self._fields[name][0] if islist else self._fields[name] 
		if not value:
			attr = VionList(attr_class) if islist else None
			super(Vion, self).__setattr__(name, attr)
			return
		if isinstance(attr_class, VionMeta):
			if islist:
				attr = self._get_list_attr(name, value)
			else:
				attr = self._get_nonlist_attr(name, value)
			super(Vion, self).__setattr__(name, attr)
		else:
			if isinstance(value, Vion) and not isinstance(value, attr_class):
				raise TypeError("{0} field {1} expected a class of type {2} but class of type {3} found.".format(self.__class__.__name__, name, attr_class, type(value)))
			field = attr_class(value)
			super(Vion, self).__setattr__(name, field)

	def _setattrs(self, attr_dict):
		assert isinstance(attr_dict, dict), "_setattrs may only be called with a dict."
		for key, value in attr_dict.items():
			if key == 'type' or key =='subtype':
				continue
			self.__setattr__(key, value)


	def as_dict(self):
		d = deepcopy(self.__dict__)
		for key, value in d.items():
			if isinstance(value, VionContainer):
				d[key] = value.as_dict()
			elif isinstance(value, list):
				lst = []
				for i,x in enumerate(value):
					if isinstance(x, VionContainer):
						lst.append(x.as_dict())
				d[key] = lst
			elif isinstance(value, datetime):
				d[key] = value.isoformat()
		# Clear dict of emptiness
		for key, value in d.items():
			if value is None or value == []:
				d.pop(key, None)
		# Add type and subtype
		saturatable_ancestor = get_saturatable_ancestor(self.__class__)
		if saturatable_ancestor:
			d['type'] = saturatable_ancestor.__name__.upper()
			if d['type'] != self.__class__.__name__.upper():
				d['subtype'] = self.__class__.__name__.upper()
		return d

	def as_json(self):
		return json.dumps(self.as_dict())

class VionList(list):
	def _get_list_item(self, item):
		if isinstance(item, Vion):
			if isinstance(item, self.type):
				return item
			else:
				raise TypeError("{0} VionList type does not support type {1}".format(self.type.__name__, type(item).__name__))
		elif isinstance(item, dict):
			return self.type(**item)
		else:
			return self.type(item)

	def __init__(self, type, lst=None):
		if not isinstance(type, VionMetaBase):
			raise VionDefinitionError("Lists may only contain pre-defined Vion types")
		list.__init__(self)
		self.type = type
		if lst:
			for x in lst:
				self.append(x)

	def __setitem__(self, index, value):
		super(VionList, self).__setitem__(index, self._get_list_item(value))	

	def __add__(self, other):
		vlist = VionList(self.type, other)
		return super(VionList, self).__add__(vlist)

	def __iadd__(self, other):
		vlist = VionList(self.type, other)
		return super(VionList, self).__iadd__(vlist)

	def append(self, item):
		super(VionList, self).append(self._get_list_item(item))

	def extend(self, lst):
		vlist = VionList(self.type, lst)
		super(VionList, self).extend(vlist)


def get_new_fields(klass):
	if not isinstance(klass.__bases__[0], VionMeta):
		return set(klass._fields)
	return set(klass._fields) - set(klass.__bases__[0]._fields)

# Only from primary inheritance
def get_new_class_fields(klass):
	if not isinstance(klass.__base__, VionMeta):
		return None
	return set(klass._class_fields) - set(klass.__base__._class_fields)

def get_saturatable_ancestor(klass):
	if not isinstance(klass, VionMeta):
		return None
	if Saturatable in klass.__base__.__bases__:
		return klass
	return get_saturatable_ancestor(klass.__base__)

class VionGroup(VionContainer):
	pass

''' These should contain only one ISOType and any number of FieldTypes'''
class ISOField(VionContainer):
	__metaclass__ = VionISOFieldMeta

class RangeField(VionContainer):
	__metaclass__ = VionISOFieldMeta

class IntRange(RangeField):
	min = Integer
	max = Integer

class FloatRange(RangeField):
	min = Float
	max = Float

class DateRange(RangeField):
	min = Datetime
	max = Datetime
