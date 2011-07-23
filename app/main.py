# coding: utf8
import os
from google.appengine.api import memcache
import logging

def main():
    path = os.environ['PATH_INFO']
    
    c = False
    # default to home
    if path=='/':
        path = '/home-pl'
        
    if path.startswith('/c/'):
        c = True
        path = path.replace('/c/','')

    # slug without slash
    slug,lang = path.lstrip('/').split('-')                        
    # key to memcache
    key = "%s-%s"%(slug,lang)
    if c:
        key = 'content-'+key
    
    body = memcache.get(key)  #@UndefinedVariable
    
    logging.info('key=%r body=%r', key, body)
    if body is None:
        logging.info('refresh!')
        if c:
            print "Location: /rc/%s-%s"%(slug,lang)
        else:
            print "Location: /rp/%s-%s"%(slug,lang)
    else:
        print "Content-Type: text/html; charset=UTF-8"
        print
        print body
        
if __name__ == '__main__':
    main()