import scrapy
import re
from  urllib.parse import urlencode
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')

# https://dev.to/iankerins/build-your-own-google-scholar-api-with-python-scrapy-4p73 
# https://scrapeops.io/python-scrapy-playbook/

MAX_NUMBER_OF_PAGES = 5
MAX_DEPTH = 0

class ScholarSpider(scrapy.Spider):
    name = "scholar"
    allowed_domains = ["scholar.google.com", "api.scraperapi.com"]
    article_id = 0
    
    def start_requests(self):
        domain = 'https://scholar.google.com/scholar?'
        queries = [
            'marine mamals acoustics', 
            'signal processing for marine mammals',
            'machine learning marine mammals recognition',
            'bio acoustics'  
        ]  
        
        urls = []
        for query in queries:
            for page_num in range(MAX_NUMBER_OF_PAGES):
                urls.append(domain + urlencode({'start': page_num*10, 'hl': 'en', 'q': query})) 

        for url in urls:
            yield scrapy.Request(get_proxy_url(url), callback=self.parse, cb_kwargs={"parent_id":-1})

    def parse(self, response, parent_id):
        for article in self.get_articles_infos( response, parent_id ):
            yield article
            if article["link_to_citers"] is not None:
                yield response.follow( 
                                        url = get_proxy_url(article["link_to_citers"]) , 
                                        callback = self.get_articles_infos, 
                                        cb_kwargs = {"parent_id":article["id"]}
                                    )
    
    def get_articles_infos(self, response, parent_id):
        for article in response.xpath('//*[@data-rp]'):
            link = article.xpath('.//h3/a/@href').extract_first()
            temp = article.xpath('.//h3/a//text()').extract()
            if not temp:
                title = "".join(article.xpath('.//h3/span[@id]//text()').extract())
            else:
                title = "".join(temp)
            snippet = "".join(article.xpath('.//*[@class="gs_rs"]//text()').extract())
            cited = article.xpath('.//a[starts-with(text(),"Cited")]/text()').extract_first()
            if cited is not None:
                cited = re.sub('\D', '', cited)
                cited = int(cited) if len(cited) > 0 else 0
            link_to_citers = article.xpath('.//a[starts-with(text(),"Cited")]/@href').extract_first()
            publication_data = "".join(article.xpath('.//div[@class="gs_a"]//text()').extract())
            yield {
                    'id': self.article_id,
                    'parent_id': parent_id,
                    'title': title,
                    'cited': cited, 
                    'publication_data': publication_data,
                    'snippet': snippet,
                    'link': link,
                    "link_to_citers": 'https://scholar.google.com' + link_to_citers if link_to_citers else None
            }
            self.article_id += 1


def build_citing_pages_urls( response ):
    citing_pages_to_explore = response.xpath('.//a[starts-with(text(),"Cited")]/@href').getall()
    citing_pages_to_explore = map(lambda url: get_proxy_url('https://scholar.google.com' + url), citing_pages_to_explore)
    return citing_pages_to_explore

def get_proxy_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url   
 