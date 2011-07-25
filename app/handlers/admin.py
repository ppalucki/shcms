# -*- coding: utf-8 -*-
import webapp2
from util import render_to_response
from google.appengine.api import users
from models import Var, Photo, Album
import logging
from forms import VarForm
from base64 import b64decode, b64encode
from google.appengine.ext import deferred

from models import Page
from google.appengine.api import memcache
from handlers.base import BaseHandler
import yaml


class AdminHandler(BaseHandler):

    #
    # ------------ utilki 
    # 
    def _redirect_to_pages(self):
        uri = self.uri_for('pages')+'?'+self.request.query
        return self.redirect(uri)        

    def _run_task(self, task_func, deffered_task_func):
        if self.app.debug or self.app.local:
            from gdata.client import BadAuthentication
            logging.info('debugmode:calling: %s'%task_func.__name__)
            try:
                task_func()
            except BadAuthentication, e:
                self.set_flash('Problem z %s(): %r.'%(task_func.__name__, e))
                return self.redirect_to('pages')
            
            name, url = 'test',''
        else:
            logging.info('deffering "%s" task...'%task_func.__name__)            
            task = deferred.defer(deffered_task_func)
            name = task.name
            url = task.url
            logging.info('"%s" task "%s" at url="%s" added to queue with: enqueued=%s deleted=%s'%(
                           task_func.__name__, name, url, task.was_enqueued, task.was_deleted))
        return name, url

    def admin(self):
        """ strona glowna admin """
        return self.render('admin/admin.html')
    
    #
    # --- ustawienia ---
    #
    def vars(self):
        """ strona edycji ustawien portalu """
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
        """ wczytanie zmiennych z settings """
        Var.update_from_settings()
        self.set_flash('Zmienne zaktualizowane.')
        return self.redirect_to('vars')
    
    #
    # --- strony ---
    #
    def update_pages(self):
        """ wczytanie stron z google-docs """
        from tasks import update_pages, update_pages_deffered
        name, url = self._run_task(update_pages, update_pages_deffered )        
        self.set_flash('Zadanie "%s" at url="%s" zakolejkowane.'%(name, url))
        return self._redirect_to_pages()

    def update_cache(self):
        """ odswiezenie calego cachu stron """
        cnt = 0        
        for page in Page.all():
            ok, _ = page.update_cache()
            ok2 = page.update_cache_content()
            if ok and ok2:
                cnt+=1
            
        self.set_flash(u'Odświeżono w cache %s stron.'%cnt)
        return self.redirect_to('admin')
                
    def update_page(self, slug, lang):
        """ odswiezenie contentu jednej strony """        
        page = Page.get_by(slug, lang)
        page.update_content()
        self.set_flash(u'Treść zakutalizowana i cache odświeżony.')
        return self._redirect_to_pages()
    
    def pages(self):
        """ edycja strona w panelu admina (z obsluga filtrow) """
        slug_filter = self.request.params.get('slug','')
        lang_filter = self.request.params.get('lang','')
        pages = Page.get_all_pages(slug_filter=slug_filter, lang_filter=lang_filter)
        assert all(p.lang for p in pages)
        return self.render('admin/pages.html', 
                           pages = pages,
                           slugs = Page.get_all_slugs_for_admin(),
                           langs = Page.get_all_langs_for_admin(),
                           slug_filter = slug_filter,
                           lang_filter = lang_filter)
    
    def edit_page(self, slug, lang):
        """ pomocnicza edycja strone z iframe z google-docs """ 
        page = Page.get_by(slug, lang) 
        return self.render('admin/edit_page.html', page=page)
    
    #
    # --- photos ---
    #
    def photos(self):
        """ zwroc strone ze zdjeciami """
        albums = Album.all()
        return self.render('admin/photos.html', albums=albums)
    
    def update_photos(self):        
        """ wczytanie zdjec z picassa """
        from tasks import update_photos, update_photos_deffered
        name, url = self._run_task(update_photos, update_photos_deffered )        
        self.set_flash('Zadanie "%s" at url="%s" zakolejkowane.'%(name, url))
        return self.redirect_to('photos')
