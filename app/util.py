# -*- coding: utf-8 -*-
from google.appengine.ext import deferred
from helpers import render_template
from models import Page, Album, Photo, Var
import logging

def render_to_response(template_name, **ctx):
    import webapp2    
    return webapp2.Response(
                render_template(template_name, **ctx)
            )


def direct_render(template_name, **ctx): 
    def _direct_render(req, *args, **kw):
        ctx.update({'req':req})
        return render_to_response(template_name, **ctx)
    return _direct_render

