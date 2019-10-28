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
    "CSPaper",
]


class CSPaper(Paper):
    _website   = "coolshell.cn"
    _paperpath = "/articles"
    _sitename  = "酷壳"

    def _get_title(self):
        """ 抽取文章标题
        """
        title_text = self._driver.title
        #<header class="entry-header">
        #    <h1 class="entry-title">
        try:
            entry_header = self._driver.find_element_by_class_name("entry-header")
            entry_title = entry_header.find_element_by_class_name("entry-title")
            title_text = entry_title.get_attribute('innerHTML').strip()
        except:
            pass
        return title_text

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        publish_info = []
        #<header class="entry-header">
        #    <div class="entry-meta">
        #        <h5 class="entry-date">
        #             <time class="entry-date">2019年04月17日 </time>
        #             <span class="author vcard">
        #                 <a rel="author">陈浩</a>
        entry_header = self._driver.find_element_by_class_name("entry-header")
        entry_meta = entry_header.find_element_by_class_name("entry-meta")
        try:
            # 抽取作者
            author = entry_meta.find_element_by_class_name("author")
            a = author.find_elements_by_tag_name("a")[0]
            a_text = a.get_attribute("innerHTML").strip()
            publish_info.append("作者: " + a_text)
            # 抽取发布日期
            entry_date = entry_meta.find_element_by_tag_name("time")
            entry_date_text = entry_date.get_attribute('innerHTML').strip()
            publish_info.append("发布日期: " + entry_date_text)
        except:
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        publish_date = today(fmt="%Y%m%d")
        #<header class="entry-header">
        #    <div class="entry-meta">
        #        <h5 class="entry-date">
        #             <time class="entry-date">2019年04月17日 </time>
        entry_header = self._driver.find_element_by_class_name("entry-header")
        entry_meta = entry_header.find_element_by_class_name("entry-meta")
        try:
            entry_date = entry_meta.find_element_by_tag_name("time")
            entry_date_text = entry_date.get_attribute('innerHTML').strip()
            # 发布日期转换
            publish_date = text2date(entry_date_text, fmt="%Y%m%d")
        except:
            pass
        return publish_date

    def _get_content(self):
        #<div id="page">
        #    <div id="content" class="site-content">
        #        <div id="primary" class="col-md-9 content-area">
        #            <article class="post-content ">
        #                <div class="entry-content">
        page = self._driver.find_element_by_id("page")
        content = page.find_element_by_id("content")
        content_area = content.find_element_by_id("primary")
        post_content = content_area.find_element_by_class_name("post-content")
        entry_content = post_content.find_element_by_class_name("entry-content")
        return entry_content

    def _gen_markdown(self):
        content = self._get_content()
        html_text = content.get_attribute('innerHTML')
        md_text = html2markdown(html_text, ext="pretty")
        return md_text

