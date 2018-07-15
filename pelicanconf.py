#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Naetw'
SITENAME = 'naetw\'s blog'
SITEURL = 'https://naetw.github.io'
PATH = 'content'
TIMEZONE = 'Asia/Taipei'
THEME = 'theme/plumage'
DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),)

# Social widget
GITHUB_USERNAME = 'Naetw'
SOCIAL = (('GitHub', 'https://github.com/{}'.format(GITHUB_USERNAME)),)

DEFAULT_PAGINATION = 10

# URL
SLUGIFY_SOURCE = 'basename'
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = ARTICLE_URL + 'index.html'

TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = TAG_URL + 'index.html'

CATEGORY_URL = 'category/{slug}/'
CATEGORY_SAVE_AS = CATEGORY_URL + 'index.html'

TAGS_SAVE_AS = 'tags/index.html'
CATEGORIES_SAVE_AS = 'categories/index.html'
ARCHIVES_SAVE_AS = 'archives/index.html'

DISPLAY_CATEGORIES_ON_MENU = False
MENUITEMS = [('Archives', '/archives'),
             ('Categories', '/categories'),
             ('Tags', '/tags'),]

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
