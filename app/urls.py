# -*- coding: utf-8 -*-
from webapp2 import Route
from handlers import admin, static, dynamic

def RF(url, handler_func=None):
    """ route factory """
    if handler_func is not None:
        handler = handler_func.im_class
        name = handler_func.__name__
    else:
        handler = admin.AdminHandler        
        name = url.split('/')[-1]    
    return Route(url, handler, handler_method=name, name=name)

urls = [    
    # admin
    RF(r'/admin'),
    RF(r'/admin/vars'),
    RF(r'/admin/update_vars'),
    RF(r'/admin/pages'),
    RF(r'/admin/update_pages'),
    RF(r'/admin/update_cache'),
    RF(r'/admin/update_page/<slug>-<lang>', admin.AdminHandler.update_page),
    RF(r'/admin/edit_page/<slug>-<lang>', admin.AdminHandler.edit_page),

    # dynamic
    RF(r'/rp/<slug>-<lang>', dynamic.DynamicHandler.refresh_page),
    RF(r'/rc/<slug>-<lang>', dynamic.DynamicHandler.refresh_content),
    RF(r'/dp/<slug>-<lang>', dynamic.DynamicHandler.dynamic_page),
    RF(r'/dc/<slug>-<lang>', dynamic.DynamicHandler.dynamic_content),
    
    # static (Local)  
    RF(r'/<slug>-<lang>',    static.StartHandler.static_page),
    RF(r'/c/<slug>-<lang>',  static.StartHandler.static_content),    
    RF(r'/',                 static.StartHandler.home_page),
    RF(r'/static/<path:.*>', static.StartHandler.static),
    RF(r'/favicon.ico',       static.StartHandler.favicon),
    
]