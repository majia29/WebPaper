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
    "Www36KrPaper",
]


class Www36KrPaper(Paper):
    _website   = "36kr.com"
    _paperpath = "/p"
    _sitename  = "36氪"

    def _get_title(self):
        """ 抽取文章标题
        """
        title_text = self._driver.title
        #<div id="app">
        #   <div class="kr-article-box"
        #       <div class="kr-article"
        #           <div class="article-content"
        #               <h1 class="article-title">${标题}</h1>
        try:
            app = self._driver.find_element_by_id("app")
            kr_article_box = app.find_element_by_class_name("kr-article-box")
            kr_article = kr_article_box.find_element_by_class_name("kr-article")
            article_content = kr_article.find_element_by_class_name("article-content")
            h1 = article_content.find_element_by_class_name("article-title")
            title_text = h1.get_attribute('innerHTML').strip()
        except:
            pass
        return title_text

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        publish_info = []
        #<div id="app">
        #   <div class="kr-article-box"
        #       <div class="kr-article"
        #           <div class="kr-article-inner"
        #               <div class="article-content"
        #                   <h1 class="article-title">${标题}</h1>
        #                   <div class="article-title-icon"
        #                       <a class="title-icon-item item-a">${作者}</a>
        #                       <span class="title-icon-item item-time">·${时间}</span>
        #                   <div class="summary">
        #                   <div class="common-width content articleDetailContent kr-rich-text-wrapper">
        app = self._driver.find_element_by_id("app")
        kr_article_box = app.find_element_by_class_name("kr-article-box")
        kr_article = kr_article_box.find_element_by_class_name("kr-article")
        kr_article_inner = kr_article.find_element_by_class_name("kr-article-inner")
        article_content = kr_article_inner.find_element_by_class_name("article-content")
        try:
            # 抽取发布者
            item_a = article_content.find_element_by_class_name("item-a")
            item_a_text = item_a.get_attribute('innerHTML').strip()
            publish_info.append("发布: " + item_a_text)
            # 抽取发布日期
            item_time = article_content.find_element_by_class_name("item-time")
            item_time_text = item_time.get_attribute('innerHTML').strip()
            item_time_text = text2date(item_time_text, fmt="%Y-%m-%d")
            publish_info.append("发布日期: " + item_time_text)
        except:
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        publish_date = today(fmt="%Y%m%d")
        #<div id="app">
        #   <div class="kr-article-box"
        #       <div class="kr-article"
        #           <div class="kr-article-inner"
        #               <div class="article-content"
        #                   <h1 class="article-title">${标题}</h1>
        #                   <div class="article-title-icon"
        #                       <a class="title-icon-item item-a">${作者}</a>
        #                       <span class="title-icon-item item-time">·${时间}</span>
        try:
            app = self._driver.find_element_by_id("app")
            kr_article_box = app.find_element_by_class_name("kr-article-box")
            kr_article = kr_article_box.find_element_by_class_name("kr-article")
            kr_article_inner = kr_article.find_element_by_class_name("kr-article-inner")
            article_content = kr_article_inner.find_element_by_class_name("article-content")
            item_time = article_content.find_element_by_class_name("item-time")
            item_time_text = item_time.get_attribute('innerHTML').strip()
            # 发布日期转换
            publish_date = text2date(item_time_text, fmt="%Y%m%d")
        except:
            pass
        return publish_date

    def _gen_markdown(self):
        #<div id="app">
        #   <div class="kr-article-box"
        #       <div class="kr-article"
        #           <div class="kr-article-inner"
        #               <div class="article-content"
        #                   <div class="common-width content articleDetailContent kr-rich-text-wrapper">
        app = self._driver.find_element_by_id("app")
        kr_article_box = app.find_element_by_class_name("kr-article-box")
        kr_article = kr_article_box.find_element_by_class_name("kr-article")
        kr_article_inner = kr_article.find_element_by_class_name("kr-article-inner")
        article_content = kr_article_inner.find_element_by_class_name("article-content")
        content = article_content.find_element_by_class_name("content")
        html_text = content.get_attribute('innerHTML')
        md_text = html2markdown(html_text, ext="pretty")
        return md_text

