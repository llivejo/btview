#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys, time
import re, os

_btimporterror = None
try:
        from BitTorrent import bencode, btformats
except ImportError, e1:
        try:
                from BitTornado import bencode; from BitTornado.BT1 import btformats
        except ImportError, e2:
                _btimporterror = '%s and %s'%(e1,e2)

def humanbytes(b):
    if b < 10000:
        return "%d bytes" % b
    elif b < 10000000:
        return "%d Kbytes" % (b/1000)
    elif b < 10000000000:
        return "%d Mbytes" % (b/1000000)
    else:
        return "%d Gbytes" % (b/1000000000)

def do_test_chksumfile(torrfile):
    if _btimporterror:
        raise EnvironmentError, _btimporterror
    try:
        metainfo = bencode.bdecode(torrfile.read())
        btformats.check_message(metainfo)
        return metainfo
    except ValueError, e:
        raise EnvironmentError, str(e) or 'invalid or corrupt torrent'

def get_if_exist(metainfo, key):
    if metainfo.has_key(key):
        s = metainfo[key]
        metainfo.pop(key)
        return s
    else:
        return None

def print_if_exist(metainfo, key):
    a = get_if_exist(metainfo, key)
    if a:
        print key, ':', a

def decode_tstamp(metainfo):
    ts = get_if_exist(metainfo, "creation date")
    if ts:
        print "created at", time.asctime(time.localtime(ts))

def get_name(info):
    if info.has_key('name.utf-8'):
        return info['name.utf-8']
    else:
        return info['name']

def get_id(name):
    """Add torrents.ru ID (topic number) to torrent name """
    p = re.compile(r'\[[a-z]+\.(ru|net|org)\]\.t(\d{6,10})\.torrent')
    m = p.match(name)
    if m:
        return "." + m.group(2)
    else:
        return ""

def normalize_name(name):
    return name.lower().replace(" ", "-").replace("_", "-").replace("~", '^')

def rename(filename):
    meta = do_test_chksumfile(open(filename))
    info = get_if_exist(meta, 'info')
    if get_name(info):
        newname = normalize_name(get_name(info) + get_id(filename) + '.torrent')
        print "renaming '%s' into '%s'" % (filename, newname)
        os.rename(filename, newname)

def total_size(metainfo):
    """
    """
    if metainfo.has_key('files'):
        total = 0
        for f in metainfo['files']:
            if f.has_key('length'):
                total += f['length']
        return total
    else:
        return None

def main():
    if len(sys.argv)>1:
        if sys.argv[1] == '-r':
            for name in sys.argv[2:]:
                rename(name)
            sys.exit(0)
        else:
            meta = do_test_chksumfile(open(sys.argv[1]))
            info = get_if_exist(meta, 'info')
            filename = get_name(info)
            filesize = get_if_exist(info, "length")
            if not(filesize):
                filesize = total_size(info)
            if filesize:
                print "%s (%s)" % (filename, humanbytes(filesize))
            else:
                print filename
            print
            decode_tstamp(meta)
            print_if_exist(meta, "announce")
            info.pop('pieces')
            for item in meta.keys():
                print item, ':', meta[item]
            print
            print "info :", info
    else:
        print "get info from .torrent metafile"
        print "  usage: %s file.torrent" % sys.argv[0]
        print "  or     -r [torrents.ru].NNNNNNN.torrent    to rename into proper name"

if __name__ == "__main__":
    main()

