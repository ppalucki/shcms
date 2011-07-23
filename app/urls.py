# -*- coding: utf-8 -*-
from webapp2 import Route
from handlers import admin, static, dynamic

urls = [    
    # admin
    Route(r'/admin', admin.AdminHandler, handler_method='index', name='admin'),
    Route(r'/admin/vars', admin.AdminHandler, handler_method='vars', name='vars'),
    Route(r'/admin/update_vars', admin.AdminHandler, handler_method='update_vars', name='update_vars'),
    Route(r'/admin/pages', admin.AdminHandler, handler_method='pages', name='pages'),
    Route(r'/admin/update_pages', admin.AdminHandler, handler_method='update_pages', name='update_pages'),
    Route(r'/admin/update_page/<slug>-<lang>', admin.AdminHandler, handler_method='update_page', name='update_page'),
    Route(r'/admin/edit_page/<slug>-<lang>', admin.AdminHandler, handler_method='edit_page', name='edit_page'),

    # dynamic
    Route(r'/rp/<slug>-<lang>', dynamic.DynamicHandler, handler_method='refresh_page', name='refresh_page'),
    Route(r'/dp/<slug>-<lang>', dynamic.DynamicHandler, handler_method='dynamic_page', name='dynamic_page'),
    
    # static (Local)  
    Route(r'/<slug>-<lang>', static.StartHandler, handler_method='static_page', name='static_page'),
    Route(r'/', static.StartHandler, handler_method='home_page', name='home_page'),
    Route(r'/static/<path>', static.StartHandler, handler_method='static', name='static'),
    Route(r'/favicon.ico', static.StartHandler, handler_method='favicon'),
    
]