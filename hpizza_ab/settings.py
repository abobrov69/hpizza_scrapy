# Scrapy settings for hpizza project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
from django.conf import settings

dj_db = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': r'C:\Wrk\hpizza_ab\hpizza_ab.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

settings.configure(DEBUG=True, TEMPLATE_DEBUG=True,DATABASES=dj_db)

BOT_NAME = 'hpizza'

SPIDER_MODULES = ['hpizza_ab']
NEWSPIDER_MODULE = 'hpizza_ab'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hpizza (+http://www.yourdomain.com)'

DOWNLOAD_DELAY = 3