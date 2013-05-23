#!/usr/bin/env python
import os
import sys
import json
import urllib2
from ConfigParser import SafeConfigParser

import pynotify

DEFAULT_CONFIG_FILE = "~/.ttrss-notify.ini"


class TTRSS(object):
    def __init__(self):
        self.apiurl = BASEURL + '/api/'
        # install http auth handler / opener
        pwm = urllib2.HTTPPasswordMgr()
        pwm.add_password(WEB_REALM, BASEURL, WEB_USER, WEB_PASSWORD)
        if WEB_AUTH_METHOD.lower() == "digest":
            handler = urllib2.HTTPDigestAuthHandler
        elif WEB_AUTH_METHOD.lower() == "basic":
            handler = urllib2.HTTPBasicAuthHandler
        handler = handler(pwm)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        # login to tiny rss
        self.session_id = ""
        self.login(TTRSS_USER, TTRSS_PASSWORD)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def _request(self, call):
        call['sid'] = self.session_id
        response = urllib2.urlopen(self.apiurl, json.dumps(call))
        return json.load(response)

    def login(self, username="", password=""):
        req = {'op': 'login', 'user': username, 'password': password}
        res = self._request(req)
        self.session_id = res['content']['session_id']

    def logout(self):
        req = {'op': 'logout'}
        self._request(req)

    def getUnreadCount(self):
        req = {'op': 'getUnread'}
        res = self._request(req)
        return int(res['content']['unread'])

    def getHeadlines(self):
        req = {'op': 'getHeadlines', 'feed_id': TTRSS_FEED_ID,
               'is_cat': TTRSS_IS_CAT, 'view_mode': "unread"}
        res = self._request(req)
        return [item['title'] for item in res['content']]

    def getCategories(self):
        req = {'op': 'getCategories'}
        res = self._request(req)
        return dict([(item['id'], item['title']) for item in res['content']])


if __name__ == "__main__":

    # read config in home directory or specified on command line
    filename = os.path.expanduser(DEFAULT_CONFIG_FILE)
    try:
        filename = sys.argv[1]
    except:
        pass

    # parse configuration
    parser = SafeConfigParser()
    parser.read(filename)
    BASEURL = parser.get('web', 'baseurl')
    WEB_AUTH_METHOD = parser.get('web', 'auth_method')
    WEB_REALM = parser.get('web', 'realm')
    WEB_USER = parser.get('web', 'username')
    WEB_PASSWORD = parser.get('web', 'password')
    TTRSS_USER = parser.get('ttrss', 'username')
    TTRSS_PASSWORD = parser.get('ttrss', 'password')
    TTRSS_FEED_ID = parser.getint('ttrss', 'feed_id')
    TTRSS_IS_CAT = parser.getboolean('ttrss', 'feed_id')
    NOTIFY_TIMEOUT = parser.getint('notify', 'timeout')

    # check feed
    with TTRSS() as ttrss:
        category = ttrss.getCategories()[str(TTRSS_FEED_ID)]
        headlines = ttrss.getHeadlines()

    # notify if any unread messages
    if headlines:
        #headlines = ttrss.getUnreadCount()

        summary = "RSS: %i unread in %s" % (len(headlines), category)
        body = "\n".join(headlines)
        body += "\n<a href='%s'>open TTRSS</a>" % BASEURL
        pynotify.init("tinyrss")
        noti = pynotify.Notification(summary, body)
        noti.set_timeout(NOTIFY_TIMEOUT)
        noti.show()
