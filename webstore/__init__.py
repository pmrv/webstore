# Copyright 2013 Marvin Poul
# Licensed under the Do What The Fuck You Want To License, Version 2
# See LICENSE for details or http://www.wtfpl.net/txt/copying

from wsgiref.util import shift_path_info
from urllib.parse import parse_qs
import cgi, json, gzip 

class BadRequest (Exception): pass
class TempError  (Exception): pass

class WebStore:

    def __init__ (self, get_path = "get", set_path = "set"):
        """
        set_path -- str, under which relative url the set functionality is reachable
        get_path -- str, analogous to set_path, both cannot have '/' in them

        i.e. the full url is then {app_mount_point}/{uuid}/{[sg]et_path}
        """

        self.paths = {
            get_path: self.get_skeleton, 
            set_path: self.set_skeleton,
        }

        self.errors = {
            BadRequest: "400 Bad Request",
            TempError:  "307 Temporary Redirect"
        }

    def get (self, params):
        """
        Placeholder, define this in your subclass.
        Returns answer as dict or string.
        params -- dict, parameters from the query string
        """
        pass

    def get_skeleton (self):

        answer = self.get (self.environ.get ("QUERY_STRING") or {})
        if isinstance (answer, dict):
            answer = json.dumps (answer)
        elif not isinstance (answer, str):
            raise ValueError (
                "Internal getter returned invalid data."
            )

        data = gzip.compress (
            answer.encode ("utf-8")
        )
        return self.answer (
            "200 OK", 
            [("Content-Type", "application/json; charset/utf-8"),
             ("Content-Encoding", "gzip"),
             ], 
            data)

    def set (self, input_dict):
        """
        Placeholder, define this in your subclass.
        Values returned by this function are ignored.
        If something goes wrong during processing your
        input, raise an Exception.
        input_dict -- dict, decoded json as submitted 
                            with the request
        """
        pass

    def set_skeleton (self):

        if self.environ ['REQUEST_METHOD'] != "POST":
            raise BadRequest ()

        form = cgi.FieldStorage (fp = self.environ ['wsgi.input'], environ = self.environ)
        input_dict = json.loads (form.getvalue ("json"))

        self.set (input_dict)

        return self.answer ("200 OK", [], "")

    def init (self, uuid):
        """
        Placeholder, define this in your subclass.
        Values returned by this function are ignored.
        If something goes wrong during processing your
        input, raise an Exception.
        Use this function to initiate any data you need
        for both, set and get requests.
        """
        pass

    def quit (self):
        """
        Placeholder, define this in your subclass.
        Values returned by this function are ignored.
        Use this function to destroy any data structures 
        you initiated in self.init (e.g. open files).
        This is also called when self.init fails, so 
        watchout for that!
        """
        pass

    def answer (self, status, headers, body):

        self.quit ()

        self.headers_cb (status, headers);
        return [body.encode ("utf-8") if not isinstance (body, bytes) else body]

    def __call__ (self, environ, headers_cb):

        self.environ    = environ
        self.headers_cb = headers_cb

        try:
            self.init (shift_path_info (environ))
            return self.paths [shift_path_info (environ)] ()
        except Exception as e:
            if len (e.args) > 0:
                body = str (e)
            else:
                body = ""
            
            status = self.errors.get (e.__class__, "500 Internal Server Error")
            header = []

            if e.__class__ == TempError:
                header.append (
                    ("Location", "/".join ( (self.environ ["SCRIPT_NAME"], self.environ ["PATH_INFO"]) ))
                )

            return self.answer (status, header, body)
