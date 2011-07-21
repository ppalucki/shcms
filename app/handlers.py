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



class BaseHandler(webapp2.RequestHandler):
    #
    # --- admin middleware
    #
    def _is_admin_request(self):
        return self.request.path.startswith('/admin')
        
    def pre_dispatch_admin(self):
        """ sprawdzenie dostepu do panelu admina """
        if self._is_admin_request():
            if self.app.local:
                class User():
                    def nickname(self):
                        return 'test'
                    def email(self):
                        return 'test@example.com'
                self.user = user = User()
                is_admin = True
            else:
                self.user = user = users.get_current_user()
                is_admin = users.is_current_user_admin()                
            can_edit = is_admin or (user is not None and (user.email()==Var.get_value('admin')))            
            logging.debug('current_user: admin=%s can_edit=%s', users.is_current_user_admin(), can_edit)            
            if not can_edit:
                if self.request.method=='POST':                                        
                    self.abort(403) # just 403 - for POSTs
                else:                    
                    if user:
                        # not admin 
                        return self.render('admin/login.html')                        
                    else:
                        # not authorized user so go to login
                        return self.redirect(users.create_login_url(self.request.path)) # login and redirect
            assert can_edit and user is not None
        
    #
    # --- lang middleware
    #
    def pre_dispatch_lang(self):
        if 'lang' in self.request.cookies:
            self.lang = self.request.cookies['lang']
        else:
            self.lang = Var.get_value('langs')[0]        
        
    def post_dispatch_lang(self, resp):
        cookie_lang = self.request.cookies.get('lang',None)  
        if cookie_lang != self.lang:
            resp.set_cookie('lang', value=self.lang)
        return resp
    
    #
    # --- flash middleware
    #
    def set_flash(self, flash):
        self.new_flash = flash
        
    def pre_dispatch_flash(self):
        self.new_flash = None
        if 'flash' in self.request.cookies:
            try:
                self.flash = b64decode(self.request.cookies['flash']).decode('utf8')
            except ValueError:
                self.flash = None
        else:
            self.flash = None        
        
    def post_dispatch_flash(self, resp):
        if self.new_flash is None:
            if resp.status_int==200:
                # jesli strona 200 i nie ma nowego flash - to skasuj stary
                resp.delete_cookie('flash')
            else:
                # jesli np. przekierowanie to nie kasuje starego ciasteczka
                pass            
        else:          
            assert self.new_flash
            resp.set_cookie('flash', b64encode(self.new_flash.encode('utf8')))
        return resp    

    #
    # --- dispatch
    # 
    
    def dispatch(self):
        # before
        self.pre_dispatch_lang()
        self.pre_dispatch_flash()
        resp = self.pre_dispatch_admin()
        if resp is not None:
            return resp
                                
        # super
        resp = super(BaseHandler, self).dispatch()
        
        ### helper if resp is string
        if isinstance(resp, basestring):
            resp = webapp2.Response(resp)
        
        # after
        resp = self.post_dispatch_lang(resp)
        resp = self.post_dispatch_flash(resp)
        return resp
     
    def render(self, template_name, **ctx):
        ctx.update({
            'req': self.request,
            'params': self.request.params, 
            'handler': self           
        })
        if self._is_admin_request():
            ctx['user'] = self.user
            assert self.user is not None
        return render_to_response(template_name, **ctx)

class AdminHandler(BaseHandler):

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
                        Var.set_value(var.name, form.data['raw'])                        
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
        return self.redirect_to('pages')
                
    def update_page(self, res_id):
        page = Page.get_by_res_id(res_id)
        page.update_content()
        self.set_flash(u'Treść zakutalizowana i cache odświeżony.')
        return self.redirect_to('pages')
    
    def refresh_page(self, slug):
        """ wywolywane do odswiezenia strony przy braku w cache """
        page = Page.get_by_slug(slug, self.lang)
        if page is None:
            self.abort(404)
        ok = page.update_cache()             
        if ok:
            return self.redirect('/%s'%slug)
        else:
            self.abort(400)
                
    def pages(self):        
        return self.render('admin/pages.html', pages=Page.all())

class TestHandler(BaseHandler):
    """ handler do testow srodowiska """
    
    def hello(self):        
        return webapp2.Response('hello')
    
    def template(self):
        return self.render('test/template.html')
    
class HomeHandler(BaseHandler):
    def get(self):
        r = self.render('home.html')
        return r
        
class DynamicHandler(BaseHandler):
    def get(self, slug):
        page = Page.get_by_slug(slug, self.lang)       
        if page is None:
            self.abort(404)
        content = page.render_content()
        if not content:
            self.abort(404)
        return content
        
