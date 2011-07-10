# -*- coding: utf-8 -*-
import webapp2
from util import render_to_response
from google.appengine.api import users
from models import Var
import logging
from forms import VarForm
import sys
from base64 import b64decode, b64encode
log = logging.getLogger()

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
                
            can_edit = is_admin or (user is not None and (user.email() in Var.get_value('admins')))            
            log.info('current_user: admin=%s can_edit=%s', users.is_current_user_admin(), can_edit)            
            if not can_edit:
                if self.request.method=='POST':                                        
                    self.abort(403) # just 403 - for POSTs
                else:                    
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
        if self.new_flash is None and resp.status_int==200:
            resp.delete_cookie('flash')
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
        self.pre_dispatch_admin()
                                
        # super
        resp = super(BaseHandler, self).dispatch()
        
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
                        form.populate_obj(var)
                        var.put()   
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
                    
    def pages(self):
        return self.render('admin/pages.html')

class TestHandler(BaseHandler):
    """ handler do testow srodowiska """
    
    def hello(self):        
        return webapp2.Response('hello')
    
    def template(self):
        return self.render('test/template.html')
    
class HomeHandler(BaseHandler):
    def get(self):
        r = self.render('home.html')
        print >>sys.stderr, r
        return r
        
    
        

