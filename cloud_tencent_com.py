# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    )

from paper import Paper
from util import *

__all__ = [
    "TencentCloudPaper",
]


class TencentCloudPaper(Paper):
    _website   = "cloud.tencent.com"
    _paperpath = "/developer/article"
    _sitename  = "腾讯云"

    def _get_title(self):
        """ 抽取文章标题
        """
        title_text = self._driver.title
        #<div class="J-body col-body pg-article">
        #    <h1 class="col-article-title J-articleTitle">
        try:
            pg_article = self._driver.find_element_by_class_name("pg-article")
            article_title = pg_article.find_element_by_class_name("J-articleTitle")
            title_text = article_title.get_attribute('innerHTML').strip()
        except:
            pass
        return title_text

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        publish_info = []
        #<div class="J-body col-body pg-article">
        #   <a class="author-name">AAA
        #<div class="col-article-time">
        #   <time datetime="YYYY-MM-DD hh:mi:ss">
        try:
            # 抽取作者
            pg_article = self._driver.find_element_by_class_name("pg-article")
            author_name = pg_article.find_element_by_xpath("//a[@class='author-name']")
            author_name_text = author_name.get_attribute("innerHTML").strip()
            publish_info.append("作者: " + author_name_text)
            # 抽取发布日期
            article_time = self._driver.find_element_by_class_name("col-article-time")
            tag_time = article_time.find_element_by_tag_name("time")
            time_text = tag_time.get_attribute("datetime").strip()
            article_date_text = time_text.split(" ")[0]
            publish_info.append("发布日期: " + article_date_text)
        except:
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        publish_date = today(fmt="%Y%m%d")
        #<div class="col-article-time">
        #   <time datetime="YYYY-MM-DD hh:mi:ss">
        try:
            article_time = self._driver.find_element_by_class_name("col-article-time")
            tag_time = article_time.find_element_by_tag_name("time")
            time_text = tag_time.get_attribute("datetime").strip()
            article_date_text = time_text.split(" ")[0]
            # 发布日期转换
            publish_date = text2date(article_date_text, fmt="%Y%m%d")
        except:
            pass
        return publish_date

    def _gen_markdown(self):
        #<div class="J-body col-body pg-article">
        #    <div class="c-markdown J-articleContent">
        articlecontent = self._driver.find_element_by_class_name("J-articleContent")
        html_text = articlecontent.get_attribute('innerHTML')
        md_text = html2markdown(html_text, ext="pretty")
        return md_text

