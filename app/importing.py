import gdata.docs.client
import settings
import gdata.photos.service
import logging

from datetime import datetime

def pr(x):
    _x = x.ToString()
    try:
        from BeautifulSoup import BeautifulSoup as BS
        print BS(_x).prettify()
    except ImportError:
        print _x
        
def get_docs_data(login, password):
    """ return all documents in format
    (slug,lang):{'id':..., 'url':..., 'title':..., 'modified':..., 'visible':True/False}
    """
    
    client = gdata.docs.client.DocsClient(source=settings.GDATA_SOURCE)
    #client.ssl = True  # Force all API requests through HTTPS
    #client.http_client.debug = False  # Set to True for debugging HTTP requests
    logging.info('auth in google docs login=%r password=%r', login, password)
    client.ClientLogin(login, password, settings.GDATA_SOURCE)
    logging.info('loading all docs ...')
    feed = client.GetDocList(uri='/feeds/default/private/full?showfolders=true')
    lang_folders=[]
    menu_folders=[]
    docs=[]
    logging.info('parsing all docs feed...')
    for entry in feed.entry:
        d = dict(
            updated_str = entry.updated.text,
            title = entry.title.text.encode('UTF-8'),
            res_id = entry.resource_id.text,
            doctype = entry.GetDocumentType(),
            parents = [link.title for link in entry.in_folders()],
            src = entry.content.src,
            etag = entry.etag,
            edit_url = entry.find_alternate_link(),
        )
        logging.info('loaded entry: %s', d['res_id'])
        
        if d['doctype']=='folder':
            if 'langs' in d['parents']:
                lang_folders.append(d)
            elif 'menu' in d['parents']:                
                menu_folders.append(d)
        elif d['doctype']=='document':
            docs.append(d)
    
    slug_folders_titles = [f['title'] for f in menu_folders]
    lang_folders_titles = [f['title'] for f in lang_folders]
    logging.info('got folders langs=%r and slugs=%s', lang_folders_titles, slug_folders_titles)
    
    # decorate docs objects with slug and lang
    good_docs = []
    for d in docs:
        langs = list(set(d['parents']).intersection(lang_folders_titles))        
        if len(langs)!=1:
            logging.warn(u'document title=%s res_id=%s nie ma dokladnie jednego lang a ma %r - ignoring this doc!', d['title'], d['res_id'], langs)
            continue
        slugs = list(set(d['parents']).intersection(slug_folders_titles))
        if len(langs)!=1:
            logging.warn(u'document title=%s res_id=%s nie ma dokladnie jednego slug a ma %r - ignoring this doc!', d['title'], d['res_id'], slugs)
            continue
        
        d['lang']=langs[0]
        d['slug']=slugs[0]
        d.pop('doctype')
        d.pop('parents')        
        d['updated'] = datetime.strptime(d.pop('updated_str').split('.')[0], '%Y-%m-%dT%H:%M:%S')  
        good_docs.append(d)
    logging.info('returning %s documents', len(good_docs))
    return good_docs


def get_albums_data(login, password):
    """ pobierz informacje o obrazkach w postaci
    [{'access': 'public',
      'photos': [{'height': 142,
                  'mimetype': 'image/jpeg',
                  'res_id': '5628231016260042338',
                  'src': 'https://lh5.googleusercontent.com/-
                  'title': u'Restaurant Zimmer.jpg',
                  'width': 254}.....

    """
    logging.info('auth in google photos')
    gd_client = gdata.photos.service.PhotosService()
    gd_client.email = login 
    gd_client.password = password
    gd_client.source = settings.GDATA_SOURCE
    gd_client.ProgrammaticLogin()
    logging.info('loading albums...')
    feed = gd_client.GetUserFeed()
    
    albums=[]
    logging.info('parsing albums...')
    for album in feed.entry:
        if album.access.text=='private':
            continue
        ad = dict(
            title = album.title.text,
            res_id = album.gphoto_id.text,
            access = album.access.text,
            photos = [],
        )
        logging.info('loading photos from album %s ...', ad['res_id'])        
        photos = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (login, album.gphoto_id.text))        
        for photo in photos.entry:
            pd = dict(
                res_id = photo.gphoto_id.text,
                title = photo.title.text.decode('utf8'),
                width = int(photo.width.text),
                height = int(photo.height.text),
                mimetype = photo.content.type,
                src = photo.content.src,                
            )
            logging.info('got photo: %s', pd['res_id'])
            ad['photos'].append(pd)
        logging.info('got %s photos', len(ad['photos']))
        albums.append(ad)
    logging.info('returning %s albums', len(albums))
    return albums
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys
    PASSWORD=sys.argv[1]    
    docs = get_docs_data('skicms@gmail.com', PASSWORD)
    albums = get_albums_data('skicms@gmail.com', PASSWORD)
    from pprint import pprint
    pprint(albums)
    pprint(docs)
    
    