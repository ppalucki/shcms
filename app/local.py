# -*- coding: utf-8 -*
from google.appengine.ext import testbed
from admin import app
from django.utils import autoreload #@UnresolvedImport
import sys

def main():    
    from wsgiref.simple_server import make_server
    tb = testbed.Testbed()
    tb.activate()
    tb.init_datastore_v3_stub(datastore_file='local.data', save_changes=True) # Next, declare which service stubs you want to use.
    tb.init_memcache_stub()
    tb.init_user_stub()    
    tb.init_taskqueue_stub()
    tb.init_urlfetch_stub()
    tb.init_images_stub() # only for dev_appserver; use
    
    httpd = make_server('127.0.0.1', 8080, app)
    httpd.serve_forever()    

#    from paste import httpserver
#    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    # Respond to requests until process is killed        
    if '-nr' in sys.argv:
        main()
    else:
        autoreload.main(main)
    