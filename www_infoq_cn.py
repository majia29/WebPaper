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
    "IQPaper",
]


class IQPaper(Paper):
    _website   = "www.infoq.cn"
    _paperpath = "/article"
    _sitename  = "InfoQ中文网"

    def _get_title(self):
        """ 抽取文章标题
        """
        title_text = self._driver.title
        #<div class="page-article">
        #   <div class="main-content">
        #       <div class="article-main">
        #           <h1>
        page_article = self._driver.find_element_by_class_name("page-article")
        main_content = page_article.find_element_by_class_name("main-content")
        article_main = main_content.find_element_by_class_name("article-main")
        try:
            h1 = self._driver.find_element_by_tag_name("h1")
            title_text = h1.get_attribute('innerHTML').strip()
        except:
            pass
        return title_text

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
            # 抽取作者
            author = article_detail_elements[0].find_element_by_class_name("author")
            com_author_name = author.find_element_by_class_name("com-author-name")
            com_author_name_text = com_author_name.get_attribute('innerHTML').strip()
            publish_info.append("作者: " + com_author_name_text)
            # 抽取译者
            translate = article_detail_elements[0].find_element_by_class_name("translate")
            com_author_name = translate.find_element_by_class_name("com-author-name")
            com_author_name_text = com_author_name.get_attribute('innerHTML').strip()
            publish_info.append("译者: " + com_author_name_text)
            # 抽取发布日期
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
        try:
            page_article = self._driver.find_element_by_class_name("page-article")
            main_content = page_article.find_element_by_class_name("main-content")
            article_main = main_content.find_element_by_class_name("article-main")
            article_detail_elements = article_main.find_elements_by_class_name("article-detail")
            article_detail = article_detail_elements[1]
            article_date = article_detail.find_element_by_class_name("date")
            article_date_text = article_date.get_attribute('innerHTML').strip()
            # 发布日期转换
            publish_date = text2date(article_date_text, fmt="%Y%m%d")
        except:
            pass        
        return publish_date

    def _get_content(self):
        #<div class="page-article">
        #   <div class="main-content">
        #       <div class="article-main">
        #           <div class="article-typo article-content">
        page_article = self._driver.find_element_by_class_name("page-article")
        main_content = page_article.find_element_by_class_name("main-content")
        article_main = main_content.find_element_by_class_name("article-main")
        article_content = article_main.find_element_by_class_name("article-content")
        return article_content

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
        md_text = html2markdown(html_text, ext="pretty")
        return md_text

