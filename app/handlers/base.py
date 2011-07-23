# -*- coding: utf-8 -*-
import webapp2
from util import render_to_response
from google.appengine.api import users
from models import Var
import logging
from base64 import b64decode, b64encode



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
        self.pre_dispatch_flash()
        resp = self.pre_dispatch_admin()
        if resp is not None:
            return resp
                                
        # super
        resp = super(BaseHandler, self).dispatch()
        
        ### helper if resp is string
        if isinstance(resp, basestring):
            resp = webapp2.Response(resp)
        
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