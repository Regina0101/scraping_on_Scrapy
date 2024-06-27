import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "quotes.json", "FEED_EXPORT_INDENT": "2",
                       "FEED_EXPORT_ENCODING": "utf-8"}
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            yield {
                "tags": quote.xpath("div[@class='tags']/a/text()").extract(),
                "author": quote.xpath("span/small/text()").get(),
                "quote": quote.xpath("span[@class='text']/text()").get()
            }
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)


class AuthorsSpider(CrawlSpider):
    name = 'authors'
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "authors.json", "FEED_EXPORT_INDENT": "2",
                       "FEED_EXPORT_ENCODING": "utf-8"}
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    rules = (Rule(LinkExtractor(restrict_xpaths="//div[@class='quote']/span/a"), callback="parse_item", follow=True),)

    def parse_item(self, response):
        item = {
            "fullname": response.xpath('//div[@class="author-details"]/h3[@class="author-title"]/text()').get(),
            "born_date": response.xpath(
                '//div[@class="author-details"]/p/span[@class="author-born-date"]/text()').get(),
            "born_location": response.xpath(
                '//div[@class="author-details"]/p/span[@class="author-born-location"]/text()').get(),
            "description": response.xpath(
                '//div[@class="author-details"]/div[@class="author-description"]/text()').get().strip()
        }

        return item


process = CrawlerProcess()
process.crawl(QuotesSpider)
process.crawl(AuthorsSpider)
process.start()
