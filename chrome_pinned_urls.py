#!/usr/bin/env python

import os
import sys
import urllib
import hashlib
import urlparse
import simplejson
from subprocess import Popen, PIPE

MAC_PATH = '~/Library/Application Support/Google/Chrome/Default/Preferences'
LIN_PATH = '~/.config/google-chrome/Default/Preferences'

def get_os_path():
    if sys.platform == 'darwin':
        path = MAC_PATH
    elif sys.platform == 'linux2':
        path = LIN_PATH
    else:
        print 'Sorry, only OS X and Linux are supported at this time'
        sys.exit()

    return path

def chrome_is_running():
    # ps awx | grep -i 'google[- ]chrome | wc -l
    reg = 'google[- ]chrome'

    ps_proc = Popen(['ps', 'awx'], stdout=PIPE)
    grep_proc = Popen(['grep', '-i', reg], stdin=ps_proc.stdout, stdout=PIPE)

    chrome_processes = grep_proc.communicate()[0].split('\n')

    return True if len(chrome_processes) > 2 else False

def get_preferences():
    path = get_os_path()

    preferences_file = open(os.path.expanduser(path))
    preferences = simplejson.load(preferences_file)

    return preferences

def get_title_for_url(url):
    # TODO: Is there a better way to just fetch the title?
    try:
        page = urllib.urlopen(url).read()
    except IOError:
        print '%s is not a well-formed url. Aborting.' % url
        sys.exit()

    try:
        title = page.split('<title>')[1].split('</title>')[0]
    except IndexError:
        title = ''

    return title

def list_pinned_urls(preferences):
    if not preferences['ntp'].has_key('pinned_urls'):
        print 'No urls are pinned'
        return

    values = preferences['ntp']['pinned_urls'].values()
    values.sort(key=lambda i: i['index'])

    for i in values:
        print '%d - %s (%s)' % (i['index'] + 1, i['url'], i['title'])

def write_preferences_file(preferences):
    path = get_os_path()
    out_file = open(os.path.expanduser(path), 'w')
    simplejson.dump(preferences, out_file, indent=3, sort_keys=True,
                    separators=(',', ': '))
    out_file.close()

    print 'Successfully wrote Chrome Preferences file. Done.'

def add_pinned_url(url, preferences):
    # Things don't work if there's no trailing slash and no path
    if urlparse.urlparse(url).path == '' and url[-1] != '/':
        url += '/'

    if not preferences['ntp'].has_key('pinned_urls'):
        preferences['ntp']['pinned_urls'] = {}

    pinned_urls = preferences['ntp']['pinned_urls']

    if len(pinned_urls) > 7:
        print 'Too many pinned urls to. Please unpin a url. Aborting.'
        sys.exit()

    key = hashlib.md5(url).hexdigest()

    if key in pinned_urls.keys():
        print '%s is already pinned. Skipping.' % url
        return preferences

    # I don't think this is necessary, but it seems like a good idea
    if key in preferences['ntp']['most_visited_blacklist'].keys():
        print 'Removing url from most visited blacklist...'
        del preferences['ntp']['most_visited_blacklist'][key]

    taken_indices = [i['index'] for i in pinned_urls.values()]
    the_index = [x for x in [y for y in range(8)] if x not in taken_indices][0]

    pinned_url = {}
    pinned_url['title'] = get_title_for_url(url)
    pinned_url['url'] = url
    pinned_url['direction'] = 'ltr'
    pinned_url['index'] = the_index

    preferences['ntp']['pinned_urls'][key] = pinned_url

    print 'Successfully added %s at index %s' % (url, the_index)

    return preferences


if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser()

    parser.set_usage('%prog [-l] [url1 url2 ...]')
    parser.set_description('Python script to manipulate Chrome\'s pinned urls')
    parser.add_option('-l', '--list', dest='do_list', action='store_true',
                      help='List current pinned urls with their indices and exit')

    opts, args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    if chrome_is_running():
        print 'Please quit Google Chrome before using this script. Aborting.'
        sys.exit()

    preferences = get_preferences()

    if opts.do_list:
        list_pinned_urls(preferences)
        sys.exit()

    for arg in args:
        add_pinned_url(arg, preferences)

    write_preferences_file(preferences)
