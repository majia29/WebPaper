# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from time import sleep

from paper import Paper
from pinyin import Pinyin
from util import *

__all__ = [
    "InfoQPaper",
]


class InfoQPaper(Paper):
    _website   = "www.infoq.cn"
    _paperpath = "/article"
    _sitename  = "InfoQ中文网"

    def __init__(self, url, driver=None):
        """ InfoQ文章类初始化
        """
        # 标准类变量
        self._class_name = self.__class__.__name__
        # 输入参数检查
        self.check_url(url, site=self._website, path=self._paperpath)
        # 创建内部对象
        self._driver = driver or init_webdriver("chrome", "drivers/chromedriver")
        self.open(url)

    def __enter__(self):
        return self._driver

    def __exit__(self, type, value, trace):
        if self._driver:
            self._driver.quit()

    @property
    def url(self):
        return self._driver.current_url

    @property
    def html_source(self):
        return self._driver.page_source

    def _get_title(self):
        """ 抽取文章标题
        """
        return self._driver.title

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        publish_info = []
        #<div class="page-article">
        #   <div class="main-content">
        #       <div class="article-main">
        #           <div class="article-detail">
        #               <ul class="author">
        #                   <li
        #                       <a class="com-author-name">
        #               <ul class="translate">
        #                   <li
        #                       <a class="com-author-name">
        #           <div class="article-detail">
        #               <p class="detail read-number">
        #                   <span class="views">
        #                   <span class="date">
        page_article = self._driver.find_element_by_class_name("page-article")
        main_content = page_article.find_element_by_class_name("main-content")
        article_main = main_content.find_element_by_class_name("article-main")
        article_detail_elements = article_main.find_elements_by_class_name("article-detail")
        try:
            author = article_detail_elements[0].find_element_by_class_name("author")
            com_author_name = author.find_element_by_class_name("com-author-name")
            com_author_name_text = com_author_name.get_attribute('innerHTML').strip()
            publish_info.append("作者: " + com_author_name_text)
        except:
            pass
        try:
            translate = article_detail_elements[0].find_element_by_class_name("translate")
            com_author_name = translate.find_element_by_class_name("com-author-name")
            com_author_name_text = com_author_name.get_attribute('innerHTML').strip()
            publish_info.append("译者: " + com_author_name_text)
        except:
            pass
        try:
            read_number = article_detail_elements[1].find_element_by_class_name("read-number")
            article_date = read_number.find_element_by_class_name("date")
            article_date_text = article_date.get_attribute('innerHTML').strip()
            publish_info.append("发布日期: " + article_date_text)
        except:
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        publish_date = today(fmt="%Y%m%d")
        #<div class="page-article">
        #   <div class="main-content">
        #       <div class="article-main">
        #           <div class="article-detail">
        #           <div class="article-detail">
        #               <span class="date">
        page_article = self._driver.find_element_by_class_name("page-article")
        main_content = page_article.find_element_by_class_name("main-content")
        article_main = main_content.find_element_by_class_name("article-main")
        article_detail_elements = article_main.find_elements_by_class_name("article-detail")
        article_detail = article_detail_elements[1]
        article_date = article_detail.find_element_by_class_name("date")
        article_date_text = article_date.get_attribute('innerHTML').strip()
        # 发布日期转换
        publish_date = text2date(article_date_text, fmt="%Y%m%d")
        return publish_date

    def _gen_markdown(self):
        #<div class="page-article">
        #   <div class="main-content">
        #       <div class="article-main">
        #           <div class="article-cover">
        #           <div class="article-typo article-content">
        page_article = self._driver.find_element_by_class_name("page-article")
        main_content = page_article.find_element_by_class_name("main-content")
        article_main = main_content.find_element_by_class_name("article-main")
        # patch: 包含封面图
        article_cover = article_main.find_element_by_class_name("article-cover")
        article_cover_text = article_cover.get_attribute('innerHTML')
        article_content = article_main.find_element_by_class_name("article-content")
        article_content_text = article_content.get_attribute('innerHTML')
        html_text = article_cover_text + article_content_text
        md_text = html2markdown(html_text)
        return md_text

    def _gen_summary(self):
        """ 生成文章摘要
        """
        return "-摘要功能未实现-"

    def _gen_tags(self):
        """ 生成文章标签列表
        """
        return ["-标签功能未实现-"]

    def open(self, url):
        """ 读取文章，并生成文章对象属性
        """
        self.check_url(url, self._website, self._paperpath)
        self._driver.get(url)
        # patch: 等待页面真正加载完成
        sleep(3)
        pinyin = Pinyin()
        self.title = self._get_title()
        self.title_full = pinyin.pinyin(self.title)
        self.title_abbr = pinyin.pinyin(self.title, initial=True)
        self.publish_info = self._get_publish_info()
        self.publish_date = self._get_publish_date()
        self.markdown     = self._gen_markdown()

    def close(self):
        self.__exit__()
