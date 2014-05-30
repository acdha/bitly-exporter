bitly-exporter
==============

Bitly.com doesn't have an export feature for non-pro accounts. This script will generate a bookmarks.html
file suitable for use with services like http://pinboard.in:

1. ``pip install bitly-api``
2. Visit https://bitly.com/a/oauth_apps and generate and OAuth token
3. ``./bitly_export.py --token=<TOKEN>``
4. Enjoy your links
