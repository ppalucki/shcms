# -*- coding: utf-8 -*-
# PATH mangling

import set_sys_path #@UnusedImport
# builitin libs
import os, sys
# outer libs
import webapp2
import jinja2 #@UnusedImport


# internal libs
from urls import urls

debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

def enable_appstats(app):
    """Enables appstats middleware."""
    from google.appengine.ext.appstats.recording import appstats_wsgi_middleware
    app.dispatch = appstats_wsgi_middleware(app.dispatch)

def enable_jinja2_debugging():
    """Enables blacklisted modules that help Jinja2 debugging."""
    from google.appengine.tools.dev_appserver import HardenedModulesHook
    HardenedModulesHook._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']
        
# Is this the development server?
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

# Instantiate the application.
app = webapp2.WSGIApplication(urls, debug=debug)
app.local = False
#enable_appstats(app) - dont work with webapp2!  'WSGIApplication' object has no attribute 'dispatch'

def main():
    app.run()

if __name__ == '__main__':
    main()
    