#!/usr/bin/env python

import os
import sys
import urllib2
import hashlib
import simplejson
from subprocess import Popen, PIPE

def chrome_is_running():
    # ps awx | grep Chrome | wc -l
    ps_proc = Popen(['ps', 'awx'], stdout=PIPE)
    grep_proc = Popen(['grep', 'Chrome'], stdin=ps_proc.stdout, stdout=PIPE)

    chrome_processes = grep_proc.communicate()[0].split('\n')

    return True if len(chrome_processes) > 2 else False

def get_preferences():
    path = '~/Library/Application Support/Google/Chrome/Default/Preferences'
    preferences_file = open(os.path.expanduser(path))
    preferences = simplejson.load(preferences_file)

    return preferences 

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
    pinned_urls = get_preferences(['ntp']['pinned_urls'])

    values = pinned_urls.values()
    values.sort(key=lambda i: i['index'])

    for i in values:
        print '%d - %s (%s)' % (i['index'] + 1, i['url'], i['title'])

def write_preferences_file(preferences):

def add_pinned_url(url):
    if chrome_is_running():
        print 'Please quit Google Chrome before adding a pinned url'
        exit()

    preferences = get_preferences()

    pinned_urls = get_preferences(['ntp']['pinned_urls'])

    key = hashlib.md5(url).hexdigest()
    taken_indices = [i['index'] for i in pinned_urls.values()]
    the_index = [x for x in [y for y in range(8)] if x not in taken_indices]

    pinned_url = {}
    pinned_url['title'] = get_title_for_url(url)
    pinned_url['url'] = url
    pinned_url['direction'] = 'ltr'
    pinned_url['index'] = the_index

    preferences['ntp']['pinned_urls'][key] = pinned_url

    write_preferences_file(preferences)


if __name__ == '__main__':
