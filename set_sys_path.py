# -*- coding: utf-8 -*-
"""Sets sys.path for the library directories."""
import os
import sys

current_path = os.path.abspath(os.path.dirname(__file__))

# Add lib as primary libraries directory, with fallback to lib/dist
# and optionally to lib/dist.zip, loaded using zipimport.
sys.path[0:0] = [
    os.path.join(current_path, 'lib'),
    os.path.join(current_path, 'lib.zip'),
]

import dev_appserver
dev_appserver.fix_sys_path()
from google.appengine.dist import use_library
use_library('django', '1.2')
