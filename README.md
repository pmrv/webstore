webstore
========

(Very) Simple framework for WSGI Apps providing a way to store JSON data on server. Comes with JS bindings.

Use Cases
---------
The idea behind this is to have a simple instrument for clientside web apps to communicate with a server
and synchronize data with other clients.

Installation
------------
Depends on Python 3 and a WSGI capable webserver (tested only for Apache + mod_wsgi). No other strings atached.  
Installation should be as simple as `python setup install`.

Usage
-----
In general the 'API' of a WebStore App looks like this
`http://your.server/$wsgi_mount/$uuid/{get,set}` 
People can GET data from the app via "get" and POST data to the app via "set" (Duhu). 
So what's that $uuid bit? Anything at all, as long as it is properly escaped.
This is used to identify the store which is supposed be accessed.
However, this is more of a suggestion than a rule. WebStore itself does not care about
its semantics, it just makes its value accessible to your App. 

The bare minimum to use WebStore (after you installed it) is this: 
```python
from webstore import WebStore
application = WebStore ()
```
Won't do much of course. To make something happen you'll have to subclass WebStore (geez).
There are four basic hooks which _can_ be defined by your App, though none are mandotory (but then XYZZY).  
  1. `WebStore.init (self) -> None`   
You can use this one to initiate any data structures you'll need to handle a request.
The $uuid bit from before is available under `self.uuid`.  
  2. `WebStore.quit (self) -> None`  
Use this to tear them down again. Beware though, that it is not guaranteed that `WebStore.init` 
ran successfully and completely when this is called.  
  3. `WebStore.get  (self, query_parameters: dict) -> (str, dict)`  
Is invoked when (you guessed it) when a GET request for `/$wsgi_mount/$uuid/get` comes in. 
If it came with a query string you'll get a dict of it as returned by `urllib.parse.parse_qs`. 
Read its docs for details.  
  4. `WebStore.set  (self, payload: dict) -> None`  
Invoked on POST request for `/$wsgi_mount/$uuid/set`. Any JSON submitted with the request 
via the `payload` form field will be handed to you as the `payload` parameter as converted to a
dict by `json.loads`. Read its docs for details.

If you don't like the get/set paths, you can change them with `get_path`/`set_path` keyword arguments
to `Webstore.__init__`. Read its doc string for details.  

WebStore also comes with basic error handling facilities. If you raise errors in any of the above mentioned
functions, they will get caught and `WebStore.errors` is searched for an error handler. `WebStore.errors`
is a proplist of `(ExceptionClass, HandlerFunction)` tuple. As it iterates through this list it checks
`isinstance (CaughtException, ExceptionClass)`. If true, `HandlerFunction` is called with the 
_instance_ of the caught Exception as a single argument and should return a 3-tuple of the HTTP status code
of the response, a list of headers as per PEP 3333 and the response body as either `str` or `bytes`.  
I chose a proplist and not a dict, because this allows us to sort exception handlers by priority and
inheritance hierarchy.

To add new exception handlers with the highest priority do `WebStore.errors.insert (0, (ExceptionClass, HandlerFunction))`.  
WebStore comes with two custom exceptions and three builtin exception handlers. If you raise `webstore.BadRequest`, it 
will be caught by the first exception handler, which will issue a _400 Bad Request_ and print all arguments of the Exception
as response body. Raising `webstore.TempError` causes a _307 Temporary Redirect_
to the same URL the client used for the current request, giving you some time
when e.g. a resource is not available or in use. The last builtin exception
handler catches instances of `Exception` that is, probably all Exceptions you
are going to raise. If you don't like that replace `WebStore.errors` with a
custom list (an empty list _is_ valid).

Also, if you read the source, you'll notice that you can easily add new URL
paths to WebStore, simply by adding them to the `WebStore.paths` dict. 

### TL;DR ###
Function:  
  1. `WebStore.init (self) -> None`   
  Init data for the request
  2. `WebStore.quit (self) -> None`  
  Clean it up again
  3. `WebStore.get  (self, query_parameters: dict) -> (str, dict)`  
  Return data to the client
  4. `WebStore.set  (self, payload: dict) -> None`  
  Get data from the client

Attributes:  
  1. `WebStore.uuid`  
  str, think of it as a session key  
  2. `WebStore.environ`  
  dict, WSGI environment dict  
  3. `WebStore.errors`  
  proplist, defines exception handlers and their priority

For more info read the source and the example. It's only ~100 LLOC and all hooks and attributes
have comments.
