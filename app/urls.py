# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, HandlerPrefixRoute
from util import direct_render
import handlers

urls = [    
    # test urls
    Route('/test/hello', handlers.TestHandler, handler_method='hello'),
    Route('/test/template', handlers.TestHandler, handler_method='template'),
    Route('/test/direct', direct_render('test/direct.html', foo='bar') ),
    
    # admin urls
    Route('/admin', handlers.AdminHandler, handler_method='index', name='admin'),
    Route('/admin/vars', handlers.AdminHandler, handler_method='vars', name='vars'),
    Route('/admin/update_vars', handlers.AdminHandler, handler_method='update_vars', name='update_vars'),
    Route('/admin/pages', handlers.AdminHandler, handler_method='pages', name='pages'),    
]