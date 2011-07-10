# -*- coding: utf-8 -*-
from webapp2 import Route
from util import direct_render
import handlers

urls = [    
# test urls
Route('/test/hello', handlers.TestHandler, handler_method='hello'),
Route('/test/template', handlers.TestHandler, handler_method='template'),
Route('/test/direct', direct_render('test/direct.html', foo='bar') ),

# admin urls
Route('/admin', handlers.AdminHandler),

# main urls
Route('/', handlers.HomeHandler, name='home')
]