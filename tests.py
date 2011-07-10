# -*- coding: utf-8 -*-
import nose, unittest
from nose.tools import eq_, assert_raises #@UnresolvedImport
import set_sys_path #@UnusedImport

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
from models import Var,Page
import settings
import urllib
from main import app

class CMSTestCase(unittest.TestCase):    
    
    def __init__(self, *args, **kw):
        tb = testbed.Testbed()    
        tb.activate() # First, create an instance of the Testbed class.    
        tb.init_datastore_v3_stub() # Next, declare which service stubs you want to use.
        tb.init_memcache_stub()
        
        self.resp = None
        super(CMSTestCase, self).__init__(*args, **kw)

        
    def get(self, url, **kw):
        """ GET with query_string in kw """
        headers = kw.pop('headers', None)
        if kw:
            url = '%s?%s'%(url, urllib.urlencode(kw))
        self.resp = app.get_response(url, headers=headers)
        return self.resp

    def post(self, url, **kw):
        """ POST with data in kw """
        headers = kw.pop('headers', None)
        self.resp = app.get_response(url, headers=headers, POST=kw)
        return self.resp
        
    #
    # my asserts
    #
    def as200(self):        
        eq_(self.resp.status_int, 200)
    
    def asContains(self, *words):
        for word in words:
            assert word in self.resp.body, 'brakuje=%r w resp.body!'%(word)
        
    
    #
    # ------------- tests ------------------
    # 
    def test_vars_models(self):
        langs = settings.VARS['langs'][1] # desc/value
        eq_(Var.all().count(), 0)
        # jeszcze nie ma w cache
        eq_(memcache.get('Var-langs'), None) #@UndefinedVariable
        # zapytujemy - dociaga z config i wklada do cache    
        eq_(Var.get_value('langs'), langs)
        # juz jest w cache
        eq_(memcache.get('Var-langs'), langs) #@UndefinedVariable
        # ale jszcze nic nie mamy w datastore
        eq_(Var.all().count(), 0) # still zero
        
        # ladujemy z config
        Var.update_from_settings()
        eq_(Var.all().count(), 4)
        
        # wciaz 4
        Var.update_from_settings()
        eq_(Var.all().count(), 4)
        
        # aktulizuemy zmienna ale ze zlym typem (nie zgadza sie z poprzednim)
        assert_raises(ValueError, Var.set_value, 'langs', 1)
        
        # aktualizujemy zmienna 
        newvalue = ['foo', 'bar']   
        Var.set_value('langs', newvalue)
        
        eq_(memcache.get('Var-langs'), newvalue) #@UndefinedVariable
        memcache.delete('Var-langs') #@UndefinedVariable
        eq_(Var.get_value('langs'), newvalue)
        eq_(memcache.get('Var-langs'), newvalue) #@UndefinedVariable

    def test_base(self):
        """ podstawowe widoki do testowania cms """
        self.get('/test/direct?x=2')
        self.asContains('* x=2', 'foo:bar', '/test/direct')
        
        self.get('/test/hello')
        self.asContains('hello')
        
        self.get('/test/template')
        
        

    def test_edit_vars(self):
        pass
    
    def test_homepage(self):
        self.get('/')
        self.as200() 
        
        self.get('/admin')
        
        


if __name__ == '__main__':
    nose.main()
