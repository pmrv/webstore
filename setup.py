from setuptools import setup

setup (
        name        = "webstore",
        version     = "0.1.0",
        author      = "Marvin Poul",
        author_email= "ponder@creshal.de",
        url         = "https://github.com/ponderstibbons/webstore",
        license     = "WTFPL2",
        packages    = ["webstore"],
        provides    = ["webstore"],
        description = "(Very) Simple framework for WSGI Apps providing a way to store JSON data on server.",
)
