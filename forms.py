# -*- coding: utf-8 -*-
#from wtforms.ext.appengine.db import model_form
from wtforms import BooleanField, Form, ValidationError, TextField
from wtforms.validators import Required
from models import Var
import yaml
from yaml.error import YAMLError

class VarForm(Form):
    
    raw = TextField(u'wartość', [Required()])
    
    def __init__(self, *args, **kw):
        assert 'obj' in kw
        self.obj = kw['obj']
        super(VarForm, self).__init__(*args, **kw)
    
    def validate_raw(self, field):
        try:
            new_value = yaml.load(field.data)
        except YAMLError, e:
            raise ValidationError('yaml scanner error:%s'%e)
            
        old_value = yaml.load(self.obj.raw)
        
        if type(new_value) != type(old_value):
            raise ValidationError(u'zły typ - oczekiwano=%r a dostałem=%r'%(
                                        type(old_value), type(new_value)))
 
        
        
