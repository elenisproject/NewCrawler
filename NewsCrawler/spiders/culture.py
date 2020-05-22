# -*- coding: utf-8 -*-

import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from NewsCrawler.utilities import formatdate
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from NewsCrawler.items import NewsCrawlerItem
from NewsCrawler.settings import IEFIMERIDA_VARS,TANEA_VARS
from NewsCrawler.settings import TOVIMA_VARS,KATHIMERINI_VARS,NAFTEMPORIKI_VARS
from NewsCrawler.settings import LIFO_VARS,EFSYN_VARS,POPAGANDA_VARS,CNN_VARS
from NewsCrawler.settings import TOPONTIKI_VARS,GENERAL_CATEGORIES,PROTAGON_VARS
from NewsCrawler.settings import IN_VARS,NEWPOST_VARS,THETOC_VARS
import mysql.connector

lifo_counter = 0
in_counter = 0
thetoc_counter = 0
protagon_counter = 0
naftemporiki_counter = 0
iefimerida_counter = 0
popaganda_counter = 0
cnn_counter = 0
efsyn_counter = 0
class CultureSpider(CrawlSpider):
    name = 'culture'
    #handle_httpstatus_list = [301, 302]
    allowed_domains = [
        'topontiki.gr',
        'popaganda.gr',
        'efsyn.gr',
        'lifo.gr',
        'naftemporiki.gr',
        'in.gr',
        'cnn.gr',
        'tanea.gr',
        'thetoc.gr',
        'newpost.gr',
        'protagon.gr',
        'iefimerida.gr',
        'tovima.gr',
        'kathimerini.gr',
        ]
    url = [
        'https://popaganda.gr/newstrack/culture/',
        'https://www.naftemporiki.gr/culture',
        'https://www.tanea.gr/category/lifearts/culture/',
        'https://www.tanea.gr/category/lifearts/cinema/',
        'https://www.tanea.gr/category/lifearts/music/',
        'https://www.cnn.gr/style/politismos',
        'https://www.cnn.gr/style/psyxagogia',
        'https://www.thetoc.gr/',
        'https://www.protagon.gr/epikairotita/',
        'https://www.in.gr/culture/',
        'https://newpost.gr/entertainment',
        'https://www.iefimerida.gr',
        ]
    topontiki_urls = ['http://www.topontiki.gr/category/p-art?page={}'.format(x) for x in range(0,TOPONTIKI_VARS['CULTURE_PAGES'])]
    efsyn_urls = ['https://www.efsyn.gr/tehnes?page={}'.format(x) for x in range(1,EFSYN_VARS['ART_PAGES'])]
    lifo_urls = ['https://www.lifo.gr/now/culture/page:{}'.format(x) for x in range(1,LIFO_VARS['CULTURE_PAGES'])]
    kathimerini_urls = ['https://www.kathimerini.gr/box-ajax?id=b5_1885015423_108233952&page={}'.format(x) for x in range(0,KATHIMERINI_VARS['CULTURE_PAGES'])] 
    tanea_urls = ['https://www.tanea.gr/category/lifearts/music/page/{}'.format(x) for x in range(1,TANEA_VARS['MUSIC_PAGES'])]+['https://www.tanea.gr/category/lifearts/cinema/page/{}'.format(x) for x in range(1,TANEA_VARS['CINEMA_PAGES'])]+['https://www.tanea.gr/category/lifearts/culture/page/{}'.format(x) for x in range(1,TANEA_VARS['CULTURE_PAGES'])]    
    tovima_urls=['https://www.tovima.gr/category/culture/page/{}'.format(x) for x in range(1,TOVIMA_VARS['CULTURE_PAGES'])]
    newpost_urls = ['http://newpost.gr/entertainment?page={}'.format(x) for x in range(1,NEWPOST_VARS['CULTURE_PAGES'])]
    urls = url + newpost_urls + tanea_urls + tovima_urls + kathimerini_urls + lifo_urls + topontiki_urls + efsyn_urls
    start_urls = urls[:]

    
    


    rules = (
        Rule(LinkExtractor(allow=('topontiki.gr/article/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_topontiki', follow=True), 
        Rule(LinkExtractor(allow=("efsyn.gr/node","efsyn.gr/tehnes"), deny=('binteo','videos','gallery','eikones','twit','comment','page=','i-omada-tis-efsyn','contact')), callback='parse_efsyn', follow=True ,process_request='process_efsyn'), 
        Rule(LinkExtractor(allow=(r'popaganda\.gr.+newstrack/',r'popaganda\.gr.+culture'), deny=('binteo','videos','gallery','eikones','twit','comment','environment','fagito-poto','sport','technews','psichagogia','klp','san-simera-newstrack','keros','kairos','world','estiasi','health','social-media','greece','cosmote','koronoios')), callback='parse_popaganda', follow=True ,process_request='process_popaganda'), 
        Rule(LinkExtractor(allow=(r'www\.lifo\.gr.+culture/'), deny=('binteo','videos','gallery','eikones','twit','comment')), callback='parse_lifo', follow=True, process_request='process_lifo'), 
        Rule(LinkExtractor(allow=(r'\.naftemporiki\.gr/story|\.naftemporiki\.gr/storypn'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_naftemporiki', follow=True,process_request='process_request'), 
        Rule(LinkExtractor(allow=(r"\.kathimerini\.gr.+politismos/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_kathimerini', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tovima\.gr.+culture"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tovima', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+culture"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+music"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
        Rule(LinkExtractor(allow=(r"\.tanea\.gr.+cinema"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_tanea', follow=True), 
        Rule(LinkExtractor(allow=('iefimerida.gr/politismos'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_iefimerida', follow=True, process_request='process_iefimerida'), 
        Rule(LinkExtractor(allow=('cnn.gr/style/politismos/'),deny=('gallery')), callback='parseInfiniteCnn', follow=True ,process_request='process_cnn'),
        Rule(LinkExtractor(allow=('cnn.gr/style/psyxagogia'),deny=('gallery')), callback='parseInfiniteCnnPS', follow=True ,process_request='process_cnn'),
        Rule(LinkExtractor(allow=('thetoc.gr/politismos'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_thetoc', follow=True ,process_request='process_thetoc'),
        Rule(LinkExtractor(allow=('protagon.gr/epikairotita/'), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_protagon', follow=True, process_request='process_protagon'),
        Rule(LinkExtractor(allow=(r"\.in\.gr.+/culture/|\.in\.gr.+/entertainment/"), deny=('binteo','videos','gallery','eikones','twit')), callback='parse_in', follow=True ,process_request='process_in'), 
        Rule(LinkExtractor(allow=(r'newpost.gr/books|newpost.gr/cinema/|newpost.gr/moysikh/|newpost.gr/art/|newpost.gr/theatre/|newpost.gr/entertainment'), deny=('page')), callback='parse_newpost', follow=True),
    )

#next three functions for cnn infinite scroll for culture
    def parseInfiniteCnn(self,response):
        pages =  CNN_VARS['CNN_CULTURE_PAGES']
        for page in range(0, pages ,9):
            url = 'https://www.cnn.gr/style/politismos?start={}'.format(page)
            yield Request(url, callback = self.parseItemCnn) 

    def parseItemCnn(self,response):
        links = response.xpath('//h3[@class="item-title"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parseItem) 

            
    def parseItem(self,response):
        global cnn_counter
        title = response.xpath('//h1[@class="story-title"]/text()').get()

        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()       
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub( "\xa0","",final_text)

        date = response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()
        final_date = formatdate(date)

        #check if this an article and not an photo gallery 
        url = response.url
        article_type = url.split('/')[5]
        contains_photos = re.search('Photos',clear_characters)
        if article_type == CNN_VARS['ARTICLE_TYPE'] and contains_photos is None and cnn_counter < 300:
            cnn_counter += 1
            yield{ 
                "topic": GENERAL_CATEGORIES['CULTURE'],
                "subtopic": GENERAL_CATEGORIES['CULTURE'],
                "website": CNN_VARS['WEBSITE'],
                "title": title,
                "article_date": final_date,
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "article_body": re.sub( r'\n|\t',"",clear_characters),
                "url": url,     
            }
#next three functions for cnn infinite scroll for entertainment
    def parseInfiniteCnnPS(self,response):
        pages =  CNN_VARS['CNN_CULTURE_PAGES']
        for page in range(0, pages ,9):
            url = 'https://www.cnn.gr/style/psyxagogia?start={}'.format(page)
            yield Request(url, callback = self.parseItemCnnPS) 

    def parseItemCnnPS(self,response):
        links = response.xpath('//h3[@class="item-title"]/a/@href').getall()
        for link in links:
            url = response.urljoin(link)
            yield Request(url,callback=self.parseItemPS) 

            
    def parseItemPS(self,response):
        global cnn_counter
        title = response.xpath('//h1[@class="story-title"]/text()').get()

        text = response.xpath('//div[@class="story-content"]//p/text()|//div[@class="story-content"]//strong/text()|//div[@class="story-content"]//a/text()').getall()
        list_to_string = " ".join(" ".join(text))
        markspaces = re.sub( "  ", "space",list_to_string)
        uneeded_spaces = re.sub( " ", "",markspaces)
        final_text = re.sub( "space", " ",uneeded_spaces)
        clear_characters = re.sub( "\xa0","",final_text)

        date = response.xpath('//div[@class="story-date story-credits icon icon-time"]/text()').get()
        final_date = formatdate(date)

        #check if this an article and not an photo gallery 
        url = response.url
        article_type = url.split('/')[5]
        contains_photos = re.search('Photos',clear_characters)
        if article_type == CNN_VARS['ARTICLE_TYPE'] and contains_photos is None and cnn_counter < 300:
            cnn_counter += 1
            yield{ 
                "topic": GENERAL_CATEGORIES['CULTURE'],
                "subtopic": GENERAL_CATEGORIES['CULTURE'],
                "website": CNN_VARS['WEBSITE'],
                "title": title,
                "article_date": final_date,
                "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="story-author"]/text()').get()),
                "article_body": re.sub( r'\n|\t',"",clear_characters),
                "url": url,     
            }
    def process_cnn(self, request):
        global cnn_counter
        if cnn_counter < 300:
            return request

    def parse_thetoc(self,response):
        global thetoc_counter
        #check if we are in an articles url
        title = response.xpath('//div[@class="article-title"]//h1/text()').get() 
        if title is not None and thetoc_counter < 300:
            text = response.xpath('//div[@class="article-content articleText"]//p/text()|//div[@class="article-content articleText"]//strong/text()|//div[@class="article-content articleText"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            date = response.xpath('//span[@class="article-date"]/text()').get()
            final_date = THETOC_VARS['full_date'] +formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            #check if we are in an article and that this article doesn't have any images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:               
                thetoc_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic": GENERAL_CATEGORIES['CULTURE'],
                    "website": THETOC_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date,
                    "author": re.sub(r'\n|\t',"",response.xpath('//div[@class="author-social"]//h5/a/span[2]/text()').get()),
                    "article_body": re.sub( r'\n|\t',"",clear_characters),
                    "url": url,                
                }
    def process_thetoc(self, request):
        global thetoc_counter
        if thetoc_counter < 300:
            return request

    def parse_protagon(self,response):
        global protagon_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title"]/text()').get() 
        if title is not None and protagon_counter < 300 :
            #check if we are in the correct category
            sub = response.xpath('//span[@class="s_roumpr"]/a/text()').get()
            if sub == PROTAGON_VARS['CATEGORY_CULTURE']:
                #get the article's text
                text = response.xpath('//div[@class="left-single-column "]//p/text()|//div[@class="left-single-column "]//strong/text()|//div[@class="left-single-column "]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub( "\xa0","",final_text)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                author = re.findall(r"(\w+).(\w+)",response.xpath('//strong[@class="generalbold uppercase"]/a/text()').get())
                list_to_tuple = author[0]
                author = ' '.join(list_to_tuple)

                date = response.xpath('//span[@class="generalight uppercase"]/text()').get()
                final_date = formatdate(date)

                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                    protagon_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['CULTURE'],
                        "subtopic": GENERAL_CATEGORIES['CULTURE'],
                        "website": PROTAGON_VARS['WEBSITE'],
                        "title": title,
                        "article_date": final_date, 
                        "author": author,
                        "article_body": re.sub( r'\s\s\s',"",clear_characters),
                        "url": url,                
                    }
    def process_protagon(self, request):
        global protagon_counter
        if protagon_counter < 300:
            return request

    def parse_in(self,response):
        #check if we are in an articles url
        global in_counter
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get() 
        if title is not None and in_counter < 300 :
            text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                in_counter +=1
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic":IN_VARS['CULTURE_SUBTOPIC'],
                    "website": IN_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date, 
                    "author": response.xpath('//span[@class="vcard author"]//a/text()').get(),
                    "article_body": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
                }
    def process_in(self, request):
        global in_counter
        if in_counter < 300:
            return request


    def parse_newpost(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="article-title"]/text()').get() 
        if title is not None :
            text = response.xpath('//div[@class="article-main clearfix"]//p/text()|//div[@class="article-main clearfix"]//strong/text()|//div[@class="article-main clearfix"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub( "\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = (response.xpath('//small[@class="article-created-time"]/text()').get()).split('/')[0]
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic": GENERAL_CATEGORIES['CULTURE'],
                    "website": NEWPOST_VARS['WEBSITE'],
                    "title": title,
                    "article_date": final_date, 
                    "author": NEWPOST_VARS['WEBSITE'],
                    "article_body": re.sub( r'\s\s\s',"",clear_characters),
                    "url": url,                
            }

    def parse_iefimerida(self,response):
        global iefimerida_counter
        #check if we are in an articles url
        title = response.xpath('//h1/span/text()').get() 
        if title is not None and iefimerida_counter < 300:
            text = response.xpath('//div[@class="field--name-body on-container"]//p/text()|//div[@class="field--name-body on-container"]/strong/text()|//div[@class="field--name-body on-container"]//p/*/text()|//div[@class="field--name-body on-container"]//p//li/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url

            date = response.xpath('//span[@class="created"]/text()').get()
            final_date = formatdate(date)

            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                iefimerida_counter +=1
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic": GENERAL_CATEGORIES['CULTURE'],
                    "website": IEFIMERIDA_VARS['AUTHOR'],
                    "title": title,
                    "article_date": final_date, 
                    "author": IEFIMERIDA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }
    def process_iefimerida(self, request):
        global iefimerida_counter
        if iefimerida_counter < 300:
            return request

    def parse_tanea(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title black-c"]/text()').get()
        if title is not None: 
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//h3/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            date = response.xpath('//span[@class="firamedium postdate updated"]/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            subtopic = url.split('/')[7]
            if len(subtopic)>15 :
                subtopic = TANEA_VARS['CATEGORY_CULTURE']
            
            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic": GENERAL_CATEGORIES['CULTURE'],
                    "website": TANEA_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": TANEA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_tovima(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1[@class="entry-title thirty black-c zonabold"]/text()').get() 
        if title is not None:
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="main-content pos-rel article-wrapper"]//p/text()|//div[@class="main-content pos-rel article-wrapper"]//strong/text()|//div[@class="main-content pos-rel article-wrapper"]//h3/text()|//div[@class="main-content pos-rel article-wrapper"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            date = response.xpath('//time/span/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic": GENERAL_CATEGORIES['CULTURE'],
                    "website": TOVIMA_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": TOVIMA_VARS['AUTHOR'],
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_kathimerini(self,response):
        #check if we are in an articles url
        title = response.xpath('//h2[@class="item-title"]/text()').get() 
        if title is not None:
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="freetext"]//p/text()|//div[@class="freetext"]//strong/text()|//div[@class="freetext"]//h3/text()|//div[@class="freetext"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            author = response.xpath('//span[@class="item-author"]/a/text()').get()
            if author == KATHIMERINI_VARS['CATEGORY_AUTHOR'] :
                author = KATHIMERINI_VARS['AUTHOR']
            #check if we are in an article and that it doesn't have images
            if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic": response.xpath('//span[@class="item-category"]/a/text()').get(),
                    "website": KATHIMERINI_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                    "url": url,                
                }

    def parse_naftemporiki(self,response):
        global naftemporiki_counter
        #check if we are in an articles url
        title = response.xpath('//h2[@id="sTitle"]/text()').get() 
        if title is not None and naftemporiki_counter < 300:
            #check if we are in the correct category
            subtopic = response.xpath('//span[@itemprop="articleSection"]/text()').get()
            if subtopic == NAFTEMPORIKI_VARS['CATEGORY_CULTURE'] :
                
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                date = response.xpath('//div[@class="Date"]/text()').get()
                final_date = formatdate(date)

                text = response.xpath('//div[@class="entityMain article"]//p/text()|//div[@class="entityMain article"]/p/strong/text()|//div[@class="entityMain article"]//h3/text()|//div[@class="entityMain article"]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(final_text)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None: 
                    naftemporiki_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['CULTURE'],
                        "subtopic": response.xpath('//div[@class="Breadcrumb"]/a[2]/text()').get(),
                        "website": NAFTEMPORIKI_VARS['AUTHOR'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": NAFTEMPORIKI_VARS['AUTHOR'],
                        "article_body": re.sub( r'\s\s\s|\n',"",final_text),
                        "url": url,                
                    }

    def process_request(self, request):
        global naftemporiki_counter
        if naftemporiki_counter < 300:
            return request

    def parse_lifo(self,response):
        global lifo_counter
        #check if we are in an articles url
        title = response.xpath('//h1[@itemprop="headline"]/text()|//meta[@itemprop="headline"]/text()|//h1/*/text()').get() 
        if title is not None and lifo_counter < 300 :
            list_to_string = " ".join(" ".join(title))
            markspaces = re.sub( "       ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            put_spaces_back = re.sub( "space", " ",uneeded_spaces)
            final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

            text = response.xpath('//div[@class="clearfix wide bodycontent"]//p/text()|//div[@class="clearfix wide bodycontent"]/p/strong/text()|//div[@class="clearfix wide bodycontent"]//h3/text()|//div[@class="clearfix wide bodycontent"]//p/*/text()').getall()
            list_to_string = " ".join(" ".join(text))
            markspaces = re.sub( "  ", "space",list_to_string)
            uneeded_spaces = re.sub( " ", "",markspaces)
            final_text = re.sub( "space", " ",uneeded_spaces)
            clear_characters = re.sub("\xa0","",final_text)

            date = response.xpath('//time/text()').get()
            final_date = formatdate(date)

            author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
            if author == None:
                author = LIFO_VARS['AUTHOR']

            #flag to see later on if we have tweets ect
            flag = re.search(r"@",clear_characters)
            url = response.url
            
            #check if we are in an article and that it doesn't have images
            if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                lifo_counter += 1
                yield {
                    "topic": GENERAL_CATEGORIES['CULTURE'],
                    "subtopic": GENERAL_CATEGORIES['CULTURE'],
                    "website": LIFO_VARS['AUTHOR'],
                    "title": final_title,
                    "article_date": final_date, 
                    "author": author,
                    "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                    "url": url,                
                }

    def process_lifo(self, request):
        global lifo_counter
        if lifo_counter < 300:
            return request

    def parse_efsyn(self,response):
        global efsyn_counter
        #check if we are in an articles url
        title = response.xpath('//h1[1]/text()').get() 
        if title is not None and efsyn_counter < 300:
            #check if we are in the correct category
            subtopic = response.xpath('//article/a/@href').get()
            category = subtopic.split('/')[1]
            if category == EFSYN_VARS['CATEGORY_CULTURE']:
                
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                text = response.xpath('//div[@class="article__body js-resizable"]//p/text()|//div[@class="article__body js-resizable"]/p/strong/text()|//div[@class="article__body js-resizable"]//h3/text()|//div[@class="article__body js-resizable"]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                author = response.xpath('//div[@class="article__author"]//a/text()').get()
                if author == None:
                    author = response.xpath('//div[@class="article__author"]/span/text()').get()

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                date = response.xpath('//time/text()').get()
                final_date = formatdate(date)

                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                    efsyn_counter += 1
                    yield {
                        "topic": GENERAL_CATEGORIES['CULTURE'],
                        "subtopic": EFSYN_VARS['ART'],
                        "website": EFSYN_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": author,
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }
    def process_efsyn(self, request):
        global efsyn_counter
        if efsyn_counter < 300:
            return request

    def parse_popaganda(self,response):
        #check if we are in an articles url
        global popaganda_counter
        title = response.xpath('//h1/text()').get() 
        if title is not None and popaganda_counter < 200: 
            #check if we are in the correct category
            category = response.xpath('//div[@class="category"]/a/text()').get()
            if category == POPAGANDA_VARS['CATEGORY_CULTURE'] :
                
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                text = response.xpath('//div[@class="post-content newstrack-post-content"]//p/text()|//div[@class="post-content newstrack-post-content"]/p/strong/text()|//div[@class="post-content newstrack-post-content"]//h3/text()|//div[@class="post-content newstrack-post-content"]//p/*/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = re.sub("\xa0","",final_text)

                author = response.xpath('//div[@class="author"]/a/text()|//div[@itemprop="author"]/*/text()').get()
                if author == None:
                    author = POPAGANDA_VARS['WEBSITE']

                date = response.xpath('//div[@class="date"]/text()|//div[@class="fullscreen-date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url

                #check if we are in an article and that it doesn't have images
                if title is not None and len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                    popaganda_counter +=1
                    yield {
                        "topic": GENERAL_CATEGORIES['CULTURE'],
                        "subtopic": POPAGANDA_VARS['CULTURE'],
                        "website": POPAGANDA_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": POPAGANDA_VARS['WEBSITE'],
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }
    def process_popaganda(self, request):
        global popaganda_counter
        if popaganda_counter < 200:
            return request


    def parse_topontiki(self,response):
        #check if we are in an articles url
        title = response.xpath('//h1/text()').get()
        if title is not None :
            sub = response.xpath('//h2/a[1]/text()').get()
            #check if we are in the correct category
            if sub == TOPONTIKI_VARS['CATEGORY_CULTURE']: 
                list_to_string = " ".join(" ".join(title))
                markspaces = re.sub( "       ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                put_spaces_back = re.sub( "space", " ",uneeded_spaces)
                final_title = re.sub(r'\n|\s\s\s',"",put_spaces_back)

                text = response.xpath('//div[@class="field-item even"]//p/text()|//div[@class="field-item even"]//p/*/text()|//div[@class="field-item even"]//p//span/text()').getall()
                list_to_string = " ".join(" ".join(text))
                markspaces = re.sub( "  ", "space",list_to_string)
                uneeded_spaces = re.sub( " ", "",markspaces)
                final_text = re.sub( "space", " ",uneeded_spaces)
                clear_characters = final_text.replace("\xa0","")

                date = response.xpath('//span[@class="date"]/text()').get()
                final_date = formatdate(date)

                #flag to see later on if we have tweets ect
                flag = re.search(r"@",clear_characters)
                url = response.url
                
                #check if we are in an article and that it doesn't have images
                if len(clear_characters)>GENERAL_CATEGORIES['ALLOWED_LENGTH']and flag is None:
                    yield {
                        "topic": GENERAL_CATEGORIES['CULTURE'],
                        "subtopic": GENERAL_CATEGORIES['CULTURE'],
                        "website": TOPONTIKI_VARS['WEBSITE'],
                        "title": final_title,
                        "article_date": final_date, 
                        "author": response.xpath('//a[@class="author"]/text()').get(),
                        "article_body": re.sub( r'\s\s\s|\n',"",clear_characters),
                        "url": url,                
                    }
