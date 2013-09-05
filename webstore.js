// Copyright 2013 Marvin Poul
// Licensed under the Do What The Fuck You Want To License, Version 2
// See LICENSE for details or http://www.wtfpl.net/txt/copying

function WebStore (root, uuid) {
    this.url = root + "/" + uuid;
}

WebStore.prototype.set = function (obj) {

    var request = new XMLHttpRequest ();
    var form    = new FormData ();

    var payload = JSON.stringify (obj);
    form.append (
        "json", payload
    );

    request.onreadystatechange = function () {
        if (this.readyState < 4 || this.status == 200) {
            return;
        }

        console.log (
            "ERROR " + this.status + " on \n" +
             payload + "\nResponse text is\n" +          
             this.responseText
        )
    };

    request.open ("POST", this.url + "/set");
    request.send (form);
}

WebStore.prototype.get = function (cb, param) {

    var querystring = "";
    if (param != undefined) {
        for (key in param) {
            var enkey = encodeURI (key);
            var value = param [key];
            if (value instanceof Array) {
                for (var i = 0; i < value.length; i++) {
                    querystring += enkey + "=" + encodeURI (String (value [i]));
                }
            } else if (value instanceof String) {
                querystring += enkey + "=" + encodeURI (value);
            }
        }
    }

    var request = new XMLHttpRequest ();

    request.onreadystatechange = function () {
        if (this.readyState < 4) return;

        if (this.status != 200) {
            console.log ("ERROR " + this.status + " on " + "/get?" + querystring);
            console.log (this.responseText);
            return;
        }

        var data = JSON.parse (this.responseText);
        cb (data);
    };
    request.open ("GET", this.url + "/get?" + querystring);
    request.send ();
}
