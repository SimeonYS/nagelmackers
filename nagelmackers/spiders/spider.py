import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import NagelmackersItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class NagelmackersSpider(scrapy.Spider):
	name = 'nagelmackers'
	start_urls = ['https://www.nagelmackers.be/nl/over-ons/actueel?page=1']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="c-pagination__item  c-pagination__next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):

		date = response.xpath('//p[@class="o-media__meta  u-mb05"]/text()').get().strip()
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="c-main__section"]//p//text()[not (ancestor::p[@class="c-author__title"])]').getall()
		content = [p.strip() for p in content if p.strip()][:-8]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=NagelmackersItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
