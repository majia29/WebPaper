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
    "ZHPaper",
]


class ZHPaper(Paper):
    _website   = "zhuanlan.zhihu.com"
    _paperpath = "/p"
    _sitename  = "知乎专栏"

    def _get_title(self):
        """ 抽取文章标题
        """
        title_text = self._driver.title
        #<div class="App">
        #    <div class="Post-content"
        #        <header class="Post-Header">
        #            <h1 class="Post-Title">在线学习（Online Learning）导读</h1>
        try:
            app = self._driver.find_element_by_class_name("App")
            post_content = app.find_element_by_class_name("Post-content")
            post_header = app.find_element_by_class_name("Post-Header")
            post_title = app.find_element_by_class_name("Post-Title")
            title_text = post_title.get_attribute('innerHTML').strip()
        except:
            pass
        return title_text

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        publish_info = []
        #<div class="App">
        #    <div class="Post-content"
        #        <header class="Post-Header">
        #            <div class="Post-Author"
        #                <div class="AuthorInfo"
        #                    <div class="AuthorInfo-content">
        #                        <div class="AuthorInfo-head">
        #                            <span class="UserLink AuthorInfo-name">
        #                                <a class="UserLink-link" ...>XXX</a>
        #        <div class="ContentItem-time">发布于 2018-05-04</div>
        try:
            # 抽取作者
            app = self._driver.find_element_by_class_name("App")
            post_content = app.find_element_by_class_name("Post-content")
            post_header = post_content.find_element_by_class_name("Post-Header")
            authorinfo = post_header.find_element_by_class_name("AuthorInfo")
            authorinfo_content = authorinfo.find_element_by_class_name("AuthorInfo-content")
            authorinfo_head = authorinfo_content.find_element_by_class_name("AuthorInfo-head")
            authorinfo_name = authorinfo_head.find_element_by_class_name("AuthorInfo-name")
            userlink_link = authorinfo_name.find_element_by_class_name("UserLink-link")
            author_name_text = userlink_link.get_attribute("innerHTML").strip()
            publish_info.append("作者: " + author_name_text)
            # 抽取发布日期
            contentitem_time = post_content.find_element_by_class_name("ContentItem-time")
            time_text = contentitem_time.get_attribute("innerHTML").strip()
            article_date_text = time_text.split(" ")[1]
            publish_info.append("发布日期: " + article_date_text)
        except:
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        publish_date = today(fmt="%Y%m%d")
        #<div class="App">
        #    <div class="Post-content"
        #        <div class="ContentItem-time">发布于 2018-05-04</div>
        try:
            app = self._driver.find_element_by_class_name("App")
            post_content = app.find_element_by_class_name("Post-content")
            contentitem_time = post_content.find_element_by_class_name("ContentItem-time")
            time_text = contentitem_time.get_attribute("innerHTML").strip()
            article_date_text = time_text.split(" ")[1]
            # 发布日期转换
            publish_date = text2date(article_date_text, fmt="%Y%m%d")
        except:
            pass
        return publish_date

    def _get_content(self):
        #<div class="App">
        #    <div class="Post-content"
        #        <article class="Post-Main 
        #             <div class="Post-RichTextContainer">
        #                 <div class="RichText ztext Post-RichText">
        app = self._driver.find_element_by_class_name("App")
        post_content = app.find_element_by_class_name("Post-content")
        post_richtext = post_content.find_element_by_class_name("Post-RichText")
        return post_richtext

    def _gen_markdown(self):
        content = self._get_content()
        content_text = content.get_attribute('innerHTML')
        # todo: 包含封面图
        md_text = html2markdown(content_text, ext="pretty")
        # patch: 移走跳转 知乎对外链使用 https://link.zhihu.com/?target= 跳转
        md_text = markdown_remove_redirect(md_text, redirect_url="https://link.zhihu.com/?target=")
        return md_text

