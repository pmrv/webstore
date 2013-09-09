# Copyright 2013 Marvin Poul
# Licensed under the Do What The Fuck You Want To License, Version 2
# See LICENSE for details or http://www.wtfpl.net/txt/copying

import json
import os, os.path
from webstore import WebStore, TempError, BadRequest


class JSONStore (WebStore):

    def __init__ (self, data_dir, *args, **kw):
        self.data_dir = data_dir
        WebStore.__init__ (self, *args, **kw)

        self.data = None

    def init (self):
        
        store = os.path.join (self.data_dir, self.uuid)
        if os.path.exists (store):
            self.data = open (store, "r+")
        else:
            raise BadRequest ("Store {} does not exist.".format (self.uuid))

    def get (self, _):
        return self.data.read ()

    def set (self, input_dict):

        try: 
            lockpath = os.path.join (self.data_dir, self.uuid + ".lck")
            lock = os.open (
                    lockpath, 
                    os.O_CREAT | os.O_EXCL
            )

            data_dict = json.load (self.data)
            data_dict.update (input_dict)

            self.data.seek (0)
            json.dump (data_dict, self.data)
            self.data.truncate ()

        except FileExistsError:
            raise TempError from None
        finally:
            os.close  (lock)
            os.remove (lockpath)

    def quit (self):

        if self.data:
            self.data.close ()

application = JSONStore ("data")
