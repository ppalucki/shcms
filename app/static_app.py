# coding: utf8
import os
from google.appengine.api import memcache
import logging

def main():
    path = os.environ['PATH_INFO']
    refresh = 'ref' in os.environ['QUERY_STRING']
    
    # default to home
    if path=='/':
        path = '/home-pl'

        
    # slug without slash
    slug,lang = path.lstrip('/').split('-')                        
    # key to memcache
    key = "%s-%s"%(slug,lang)
    
    body = memcache.get(key)  #@UndefinedVariable
    if body is None or refresh:
        logging.info('refresh!')
        print "Location: /rp/%s-%s"%(slug,lang)
    else:
        logging.info('got! %s')
        print "Content-Type: text/html; charset=UTF-8"
        print body
        
if __name__ == '__main__':
    main()