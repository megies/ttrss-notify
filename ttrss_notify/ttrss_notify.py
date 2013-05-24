#!/usr/bin/env python
import os
import sys
import json
import time
import urllib2
from ConfigParser import SafeConfigParser

import pynotify

DEFAULT_CONFIG_FILE = "~/.ttrss-notify.ini"
INTERVAL = 300


class TTRSS(object):
    def __init__(self, config_file):
        # parse configuration
        parser = SafeConfigParser()
        parser.read(config_file)
        self.baseurl = parser.get('web', 'baseurl')
        web_auth_method = parser.get('web', 'auth_method')
        web_realm = parser.get('web', 'realm')
        web_user = parser.get('web', 'username')
        web_password = parser.get('web', 'password')
        ttrss_user = parser.get('ttrss', 'username')
        ttrss_password = parser.get('ttrss', 'password')
        self.ttrss_feed_id = parser.getint('ttrss', 'feed_id')
        self.ttrss_is_cat = parser.getboolean('ttrss', 'is_cat')
        self.notify_timeout = parser.getint('notify', 'timeout')
        self.apiurl = self.baseurl + '/api/'
        # install http auth handler / opener
        pwm = urllib2.HTTPPasswordMgr()
        pwm.add_password(web_realm, self.baseurl, web_user, web_password)
        if web_auth_method.lower() == "digest":
            handler = urllib2.HTTPDigestAuthHandler
        elif web_auth_method.lower() == "basic":
            handler = urllib2.HTTPBasicAuthHandler
        handler = handler(pwm)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        # login to tiny rss
        self.session_id = ""
        self.login(ttrss_user, ttrss_password)
        pynotify.init("tinyrss")

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

    def getHeadlines(self, feed_id, is_cat):
        req = {'op': 'getHeadlines', 'feed_id': feed_id,
               'is_cat': is_cat, 'view_mode': "unread"}
        res = self._request(req)
        return res['content']

    def getCategories(self):
        req = {'op': 'getCategories'}
        res = self._request(req)
        return dict([(int(item['id']), item) for item in res['content']])

    def getFeeds(self):
        req = {'op': 'getFeeds', 'cat_id': -4}
        res = self._request(req)
        return dict([(int(item['id']), item) for item in res['content']])

    def runOnce(self):
        # check feed
        headlines = None
        if self.ttrss_is_cat:
            categories = self.getCategories()
        else:
            categories = self.getFeeds()
        category = categories[self.ttrss_feed_id]
        if category['unread']:
            headlines = self.getHeadlines(self.ttrss_feed_id,
                                          self.ttrss_is_cat)
        # notify if any unread messages
        if headlines:
            self.notify(category, headlines)

    def notify(self, category, headlines):
        summary = "RSS: %i unread in %s" % (category['unread'],
                                            category['title'])
        body = "&#8226; " + "\n&#8226; ".join([h['title'] for h in headlines])
        body += "\n<a href='%s'>open TTRSS</a>" % self.baseurl
        noti = pynotify.Notification(summary, body)
        noti.set_timeout(self.notify_timeout)
        noti.show()


def main():
    # read config at default location or specified on command line
    filename = os.path.expanduser(DEFAULT_CONFIG_FILE)
    try:
        filename = sys.argv[1]
    except:
        pass

    with TTRSS(filename) as ttrss:
        while True:
            ttrss.runOnce()
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
