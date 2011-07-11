# -*- coding: utf-8 -*-
import webapp2
from helpers import render_template
import logging
log = logging.getLogger(__name__)

def render_to_response(template_name, **ctx):    
    return webapp2.Response(
                render_template(template_name, **ctx)
            )


def direct_render(template_name, **ctx): 
    def _direct_render(req, *args, **kw):
        ctx.update({'req':req})
        return render_to_response(template_name, **ctx)
    return _direct_render