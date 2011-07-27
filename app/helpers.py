# -*- coding: utf-8 -*-
from webapp2_extras import jinja2
from google.appengine.api import users
import webapp2
import string
import settings
from models import Var, Album

def url_for_page(name, page, lang=None):
    return webapp2.uri_for(name, slug=page.slug, lang=lang or page.lang)

def url_for_flag(lang, type):
    return '/static/flags/%s/%s'%(lang,type)

def lang_img(lang, type='small.png', current=False):
    return '<img class="flag%s" src="%s" alt="%s" />'%((' current_flag' if current else ''),url_for_flag(lang, type), lang)

def lang_link(lang, href, type='small.png', current=False):
    return '<a class="flag" href="%s">%s</a>'%( href, lang_img(lang, type, current)) 

jinja2.default_config.update(
    globals=dict(
        create_login_url = users.create_login_url,
        create_logout_url = users.create_logout_url, 
        get_req = webapp2.get_request,
        uri_for = webapp2.uri_for,
        settings = settings,
        Var = Var,
        Album = Album,
        url_for_page = url_for_page,
        url_for_flag = url_for_flag,
        lang_img = lang_img,
        lang_link = lang_link        
    ),
    filters=dict(
        lower = string.lower,
        upper = string.upper
    ),
)

def render_template(template_name, **context):
    return jinja2.get_jinja2().render_template(template_name, **context)

