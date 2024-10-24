import os
import urllib.request
import re
import threading
import posixpath
import urllib.parse
import argparse
import socket
import time
import hashlib
import pickle
import signal
import imghdr
import ssl

# Bing image bulk downloader
# example of use:
# python image-downloader-bing.py -s "cat with mouse in mouth" --adult-filter-off --limit 750 --filters "+filterui:imagesize-medium" -p "20200811"
#
# if filenames with multiple dots are showing up, try removing them with rename command, ex: rename -n 's/\./_/' *.*.jpg

# config
output_dir = '../data/download'  # default output dir
adult_filter = True  # adult filter on by default
socket.setdefaulttimeout(5)

tried_urls = []
image_md5s = {}
in_progress = 0
urlopenheader = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}


def download(pool_sema: threading.Semaphore, url: str, output_dir: str, output_file_prefix: str = None):
    global in_progress

    if url in tried_urls:
        return
    pool_sema.acquire()
    in_progress += 1
    path = urllib.parse.urlsplit(url).path
    filename = posixpath.basename(path).split('?')[0]  # strip GET parameters from filename
    name, ext = os.path.splitext(filename)
    name = name[:36].strip()
    filename = output_file_prefix + '-' + name + ext

    try:
        request = urllib.request.Request(url, None, urlopenheader)
        image = urllib.request.urlopen(request).read()
        if not imghdr.what(None, image):
            print('Invalid image, not saving ' + filename)
            return

        md5_key = hashlib.md5(image).hexdigest()
        if md5_key in image_md5s:
            print('Image is a duplicate of ' + image_md5s[md5_key] + ', not saving ' + filename)
            return

        i = 0
        while os.path.exists(os.path.join(output_dir, filename)):
            if hashlib.md5(open(os.path.join(output_dir, filename), 'rb').read()).hexdigest() == md5_key:
                print('Already downloaded ' + filename + ', not saving')
                return
            i += 1
            filename = "%s-%s-%d%s" % (output_file_prefix, name, i, ext)

        image_md5s[md5_key] = filename

        imagefile = open(os.path.join(output_dir, filename), 'wb')
        imagefile.write(image)
        imagefile.close()
        print("OK: {}".format(filename))
        tried_urls.append(url)
    except Exception as e:
        print("FAIL: {} - {}".format(filename, e))
    finally:
        pool_sema.release()
        in_progress -= 1


def fetch_images_from_keyword(pool_sema: threading.Semaphore, keyword: str, output_dir: str, filters: str,
                              limit: int, output_file_prefix: str = None):
    current = 0
    last = ''
    while True:
        time.sleep(0.1)

        if in_progress > 10:
            continue

        request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(keyword) + '&first=' + str(
            current) + '&count=35&adlt=' + adlt + '&qft=' + ('' if filters is None else filters)
        request = urllib.request.Request(request_url, None, headers=urlopenheader)
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf8')
        links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
        try:
            if links[-1] == last:
                return
            for index, link in enumerate(links):
                if limit is not None and current + index >= limit:
                    return
                t = threading.Thread(target=download, args=(pool_sema, link, output_dir, output_file_prefix))
                t.start()
                current += 1
            last = links[-1]
        except IndexError:
            print('No search results for "{0}"'.format(keyword))
            return


def backup_history(*args):
    download_history = open(os.path.join(output_dir, 'download_history.pickle'), 'wb')
    pickle.dump(tried_urls, download_history)
    copied_image_md5s = dict(image_md5s)
    # we are working with the copy, because length of input variable for pickle must not be changed during dumping
    pickle.dump(copied_image_md5s, download_history)
    download_history.close()
    print('history_dumped')
    if args:
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bing image bulk downloader')
    parser.add_argument('-s', '--search-string', help='Keyword to search', required=False)
    parser.add_argument('-p', '--file-prefix', help='Prefix for downloaded files', required=False, default='bbid')
    parser.add_argument('-f', '--search-file', help='Path to a file containing search strings line by line',
                        required=False)
    parser.add_argument('-o', '--output', help='Output directory', required=False)
    parser.add_argument('--adult-filter-on', help='Enable adult filter', action='store_true', required=False)
    parser.add_argument('--adult-filter-off', help='Disable adult filter', action='store_true', required=False)
    parser.add_argument('--filters', help='Any query based filters you want to append when searching for images, '
                                          'e.g. +filterui:license-L1', required=False)
    parser.add_argument('--limit', help='Make sure not to search for more than specified amount of images.',
                        required=False, type=int)
    parser.add_argument('--threads', help='Number of threads', type=int, default=20)
    args = parser.parse_args()

    ssl._create_default_https_context = ssl._create_unverified_context


    if (not args.search_string) and (not args.search_file):
        parser.error('Provide Either search string or path to file containing search strings')
    if args.output:
        output_dir = args.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir_origin = output_dir
    signal.signal(signal.SIGINT, backup_history)
    try:
        download_history = open(os.path.join(output_dir, 'download_history.pickle'), 'rb')
        tried_urls = pickle.load(download_history)
        image_md5s = pickle.load(download_history)
        download_history.close()
    except (OSError, IOError):
        tried_urls = []
    if adult_filter:
        adlt = ''
    else:
        adlt = 'off'
    if args.adult_filter_off:
        adlt = 'off'
    elif args.adult_filter_on:
        adlt = ''
    pool_sema = threading.BoundedSemaphore(args.threads)
    if args.search_string:
        fetch_images_from_keyword(pool_sema, args.search_string, output_dir, args.filters, args.limit, args.file_prefix)
    elif args.search_file:
        try:
            inputFile=open(args.search_file)
        except (OSError, IOError):
            print("Couldn't open file {}".format(args.search_file))
            exit(1)
        for keyword in inputFile.readlines():
            output_sub_dir = os.path.join(output_dir_origin, keyword.strip().replace(' ', '_'))
            if not os.path.exists(output_sub_dir):
                os.makedirs(output_sub_dir)
            fetch_images_from_keyword(pool_sema, keyword, output_sub_dir, args.filters, args.limit, args.file_prefix)
            backup_history()
            time.sleep(10)
        inputFile.close()
