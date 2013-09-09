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

        # delegates handling of a path to a function
        self.paths = { 
            get_path: self.get_skeleton, 
            set_path: self.set_skeleton,
        }

        # delegates handling of an error to a function
        # an error handler is called with the caught
        # exception: handler (e)
        # and is expected to return a three tuple
        # (status, headers, body)
        self.errors = [
            (BadRequest, self.fail_badrequest),
            (TempError,  self.fail_temp),
            # since ∀ subclasses S of C: isinstance (S (), C) == True
            # the next tuple will catch all Exceptions,
            # remove it from the list, if you don't want that
            (Exception,  self.fail), 
        ]

    def get (self, params):
        """
        Placeholder, define this in your subclass.
        Returns answer as dict or string.
        params -- dict, parameters from the query string
        """
        pass

    def get_skeleton (self):

        answer = self.get (parse_qs (self.environ.get ("QUERY_STRING", "")))
        if isinstance (answer, dict):
            answer = json.dumps (answer)
        elif not isinstance (answer, (str, bytes)):
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
        input_dict = json.loads (form.getvalue ("payload"))

        self.set (input_dict)

        return self.answer ("200 OK", [], "")

    def init (self):
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

    def fail (self, e):

        status = "500 Internal Server Error"
        header = []

        return status, header, str (e)

    def fail_badrequest (self, e):

        status = "400 Bad Request"
        header = []

        return status, header, "\n".join (map (str, e.args))

    def fail_temp (self, e):

        status = "307 Temporary Redirect"
        header = []

        header = [
            ("Location", "/".join ( (self.environ ["SCRIPT_NAME"], self.environ ["PATH_INFO"]) ))
        ]

        return status, header, ""

    def __call__ (self, environ, headers_cb):

        self.environ    = environ.copy ()
        self.headers_cb = headers_cb

        try:
            self.uuid = shift_path_info (environ)
            self.init ()
            path = shift_path_info (environ)
            return self.paths [path] ()

        except Exception as e:
            for error, handler in self.errors:
                if isinstance (e, error):
                    return self.answer (*handler (e))
            else:
                # if the Exception is not handled we raise it again
                raise e from None 
