# -*- coding: utf-8 -*-
from models import Page
from handlers.base import BaseHandler

class DynamicHandler(BaseHandler):
    
    def dynamic_page(self, slug, lang):
        """ dynamiczna strona """
        page = Page.get_by(slug, lang)       
        if page is None:
            self.abort(404)
        content = page.render_content()
        if not content:
            self.abort(404)
        return content
    
    def refresh_page(self, slug, lang):
        """ wywolywane do odswiezenia strony przy braku w cache """
        page = Page.get_by(slug, lang)
        if page is None:
            self.abort(404)
        ok, content = page.update_cache()             
        if ok:
            return self.redirect('/%s-%s'%(slug,lang))
        else:
            self.abort(400)   