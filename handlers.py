# -*- coding: utf-8 -*-
import webapp2
from util import render_to_response
from google.appengine.api import users
from models import Var

class BaseHandler(webapp2.RequestHandler):
        
    def _is_admin_request(self):
        return self.request.path.startswith('/admin')
        
    def dispatch(self):
        # admin permission
        if self._is_admin_request():        
            user = users.get_current_user()       
            user_can_edit = users.is_current_user_admin() or (user and user.email() in Var.get_value('admins'))
            self.user = user
            if not user_can_edit:
                if self.request.method=='POST':                    
                    self.abort(403) # just 403 - for POSTs
                else:                    
                    self.redirect(users.create_login_url(self.request.path)) # login and redirect
                        
        # super
        return super(BaseHandler, self).dispatch()

                
    def render(self, template_name, **ctx):
        ctx.update({
            'req': self.request,
            'params': self.request.params,            
        })
        if self._is_admin_request():
            ctx['user'] = self.user
        return render_to_response(template_name, **ctx)

class AdminHandler(BaseHandler):

    def index(self):
        return self.render('admin/index.html')

    def vars(self):
        return self.render('admin/vars.html', vars = Var.all())
            
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
        return self.render('home.html')
        
    
        

