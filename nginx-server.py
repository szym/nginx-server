#!/usr/bin/env python
"""\
Usage: %prog [path:.] [port:8000]
"""

import os
import sys
import shutil
import tempfile

conf_template = """\
error_log /dev/stderr;
pid %(path)s/nginx.pid;
worker_processes 1;

daemon off;
events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;
    access_log /dev/stdout;
    client_body_temp_path %(path)s/body;
    proxy_temp_path %(path)s/proxy;
    fastcgi_temp_path %(path)s/fastcgi;
    uwsgi_temp_path %(path)s/uwsgi;
    scgi_temp_path %(path)s/scgi;

    gzip             on;
    gzip_http_version 1.1;
    gzip_proxied     any;
    gzip_types       text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_disable     "MSIE [1-6]\.";
    gzip_comp_level  6;

    server {
        listen %(port)s;

        location / {
            root "%(root)s/";
            autoindex on;
            index index.html index.htm;
        }
    }
}
"""

def get_realpath(path):
    return os.path.realpath(os.path.join(os.path.abspath(os.curdir), path))

def main():
    try:
        path = sys.argv[1]
    except:
        path = "."
    root = get_realpath(path)
    try:
        port = sys.argv[2]
    except:
        port = "8000"

    address = "http://localhost:%s" % port

    workpath = tempfile.mkdtemp(prefix="nginx")

    conf = os.path.join(workpath, "nginx.conf")
    mime_source = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mime.types")
    mime_dest = os.path.join(workpath, "mime.types")
    shutil.copyfile(mime_source, mime_dest)
    with open(conf, "w") as f:
        conf_data = conf_template % dict(root=root, port=port, path=workpath)
        f.write(conf_data)
    print >>sys.stderr, "%r serving in %r" % (root, address)
    os.execvp("nginx", ["nginx", "-c", conf])

main()
