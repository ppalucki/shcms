# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import users
from cms.models import Var

class AdminMiddleware:
    def pre_dispatch(self, handler):
        from wx.py.PyShell import main; main(dict(globals(), ** locals()))
        kupa

class LangMiddleware:

    def pre_dispatch(self, handler):
        kupa
        handler.lang = handler.request.cookies.get('lang')
    
    def post_dispatch(self, handler, response):
        kupa
        response.cookies.set('lang', handler.lang)
        
        