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

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy import log, signals
from hpizza_ab.hpizza_spider import HPizzaSpider


spider = HPizzaSpider(allowed_domains = ["www.hardpizza.ru"],start_urls = ["http://www.hardpizza.ru/deserty.html", ])
# spider = HPizzaDetailSpider(11, name='hpd',start_urls=['http://www.hardpizza.ru/index.php?option=com_virtuemart&nosef=1&view=productdetails&task=recalculate&virtuemart_product_id=36&format=json&amp;lang=ru&customPrice%255B0%255D%255B11%255D%3D16%26quantity%255B%255D%3D1%26option%3Dcom_virtuemart%26virtuemart_product_id%255B%255D%3D36%26virtuemart_manufacturer_id%3DArray%26'])
crawler = Crawler(Settings({'BOT_NAME':'hpizza_ab','DOWNLOAD_DELAY':24,'ITEM_PIPELINES':['hpizza_ab.pipelines.HpizzaPipeline',]}))
crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start(logfile='crawl.txt',loglevel=log.INFO,logstdout=False)
reactor.run() # the script will block here until the spider_closed signal was sent


