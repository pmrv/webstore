# Copyright 2013 Marvin Poul
# Licensed under the Do What The Fuck You Want To License, Version 2
# See LICENSE for details or http://www.wtfpl.net/txt/copying

import json
import os.path
from webstore import WebStore

class JSONStore (WebStore):

    def __init__ (self, data_dir, **kw):
        self.data_dir = data_dir
        WebStore.__init__ (self, **kw)

    def init (self, uuid):
        
        store = os.path.join (self.data_dir, uuid)
        if os.path.exists (store):
            self.data = open (store, "r+")
        else:
            raise BadRequest ("Store {} does not exist.".format (store))

    def get (self, _):
        return self.data.read ()

    def set (self, input_dict):

        data_dict = json.load (self.data)
        data_dict.update (input_dict)

        self.data.seek (0)
        json.dump (data_dict, self.data)
        self.data.truncate ()

application = JSONStore ("data")
