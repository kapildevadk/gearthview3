# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.application.service import ServiceMaker

service_maker = ServiceMaker(
    "Twisted Web",
    "twisted.web.tap",
    ("A general-purpose web server which can serve from a "
     "filesystem or application resource."),
    "web"
)

service_maker.description = "A highly flexible and scalable web server"
service_maker.options.addOption(
    "-p", "--port", type="int", default=8080,
    help="Port number for the web server to listen on"
)

