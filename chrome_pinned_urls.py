#!/usr/bin/env python

import os
import sys
import urllib2
import simplejson
from subprocess import Popen, PIPE

def chrome_is_running():
    # ps awx | grep Chrome | wc -l
    ps_proc = Popen(['ps', 'awx'], stdout=PIPE)
    grep_proc = Popen(['grep', 'Chrome'], stdin=ps_proc.stdout, stdout=PIPE)

    chrome_processes = grep_proc.communicate()[0].split('\n')

    return True if len(chrome_processes) > 2 else False

def get_pinned_urls():
    path = '~/Library/Application Support/Google/Chrome/Default/Preferences'
    preferences_file = open(os.path.expanduser(path))
    preferences = simplejson.load(preferences_file)
    pinned_urls = preferences['ntp']['pinned_urls']

    return pinned_urls 

def get_title_for_url(url):
    # TODO: Is there a better way to just fetch the title?
    try:
        page = urllib.urlopen(url).read()
    except IOError:
        print 'Not a good url?'
        exit()

    try:
        title = page.split('<title>')[1].split('</title>')[0]
    except IndexError:
        title = ''

    return title

def list_pinned_urls(pinned_urls):
    for k, v in pinned_urls.items():
        print v['title'], v['url']

if __name__ == '__main__':
    preferences = get_preferences()
    list_pinned_urls(preferences)
