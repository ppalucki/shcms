# coding: utf8
import os, sys
from google.appengine.api import memcache
import time, datetime

s0 = time.time()

def main():
    s = time.time()
    path = os.environ['PATH_INFO']
    q = os.environ['QUERY_STRING']
    refresh = 'ref' in q
    try:
        cookies = os.environ['HTTP_COOKIE']
        lang = filter(lambda v:v.startswith('lang='), (i.strip() for i in cookies.split(';')))[0].replace('lang=','')
    except (IndexError,KeyError):
        lang = 'pl'
    key = "%s@%s"%(path,lang)
    
    print "Content-Type: text/html"
    print ""
    print "<pre>Page=", key    
    body = memcache.get(key)  #@UndefinedVariable
    if body is None or refresh:        
        body = str(datetime.datetime.now())+""" a ac accumsan ad adipiscing aenean aliquam aliquet amet ante aptent arcu at auctor augue bibendum blandit class commodo condimentum congue consectetuerconsequat conubia convallis cras cubilia """*10
        memcache.set(key, body) #@UndefinedVariable
    print
    n = time.time()
    print 'rendered in %.3f (%.3f) </pre>'%(n-s, n-s0)
    print 
    print body

if __name__ == '__main__':
    main()