# -*- coding: utf-8 -*-
# PATH mangling

import set_sys_path #@UnusedImport
# builitin libs
import os, sys
# outer libs

# Is this the development server?
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
local = (sys.argv[0] in ('local.py', 'app/local.py'))
if local:
    sys.path = map(lambda p: p.replace('app/lib.zip','lib').replace('app\\lib.zip','lib'), sys.path) # for debug replace lib.zip with local directory
    
import webapp2
import jinja2 #@UnusedImport
from pytz.gae import pytz #@UnresolvedImport


# internal libs
from urls import urls

def enable_appstats(app):
    """Enables appstats middleware."""
    from google.appengine.ext.appstats.recording import appstats_wsgi_middleware
    app.dispatch = appstats_wsgi_middleware(app.dispatch)

def enable_jinja2_debugging():
    """Enables blacklisted modules that help Jinja2 debugging."""
    from google.appengine.tools.dev_appserver import HardenedModulesHook
    HardenedModulesHook._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']
        


# Instantiate the application.
app = webapp2.WSGIApplication(urls, debug=debug)
app.local = local
app.debug = debug
#enable_appstats(app) - dont work with webapp2!  'WSGIApplication' object has no attribute 'dispatch'

def main():
    app.run()

if __name__ == '__main__':
    main()
    