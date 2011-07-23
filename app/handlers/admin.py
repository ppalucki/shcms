# -*- coding: utf-8 -*-
import webapp2
from util import render_to_response
from google.appengine.api import users
from models import Var
import logging
from forms import VarForm
from base64 import b64decode, b64encode
from google.appengine.ext import deferred
from util import update_pages, update_pages_deffered
from models import Page
from google.appengine.api import memcache
from handlers.base import BaseHandler
import yaml


class AdminHandler(BaseHandler):
    
    def _redirect_to_pages(self):
        uri = self.uri_for('pages')+'?'+self.request.query
        return self.redirect(uri)        

    def index(self):
        return self.render('admin/index.html')

    def vars(self):
        if self.request.method=='POST':
            name = self.request.params['name'] 
            forms_and_vars = []
            for var in Var.all():
                if name == var.name:
                    form = VarForm(self.request.POST, obj=var) 
                    if form.validate():
                        new_value = yaml.load(form.data['raw'])
                        Var.set_value(var.name, new_value)                        
                        self.set_flash(u'Zmienna "%s" zapisana.'%var.desc)
                        return self.redirect_to('vars')
                else:
                    form = VarForm(obj=var)                                 
                forms_and_vars.append((form,var))
        else:
            # default
            forms_and_vars = [(VarForm(obj=var),var) for var in Var.all()]
        return self.render('admin/vars.html', forms_and_vars=forms_and_vars)
    
    def update_vars(self):
        Var.update_from_settings()
        self.set_flash('Zmienne zaktualizowane.')
        return self.redirect_to('vars')
    
    def update_pages(self):        
        if self.app.debug or self.app.local:
            logging.info('debugmode:calling: update_pages')
            from gdata.client import BadAuthentication
            try:
                update_pages()
            except BadAuthentication, e:
                self.set_flash('Problem z update_pages(): %r.'%e)
                return self.redirect_to('pages')
            
            name, url = 'test',''
        else:
            logging.info('deffering "update_pages" task...')            
            task = deferred.defer(update_pages_deffered)
            name = task.name
            url = task.url
            logging.info('update_pages task "%s" at url="%s" added to queue with: enqueued=%s deleted=%s'%(name, url, task.was_enqueued,task.was_deleted))
            
        self.set_flash('Zadanie "%s" at url="%s" zakolejkowane.'%(name, url))
        return self._redirect_to_pages()

    def update_cache(self):
        cnt = 0        
        for page in Page.all():
            ok, _ = page.update_cache()
            ok2 = page.update_cache_content()
            if ok and ok2:
                cnt+=1
            
        self.set_flash(u'Odświeżono w cache %s stron.'%cnt)
        return self._redirect_to_pages()
                
    def update_page(self, slug, lang):        
        page = Page.get_by(slug, lang)
        page.update_content()
        self.set_flash(u'Treść zakutalizowana i cache odświeżony.')
        return self._redirect_to_pages()
    
    def pages(self):
        slug_filter = self.request.params.get('slug','')
        lang_filter = self.request.params.get('lang','')
        pages = Page.all().order('slug').order('lang')
        slugs = sorted(set((p.slug for p in pages)))
        langs = sorted(set((p.lang for p in pages)))
        if slug_filter:
            pages = pages.filter('slug =', slug_filter)
        if lang_filter:
            pages = pages.filter('lang =', lang_filter)            
        return self.render('admin/pages.html', 
                           pages=pages, 
                           slugs=slugs,
                           langs=langs,
                           slug_filter=slug_filter,
                           lang_filter=lang_filter)
    
    def edit_page(self, slug, lang):
        page = Page.get_by(slug, lang) 
        return self.render('admin/edit_page.html', page=page)
    
