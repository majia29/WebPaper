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
    "SFPaper",
]


class SFPaper(Paper):
    _website   = "segmentfault.com"
    _paperpath = "/a"
    _sitename  = "思否"

    def _get_title(self):
        """ 抽取文章标题
        """
        title_text = self._driver.title
        #<div class="post-topheader__info">
        #    <h1 class="articleTitle">
        try:
            post_topheader_info = self._driver.find_element_by_class_name("post-topheader__info")
            a = post_topheader_info.find_element_by_xpath("//h1[@id='articleTitle']/a")
            title_text = a.get_attribute('innerHTML').strip()
        except:
            pass
        return title_text

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        publish_info = []
        #<div class="post-topheader">
        #   <div class="post-topheader__info">
        #       <div class="article__authorright">
        #           <div class="article__authormeta">
        #               <a><strong>AAA
        #           <span>YYYY-MM-DD 发布
        post_topheader = self._driver.find_element_by_class_name("post-topheader")
        post_topheader_info = post_topheader.find_element_by_class_name("post-topheader__info")
        article_authorright = post_topheader_info.find_element_by_class_name("article__authorright")
        try:
            # 抽取作者
            article_authormeta = article_authorright.find_element_by_class_name("article__authormeta")
            #a = article_authormeta.find_elements_by_tag_name("a")[0]
            #strong = a.find_elements_by_tag_name("strong")[0]
            strong = article_authormeta.find_element_by_xpath("//a[@class='mr5']/strong")
            strong_text = strong.get_attribute("innerHTML").strip()
            publish_info.append("作者: " + strong_text)
            # 抽取发布日期
            span = post_topheader_info.find_elements_by_xpath("//div[@class='article__authorright']/span")[0]
            span_text = span.get_attribute('innerHTML').strip()
            article_date_text = span_text.split(" ")[0]
            publish_info.append("发布日期: " + article_date_text)
        except:
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        publish_date = today(fmt="%Y%m%d")
        #<div class="post-topheader">
        #   <div class="post-topheader__info">
        #       <div class="article__authorright">
        #           <div class="article__authormeta">
        #               <a><strong>AAA
        #           <span>YYYY-MM-DD 发布
        try:
            post_topheader = self._driver.find_element_by_class_name("post-topheader")
            post_topheader_info = post_topheader.find_element_by_class_name("post-topheader__info")
            span = post_topheader_info.find_elements_by_xpath("//div[@class='article__authorright']/span")[0]
            span_text = span.get_attribute('innerHTML').strip()
            article_date_text = span_text.split(" ")[0]
            # 发布日期转换
            publish_date = text2date(article_date_text, fmt="%Y%m%d")
        except:
            pass
        return publish_date

    def _get_content(self):
        #<div class="article fmt article-content">
        article_content = self._driver.find_element_by_class_name("article-content")
        return article_content
        
    def _gen_markdown(self):
        content = self._get_content()
        html_text = content.get_attribute('innerHTML')
        md_text = html2markdown(html_text, ext="pretty")
        return md_text

