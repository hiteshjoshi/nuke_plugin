#!/usr/bin/env python3
__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "hiteshjoshi"
__home_page__ = "https://hitesh.io/"

import os
import posixpath
import http.server
import urllib.request
import urllib.parse
import urllib.error
import cgi
import shutil
import mimetypes
import re
from io import BytesIO
import json
import sys
from fastai.vision import *

learn = load_learner(sys.argv[1])


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    server_version = "SimpleHTTPWithUpload/" + __version__

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'hello': 'world', 'received': 'ok'}))

    def do_POST(self):
        """Serve a POST request."""
        r, info, length = self.deal_post_data()
        self._set_headers()
        # "File '%s' upload success!" % fn
        success = "true" if r else "false"
        json_string = json.dumps(
            {'success': '%s' % success, 'weight': '%s' % info})
        self.wfile.write(json_string.encode(encoding='utf_8'))

    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, 0, 0)
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, 0, remainbytes)
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(
            r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, 0, remainbytes)
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, 0, remainbytes)

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                pred_class, pred_idx, outputs = learn.predict(open_image(fn))
                return (True, pred_class, remainbytes)
            else:
                out.write(preline)
                preline = line
        return (False, 0, remainbytes)

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


def test(HandlerClass=SimpleHTTPRequestHandler,
         ServerClass=http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()
