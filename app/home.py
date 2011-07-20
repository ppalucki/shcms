# coding: utf8
import os, sys
import time, datetime
from google.appengine.api import memcache
import logging

def main():
    path = os.environ['PATH_INFO']
    q = os.environ['QUERY_STRING']
    refresh = 'ref' in q
    
    # lang from cookie
    try:
        cookies = os.environ['HTTP_COOKIE']
        lang = filter(lambda v:v.startswith('lang='), (i.strip() for i in cookies.split(';')))[0].replace('lang=','')
    except (IndexError,KeyError):
        lang = 'pl' # default lang
    
    # default to home
    if path=='/':
        path = '/home'
        
    # slug without slash
    slug = path.lstrip('/')                    
    
    # key to memcache
    key = "%s@%s"%(slug,lang)
    
    body = memcache.get(key)  #@UndefinedVariable
    if body is None or refresh:
        logging.info('refresh!')
        print "Location: /rp/%s"%slug
    else:
        logging.info('got! %s')
        print "Content-Type: text/html; charset=UTF-8"
        print body
        
if __name__ == '__main__':
    main()