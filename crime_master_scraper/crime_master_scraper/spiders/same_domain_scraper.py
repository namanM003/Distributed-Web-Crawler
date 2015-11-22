'''This file contains the core scraping logic. Only those pages belonging to the same domain 
as that of the provided input url are scraped.'''

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from crime_master_scraper.items import CrimeMasterScraperItem
from urlparse import urlparse
import urllib2
from scrapy.exceptions import CloseSpider
#from scrapy.project import crawler

def get_redirected_url(url):
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
    request = opener.open(url)
    return request.url

class MySpider(CrawlSpider):
    #Name of the spider
    name = "crime_master"

    #We don't need any other restricting rules as we are already using the default Offsite Middleware to restrict other domains
    #We just need a callback to parse_items
    rules = (
        Rule(LinkExtractor(), callback="parse_items", follow= True),
    )

    def __init__(self, start_url = '', num_pages_to_crawl=1,*args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)

        #start_urls = [kwargs.get('start_url')]
        #Assign a start url to start scraping
	fp = urllib2.urlopen(start_url)
	start_url = get_redirected_url(start_url)
        self.start_urls = [start_url]

	self.num_pages_to_crawl = num_pages_to_crawl
	self.num_pages_crawled = 1

        #Extract domain-name of the start_url. To restrict to the domain, scrapy expects domain name to be of pattern "google.com".
        #Hence, the additional https:// and / tags needs to be removed.
        parsed_uri = urlparse(self.start_urls[0])
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        domain = domain.replace('http://','')
        domain = domain.replace('https://','')
        domain = domain.replace('/','')

        #Restrict the domain to that of the start_url's domain
        self.allowed_domains = [domain]

    def parse_items(self, response):
	#Stop crawling if max number of pages are crawled
	if int(self.num_pages_crawled) == int(self.num_pages_to_crawl):
		raise CloseSpider('Maximum number of pages crawled')
        #Yield each scraped item's url. You could also return the entire list of urls from the response but yield results in a better performance.
        item = CrimeMasterScraperItem()
        item['link'] = response.url
	self.num_pages_crawled = self.num_pages_crawled + 1
        yield item
