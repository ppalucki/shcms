# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, HandlerPrefixRoute
from util import direct_render
import handlers

urls = [    
    # test urls
    Route(r'/test/hello', handlers.TestHandler, handler_method='hello'),
    Route(r'/test/template', handlers.TestHandler, handler_method='template'),
    Route(r'/test/direct', direct_render('test/direct.html', foo='bar') ),
    
    # admin urls
    Route(r'/admin', handlers.AdminHandler, handler_method='index', name='admin'),
    Route(r'/admin/vars', handlers.AdminHandler, handler_method='vars', name='vars'),
    Route(r'/admin/update_vars', handlers.AdminHandler, handler_method='update_vars', name='update_vars'),
    Route(r'/admin/pages', handlers.AdminHandler, handler_method='pages', name='pages'),
    Route(r'/admin/update_pages', handlers.AdminHandler, handler_method='update_pages', name='update_pages'),
    Route(r'/admin/update_page/<res_id>', handlers.AdminHandler, handler_method='update_page', name='update_page'),
    
    # specjalne urle
    Route(r'/rp/<slug>', handlers.AdminHandler, handler_method='refresh_page', name='refresh_page'),
    Route(r'/d/<slug>', handlers.DynamicHandler),
]