# -*- coding: utf-8 -*-
import re
from datetime import datetime
import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobboleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):

    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/'] # 起始url

    def parse(self, response):
        """
        1.获取列表页中的文章url并交给scrapy下载后并进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        # 解析列表页中的所有文章url并交给scrapy下载后进行解析
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first()
            yield Request(url=parse.urljoin(response.url, post_url), meta={"font_image_url": image_url}, callback=self.parse_detail)
        # 提取下一页并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        爬取数据
        """
        # front_image_url = response.meta.get("font_image_url", "")
        # title = response.xpath("//div[@class='entry-header']/h1/text()").extract_first("")  # 标题
        # create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·", "").strip()    # 日期
        # praise_nums = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]    # 点赞数
        # fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]   # 收藏人数
        # match_re = re.match(".*?(\d+).*", fav_nums)
        #
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0] # 评论人数
        # match_re = re.match(".*?(\d+).*]", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.xpath("//div[@class='entry']").extract()[0]  # 日期
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list= [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)   # 标签
        #
        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     create_date = datetime.strftime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.now().date()
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content

        article_item = JobboleArticleItem()
        # 通过itemload加载item
        front_image_url = response.meta.get("font_image_url", "")
        item_loader = ArticleItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_xpath("title", "//div[@class='entry-header']/h1/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("create_date", "//p[@class='entry-meta-hide-on-mobile']/text()")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_xpath("praise_nums", "//span[contains(@class, 'vote-post-up')]/h10/text()")
        item_loader.add_xpath("comment_nums", "//a[@href='#article-comment']/span/text()")
        item_loader.add_xpath("fav_nums", "//span[contains(@class, 'bookmark-btn')]/text()")
        item_loader.add_xpath("content", "//div[@class='entry']")
        item_loader.add_xpath("tags", "//p[@class='entry-meta-hide-on-mobile']/a/text()")
        article_item= item_loader.load_item()
        yield article_item




