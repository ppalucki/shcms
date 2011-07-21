# -*- coding: utf-8 -*-
from data import get_docs_data, get_albums_data
from google.appengine.ext import deferred
from helpers import render_template
from models import Page, Album, Photo, Var
import logging
import webapp2

def render_to_response(template_name, **ctx):    
    return webapp2.Response(
                render_template(template_name, **ctx)
            )


def direct_render(template_name, **ctx): 
    def _direct_render(req, *args, **kw):
        ctx.update({'req':req})
        return render_to_response(template_name, **ctx)
    return _direct_render

def get_doc_content(src):
    """ src - src url """
    from google.appengine.api.urlfetch import fetch, Error
    response = fetch(src, deadline=10)
    assert response.status_code == 200
    if 'Welcome to Google Docs' in response.content or 'gaia_loginbox' in response.content or "Don't have a Google Account?" in response.content:
        raise Exception(u'brak uprawnien do pobrania zawartosci strony z %s (czyzby nie byla udostepniona?)'%src)
    return response.content   


        
def update_pages():
    logging.info('-> updateing pages')
    docs = get_docs_data(Var.get_value('admin'),Var.get_value('password'))
    
    docs_by_keys = dict((doc['res_id'],doc) for doc in docs)
    updated_or_deleted = set()
    
    updated_cnt = deleted_cnt = created_cnt = 0  
    # updateing
    for page in Page.all():
        
        # delete
        if not page.res_id in docs_by_keys:
            logging.info('page %s deleted'%page.res_id)
            page.delete()
            deleted_cnt+=1

        else:        
            doc = docs_by_keys[page.res_id]
            # update existing
            page.slug = doc['slug']
            page.lang = doc['lang']
            page.title = doc['title']
            page.etag = doc['etag']
            page.updated = doc['updated']
            page.content = get_doc_content(doc['src'])
            page.src = doc['src']
            page.edit_url = doc['edit_url']
            page.put()            
            logging.info('page %s updated'%doc['res_id'])            
            updated_or_deleted.add( page.key().name() )
            updated_cnt+=1
        
    # new pages
    new_pages_ids = set(docs_by_keys) - updated_or_deleted
    for new_page_id in new_pages_ids:
        doc = docs_by_keys[new_page_id]
        # create new page
        page = Page(key_name=doc['res_id'],
            slug = doc['slug'],
            lang = doc['lang'],
            title = doc['title'],
            etag = doc['etag'],
            updated = doc['updated'],
            src = doc['src'],
            edit_url = doc['edit_url'],
            content = get_doc_content(doc['src']),
        )
        page.put()        
        logging.info('page %s created'%doc['res_id'])
        created_cnt+=1
        
    logging.info('<- updateing pages updated=%s created=%s deleted=%s'%(updated_cnt, created_cnt, deleted_cnt))


def update_photos():
    albums = get_albums_data()
    pass

def update_pages_deffered():
    logging.info('-> update_pages_deffered')
    try:
        update_pages()
    except Exception:
        logging.exception('<- deffered function "update_pages" exception:')
        raise deferred.PermanentTaskFailure
    logging.info('<- update_pages_deffered')