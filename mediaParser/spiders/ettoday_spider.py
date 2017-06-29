#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
東森時報
"""
import scrapy
from scrapy.selector import Selector
import time
import re

TODAY = time.strftime('%Y/%m/%d')
TODAY_URL = time.strftime('%Y-%m-%d')
ROOT_URL = 'http://www.ettoday.net'


class EttodaySpider(scrapy.Spider):
    name = "ettoday"

    def start_requests(self):
        urls = [
            'http://www.ettoday.net/news/news-list-' + TODAY_URL + '-0.htm'
        ]
        for url in urls:
            meta = {'iter_time': 0}
            yield scrapy.Request(url, callback=self.parse_news_list, meta=meta)

    def parse_news_list(self, response):
        has_next_page = True
        response.meta['iter_time'] += 1
        isFirstIter = response.meta['iter_time'] == 1
        prefix = '.part_list_2' if isFirstIter else ''
        for news_item in response.css(prefix+' h3'):
            url = news_item.css('a::attr(href)').extract_first()
            url = ROOT_URL + url
            category = news_item.css('em::text').extract_first()
            date_time = news_item.css('span::text').extract_first()

            if TODAY not in date_time:
                has_next_page = False
                continue

            response.meta['category'] = category
            yield scrapy.Request(url, callback=self.parse_news, meta=response.meta)
        if(has_next_page):
            tFile = time.strftime('%Y%m%d') + '.xml'
            yield scrapy.FormRequest(url="http://www.ettoday.net/show_roll.php",
                                     callback=self.parse_news_list,
                                     meta=response.meta,
                                     formdata={'offset': str(response.meta['iter_time']),
                                               'tPage': '3',
                                               'tFile': tFile,
                                               'tOt': '0',
                                               'tSi': '100'
                                               })

        # get scroll news list
        # yield scrapy.Request(url, callback=self.parse_news_list)

    def parse_news(self, response):
        title = response.css('h1.title::text').extract_first()
        if not title:
            title = response.css('h2.title::text').extract_first()
            if not title:
                title = response.css('h1.title_article::text').extract_first()

        p_list = response.css('.story p::text').extract()

        content = ''
        for p in p_list:
            content += p

        yield {
            'website': "東森新聞雲",
            'url': response.url,
            'title': title,
            'date': time.strftime('%Y-%m-%d'),
            'content': content,
            'category': response.meta['category']
        }