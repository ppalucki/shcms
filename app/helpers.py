# -*- coding: utf-8 -*-
from webapp2_extras import jinja2
from google.appengine.api import users
import webapp2
import string
import settings
from models import Var

def uri_for_page(name, page):
    return webapp2.uri_for(name, slug=page.slug, lang=page.lang)

jinja2.default_config.update(
    globals=dict(
        create_login_url = users.create_login_url,
        create_logout_url = users.create_logout_url, 
        get_req = webapp2.get_request,
        uri_for = webapp2.uri_for,
        settings = settings,
        Var = Var,
        uri_for_page = uri_for_page,
        
    ),
    filters=dict(
        lower = string.lower,
        upper = string.upper
    ),
)

def render_template(template_name, **context):
    return jinja2.get_jinja2().render_template(template_name, **context)

