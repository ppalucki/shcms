# -*- coding: utf-8 -*-
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import memcache
import yaml
import logging
import settings
import webapp2
from pytz.gae import pytz #@UnresolvedImport


class Page(db.Model):
    """ strona """
    
    slug        = db.StringProperty(required=True)    
    lang        = db.StringProperty(required=True)
    #order       = db.FloatProperty(verbose_name=u'kolejność', required=True)    
    hidden      = db.BooleanProperty(default=False, required=True)
    title       = db.StringProperty(required=True)
    content     = db.TextProperty(required=True)
    etag        = db.StringProperty(required=True)
    updated     = db.DateTimeProperty(required=True)
    edit_url    = db.TextProperty()
    src         = db.TextProperty()

    @property
    def res_id(self):
        return self.key().name()

    def __repr__(self):
        return u'<Page %s@%s>'%(self.slug, self.lang)

    @classmethod
    def get_by_slug(cls, slug, lang):
        return cls.all().filter('slug =', slug).filter('lang =', lang).get()
    
    @classmethod
    def get_by_res_id(cls, res_id):
        return cls.get_by_key_name(res_id)
    
    def update_content(self):
        from util import get_doc_content
        self.content = get_doc_content(self.src)
        self.put()
        
    def render_content(self):
        from util import render_template
        return render_template('base.html', content=self.content, title=self.title)
    
    def update_cache(self):
        content = self.render_content()
        if not content:
            return
        return memcache.set("%s@%s"%(self.slug, self.lang), content.encode('utf8'))  #@UndefinedVariable        

    @property
    def updated_local(self):
        mytz = pytz.timezone('Europe/Warsaw') 
        return pytz.utc.localize(self.updated).astimezone(mytz)
        

class Album(db.Model):
    name        = db.StringProperty(verbose_name=u'slug', required=True)
    lang        = db.StringProperty(verbose_name=u'jęyzk', required=True)

class Photo(db.Model):
    """ strona """
    
    slug        = db.StringProperty(verbose_name=u'slug', required=True)    
    lang        = db.StringProperty(verbose_name=u'jęyzk', required=True)
    order       = db.FloatProperty(verbose_name=u'kolejność', required=True)    
    hidden      = db.BooleanProperty(default=False)
    title       = db.StringProperty(verbose_name=u'tytuł', required=True)
    content     = db.TextProperty(verbose_name=u'treść', required=True)
            
class Var(db.Model):
    """ edytowalne zmienne """        
    raw       = db.TextProperty(required=True)            
    desc      = db.StringProperty()
    
    @property
    def name(self):
        return self.key().name()
    
    @property
    def value(self):
        return yaml.load(self.raw)
    
    @classmethod
    def update_from_settings(cls):
        for name, (desc, value) in settings.VARS.iteritems():
            raw = yaml.dump(value)
            logging.debug('inserting var=%s raw=%r', name, raw)  
            cls.get_or_insert(key_name=name, raw=raw, desc=desc)

    @classmethod
    def get_value(cls, name):
        current_request = webapp2.WSGIApplication.request
        if current_request is not None:
            if hasattr(current_request, 'vars_registry') and name in current_request.vars_registry:
                return current_request.vars_registry[name]
        
        value = memcache.get('Var-%s'%name) #@UndefinedVariable
        if value is not None:
            return value
        var = cls.get_by_key_name(name)
        if var is not None:
            value = var.value
            memcache.add('Var-%s'%name, value) #@UndefinedVariable        
            return value
        
        desc, value = settings.VARS[name] #@UnusedVariable
        memcache.add('Var-%s'%name, value) #@UndefinedVariable
        
        if current_request is not None:
            if not hasattr(current_request, 'vars_registry'):
                current_request.vars_registry = {}
            current_request.vars_registry[name]=value            
        return value
    
    @classmethod
    def set_value(cls, name, value):
        var = Var.get_by_key_name(name)
        assert var is not None, 'var=%s not found'%name
        expected_type = yaml.load(var.raw)
        if type(value) != type(expected_type):
            raise ValueError('expected type=%s but got=%s'%(expected_type, type(value)))
        var.raw = yaml.dump(value)
        var.put() 
        
        assert memcache.set('Var-%s'%name, value) #@UndefinedVariable
    
    def __repr__(self):
        return u'<Var(%s:%r)>'%(self.name, self.value)
            
class Image(db.Model):
    """ obrazki """
    title       = db.StringProperty(required=True)
    desc        = db.StringProperty()
    body        = db.BlobProperty(required=True) 
    
    
        

