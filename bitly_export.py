#!/usr/bin/env python
# encoding: utf-8
"""Simple bit.ly -> bookmarks.html exporter"""
from __future__ import absolute_import, print_function, unicode_literals

import argparse
import codecs
import getpass
import sys
from cgi import escape as html_escape

try:
    import bitly_api
except ImportError:
    print('Unable to import bitly_api: pip install bitly-api?')
    raise


BOOKMARK_HEADER = """
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Bookmarks</title>
<h1>Bookmarks</h1>
<dl>
""".strip()

BOOKMARK_TEMPLATE = """
<dt><a href="{url}" add_date="{add_timestamp}" private="{private}" tags="{tags}">{title}</A>
<dd>{description}</dd>
""".strip()

BOOKMARK_FOOTER = """
</dl>
""".strip()


SHARE_TEMPLATE = """
{share_type}: <a href="{remote_share_link}">{text}</a>
""".strip()


def download_links(access_token, page_size=100):
    bitly = bitly_api.Connection(access_token=access_token)

    offset = 0

    while True:
        print('Fetching {start}-{end}…'.format(start=offset, end=offset + page_size), file=sys.stderr)

        links = bitly.user_link_history(offset=offset, limit=page_size)

        for l in links:
            yield l

        if len(links) < page_size:
            raise StopIteration
        else:
            offset += page_size


def export_links(links, output_file):
    print(BOOKMARK_HEADER, file=output_file)

    for l in links:
        parms = {
            'url': html_escape(l['long_url']),
            'title': html_escape(l.get('title', None) or ''),
            'add_timestamp': l['created_at'],
            'tags': '',
            'private': '1' if l['private'] else '0',
            'description': html_escape(l.get('text', '')),
        }

        if 'shares' in l and not parms['description']:
            share_links = [SHARE_TEMPLATE.format(**{k: html_escape(v) if isinstance(v, str) else v
                                                    for k, v in i.items()})
                                                 for i in l['shares'] if i['share_type'] != 'email']
            if len(share_links) > 1:
                parms['description'] = '<ul><li>%s</li></ul>' % '</li><li>'.join(share_links)
            else:
                parms['description'] = '<br>'.join(share_links)

        print(BOOKMARK_TEMPLATE.format(**parms),
              file=output_file)

    print(BOOKMARK_FOOTER, file=output_file)


def main():
    parser = argparse.ArgumentParser(__doc__.strip())
    parser.add_argument('--token', help='OAuth token obtained at https://bitly.com/a/oauth_apps')
    parser.add_argument('--output-filename', default='bookmarks.html',
                        help='Output filename (default: %(default)s)')
    args = parser.parse_args()

    token = args.token
    if not token:
        token = getpass.getpass('Bitly token:')

    links = download_links(token)

    with codecs.open(args.output_filename, 'w', encoding='utf-8') as f:
        export_links(links, f)


if __name__ == "__main__":
    main()
