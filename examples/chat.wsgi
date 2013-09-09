import os.path
from webstore import WebStore

class Chat (WebStore):

    def __init__ (self, log_dir, *args, **kw):

        WebStore.__init__ (self, *args, **kw)
        self.log_dir  = log_dir
        self.data = None

        self.errors = []

    def init (self):
        logfile = os.path.join (self.log_dir, self.uuid)
        self.data = open (logfile, "a+")

    def quit (self):
        if self.data:
            self.data.close ()
            self.data = None

    def get (self, _):

        self.data.seek (0)
        hist = self.data.read ()
        return {"history": hist}

    def set (self, input_data):

        msg = input_data.get ("message", "")
        self.data.write (msg)

application = Chat ("/var/www/lab/chatlogs")
