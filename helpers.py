# -*- coding: utf-8 -*-
from webapp2_extras import jinja2
from google.appengine.api import users
import webapp2
import string

jinja2.default_config.update(
    globals=dict(
        create_login_url = users.create_login_url,
        create_logout_url = users.create_logout_url, 
        get_req = webapp2.get_request,             
    ),
    filters=dict(
        lower = string.lower,
        upper = string.upper
    ),
)

def render_template(template_name, **context):
    return jinja2.get_jinja2().render_template(template_name, **context)

