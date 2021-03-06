# -*- coding: utf-8 -*-
from models import Page
from google.appengine.api import memcache
from handlers.base import BaseHandler
import os, mimetypes
import webapp2
import logging


class StartHandler(BaseHandler):     
                   
    def static_page(self, slug, lang):
        """ prosto z cache albo odswiezenie cache """
        assert self.app.local, 'powinno dzialac tylko przy local server!'
        key = "%s-%s"%(slug, lang)       
        body = memcache.get(key)  #@UndefinedVariable        
        if body:
            return body     
        page = Page.get_by(slug, lang)
        if page is None:
            self.abort(404)
        ok, content = page.update_cache()             
        if ok:
            return content
        else:
            self.abort(400)
            
    def static_content(self, slug, lang):
        """ just return page content """
        assert self.app.local, 'powinno dzialac tylko przy local server!'        
        key = "content-%s-%s"%(slug, lang)       
        body = memcache.get(key)  #@UndefinedVariable
        if body:
            return body     
        page = Page.get_by(slug, lang)
        if page is None:
            self.abort(404)
        memcache.set(key, page.content)  #@UndefinedVariable
        return page.content
        
    #
    # serwowanie pliku statycznych z katago static
    #
    def static(self, path):
        """ statics handling """        
        assert self.app.local, 'powinno dzialac tylko przy local server!'
        file_path = os.path.join('static', path)
        if not os.path.exists(file_path):
            logging.warn('"%s" not found'%file_path)
            self.abort(404)
        fp = open(file_path, 'rb')
        mime_type = mimetypes.guess_type(file_path)[0]
        output = fp.read()
        fp.close()
        return webapp2.Response(output, content_type=mime_type)
    
    #
    # pomocnicze 
    #
    def favicon(self):
        return self.static('favicon.ico')
    
    def home_page(self):
        """ default home-pl """
        return self.static_page('home', 'pl')    