# -*- coding: utf-8 -*-
from google.appengine.ext import deferred
from models import Page, Album, Photo, Var
import logging

#
# --------- update pages
#
def get_doc_content(src):
    """ src - src url """
    from google.appengine.api.urlfetch import fetch, Error
    response = fetch(src, deadline=10)
    assert response.status_code == 200
    if 'Welcome to Google Docs' in response.content or 'gaia_loginbox' in response.content or "Don't have a Google Account?" in response.content:
        raise Exception(u'brak uprawnien do pobrania zawartosci strony z %s (czyzby nie byla udostepniona?)'%src)
    return response.content   

def fix_content(src):
    import BeautifulSoup
    bs = BeautifulSoup.BeautifulSoup(src)
    style = bs.head.style
    style.setString( style.text.replace('body','#body') )
    styles = style.prettify()
    # body as span
    body = bs.body
    body.name = 'span'
    body['id']='body'
    span = body.prettify()
    return span, styles

def update_pages():
    logging.info('-> updateing pages')
    from importing import get_docs_data
    docs = get_docs_data(Var.get_value('admin'),Var.get_value('password'))
    
    docs_by_keys = dict((doc['res_id'],doc) for doc in docs)
    updated_or_deleted = set()
    
    updated_cnt = deleted_cnt = created_cnt = 0  
    # updateing
    for page in Page.all():
        
        # delete
        if not page.res_id in docs_by_keys:
            page.delete()
            deleted_cnt+=1
            logging.info('page %s deleted'%page.res_id)
            updated_or_deleted.add( page.res_id )

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
            updated_cnt+=1        
            updated_or_deleted.add( page.res_id )
        
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

def update_pages_deffered():
    logging.info('-> update_pages_deffered')
    try:
        update_pages()
    except Exception:
        logging.exception('<- deffered function "update_pages" exception:')
        raise deferred.PermanentTaskFailure
    logging.info('<- update_pages_deffered')
    
#
# ---------------- photos and albums -------------------
#
def update_photos():
    logging.info('-> updateing pages')
    from importing import get_docs_data, get_albums_data
    albums = get_albums_data(Var.get_value('admin'),Var.get_value('password'))
    
    docs_by_keys = dict((album['res_id'],album) for album in albums)    
    updated_or_deleted = set()
    
    updated_cnt = deleted_cnt = created_cnt = 0  
    pupdated_cnt = pdeleted_cnt = pcreated_cnt = 0
    # updateing
    for album in Album.all():        
        # delete
        if not album.res_id in docs_by_keys:
            for photo in album.photos:
                photo.delete()
                logging.info('photo %s deleted (in album=%s)', photo.res_id, album.res_id)
                pdeleted_cnt+=1
            album.delete()
            deleted_cnt+=1
            logging.info('album %s deleted'%album.res_id)
            updated_or_deleted.add( album.res_id )

        else:        
            # update existing album 
            doc = docs_by_keys[album.res_id]
            album.title = doc['title']
            album.put()            
            logging.info('album %s updated'%doc['res_id'])
            updated_or_deleted.add( album.res_id )            
            
            ######################
            # update/delete his photos            
            pupdated_or_deleted=set()
            pdocs_by_keys = dict( (pdoc['res_id'],pdoc) for pdoc in doc['photos'])
            #add/remove/update
            for photo in album.photos:
                if not photo.res_id in pdocs_by_keys:
                    photo.delete()
                    pdeleted_cnt+=1
                    logging.info('photo %s deleted (in album=%s)', photo.res_id, album.res_id)
                else:
                    pdoc = pdocs_by_keys[photo.res_id]
                    photo.title = pdoc['title']
                    photo.src = pdoc['src']
                    photo.mimetype = pdoc['mimetype']
                    photo.height = pdoc['height']
                    photo.width = pdoc['width']      
                    photo.order = doc['photos'].index(pdoc)              
                    photo.put()
                    pupdated_cnt+=1
                    logging.info('photo %s updated (in album=%s)', photo.res_id, album.res_id)                
                pupdated_or_deleted.add(photo.res_id)
            
            ######################
            ## create new photos
            new_photos_ids = set(pdocs_by_keys) - pupdated_or_deleted
            for new_photo_id in new_photos_ids:
                pdoc = pdocs_by_keys[new_photo_id]
                Photo(
                    album=album,                
                    key_name=pdoc['res_id'],
                    src=pdoc['src'],
                    title=pdoc['title'],
                    mimetype=pdoc['mimetype'],
                    height=pdoc['height'],
                    width=pdoc['width'],
                    order=doc['photos'].index(pdoc)          
                ).put()
                logging.info('photo %s created (in album=%s)', photo.res_id, album.res_id)
                pcreated_cnt+=1        
            updated_cnt+=1
        
    # new pages
    new_albums_ids = set(docs_by_keys) - updated_or_deleted
    for new_album_id in new_albums_ids:
        doc = docs_by_keys[new_album_id]
        # create new album
        album = Album(key_name=doc['res_id'],
                      title = doc['title'])
        album.put()        
        for pdoc in doc['photos']:
            # create new photo
            Photo(
                album=album,                
                key_name=pdoc['res_id'],
                src=pdoc['src'],
                title=pdoc['title'],
                mimetype=pdoc['mimetype'],
                height=pdoc['height'],
                width=pdoc['width'],
                order=doc['photos'].index(pdoc)           
            ).put()
            pcreated_cnt+=1
            logging.info('photo %s created (in album=%s)', pdoc['res_id'], album.res_id )                        
        logging.info('album %s created'%doc['res_id'])
        created_cnt+=1
        
    logging.info('<- updateing album/photos updated=%s created=%s deleted=%s pupdated=%s pcreated=%s pdeleted=%s',
                    updated_cnt, created_cnt, deleted_cnt, pupdated_cnt, pcreated_cnt, pdeleted_cnt)


def update_photos_deffered():
    logging.info('-> update_pages_deffered')
    try:
        update_photos()
    except Exception:
        logging.exception('<- deffered function "update_pages" exception:')
        raise deferred.PermanentTaskFailure
    logging.info('<- update_pages_deffered')