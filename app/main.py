# coding: utf8
import os
from google.appengine.api import memcache
import logging

def main():
    path = os.environ['PATH_INFO']
    
    
    
    if path=='/gallery.xml':
        content_type = 'application/xml'
        key = 'gallery.xml-BROKEN!'
        location = '/r/gallery.xml'
        
    else:
        content_type = 'text/html; charset=UTF-8'
        # default to home
        if path=='/':
            path = '/home-pl'
        
        # is content requeste
        c = False
        if path.startswith('/c/'):
            c = True
            path = path.replace('/c/','')
        
        # slug without slash
        slug,lang = path.lstrip('/').split('-')                        
        # key to memcache
        key = "%s-%s"%(slug,lang)
        location = "/rp/%s-%s"%(slug,lang)        
        if c:
            location = "/rc/%s-%s"%(slug,lang)
            key = 'content-'+key
    
    body = memcache.get(key)  #@UndefinedVariable    
    if body is None:
        print "Location: %s"%location
    else:
        print "Content-Type: %s"%content_type
        print
        print body
        
if __name__ == '__main__':
    main()