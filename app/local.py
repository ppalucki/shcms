# -*- coding: utf-8 -*
from app import app # to powoduje ustawienie odpowiedni sciezek!
def initstubs():
    from google.appengine.ext import testbed
    import logging
    logging.basicConfig(level=logging.DEBUG) 
    tb = testbed.Testbed()
    tb.activate()
    tb.init_datastore_v3_stub(datastore_file='local.data', save_changes=True) # Next, declare which service stubs you want to use.
    tb.init_memcache_stub()
    tb.init_user_stub()    
    tb.init_taskqueue_stub()
    tb.init_urlfetch_stub()
    tb.init_images_stub() # only for dev_appserver; use
    return app

def main():   
    app = initstubs()
    from wsgiref.simple_server import make_server
    httpd = make_server('127.0.0.1', 8080, app)
    httpd.serve_forever()
#    from paste import httpserver
#    httpserver.serve(app, host='127.0.0.1', port='8080')

def pyshell():
    initstubs()
    from models import Album, Photo, Var, Page
    ### PUT CODE HERE
    # ...
    from tasks import update_photos
    update_photos()
    ### SHELL START!
    from wx.py.PyShell import main; main(dict(globals(), ** locals())) #@UnresolvedImport

if __name__ == '__main__':
    # Respond to requests until process is killed
    import sys     
    if '-sh' in sys.argv:
        pyshell()     
    elif '-nr' in sys.argv:
        main()
    else:
        import autoreload 
        autoreload.main(main)
    