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
    "WBPaper",
]


class WBPaper(Paper):
    _website   = "weibo.com"
    _paperpath = "/ttarticle/p"
    _sitename  = "新浪微博"

    def _get_title(self):
        """ 抽取文章标题
        """
        return self._driver.title

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        publish_info = []
        #<div class="WB_miniblog">
        #   <div class="WB_main">
        #       <div class="WB_artical">
        #           <div class="main_editor">
        #               <div class="authorinfo">
        #                   <span class="W_autocut">
        #                       <em class="W_autocut">...</em>
        #                   <span class="time">...</span>
        wb_miniblog = self._driver.find_element_by_class_name("WB_miniblog")
        wb_main = wb_miniblog.find_element_by_class_name("WB_main")
        wb_artical = wb_main.find_element_by_class_name("WB_artical")
        main_editor = wb_artical.find_element_by_class_name("main_editor")
        authorinfo = main_editor.find_element_by_class_name("authorinfo")
        try:
            w_autocut = authorinfo.find_element_by_class_name("W_autocut")
            w_autocut = w_autocut.find_element_by_class_name("W_autocut")
            w_autocut_text = w_autocut.get_attribute('innerHTML').strip()
            publish_info.append("作者: " + w_autocut_text)
        except:
            pass
        try:
            time = authorinfo.find_element_by_class_name("time")
            time_text = time.get_attribute('innerHTML').strip()
            time_text = time_text.split(" ")[1]  # 原文格式："发布于 2019-05-03 08:48:09"
            publish_info.append("发布日期: " + time_text)
        except:
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        publish_date = today(fmt="%Y%m%d")
        #<div class="WB_miniblog">
        #   <div class="WB_main">
        #       <div class="WB_artical">
        #           <div class="main_editor">
        #               <div class="authorinfo">
        #                   <span class="time">...</span>
        wb_miniblog = self._driver.find_element_by_class_name("WB_miniblog")
        wb_main = wb_miniblog.find_element_by_class_name("WB_main")
        wb_artical = wb_main.find_element_by_class_name("WB_artical")
        main_editor = wb_artical.find_element_by_class_name("main_editor")
        authorinfo = main_editor.find_element_by_class_name("authorinfo")
        time = authorinfo.find_element_by_class_name("time")
        time_text = time.get_attribute('innerHTML').strip()
        time_text = time_text.split(" ")[1]  # 原文格式："发布于 2019-05-03 08:48:09"
        # 发布日期转换
        publish_date = text2date(time_text, fmt="%Y%m%d")
        return publish_date

    def _get_content(self):
        #<div class="WB_miniblog">
        #   <div class="WB_main">
        #       <div class="WB_artical">
        #           <div class="main_editor">
        #               <div class="WB_editor_iframe_new">
        wb_miniblog = self._driver.find_element_by_class_name("WB_miniblog")
        wb_main = wb_miniblog.find_element_by_class_name("WB_main")
        wb_artical = wb_main.find_element_by_class_name("WB_artical")
        main_editor = wb_artical.find_element_by_class_name("main_editor")
        wb_editor_iframe_new = main_editor.find_element_by_class_name("WB_editor_iframe_new")
        return wb_editor_iframe_new

    def _gen_markdown(self):
        #<div class="WB_miniblog">
        #   <div class="WB_main">
        #       <div class="WB_artical">
        #           <div class="main_toppic">
        #           <div class="main_editor">
        #               <div class="WB_editor_iframe_new">
        wb_miniblog = self._driver.find_element_by_class_name("WB_miniblog")
        wb_main = wb_miniblog.find_element_by_class_name("WB_main")
        wb_artical = wb_main.find_element_by_class_name("WB_artical")
        # patch: 包含封面图
        main_toppic = wb_artical.find_element_by_class_name("main_toppic")
        main_toppic_text = main_toppic.get_attribute('innerHTML')
        main_editor = wb_artical.find_element_by_class_name("main_editor")
        wb_editor_iframe_new = main_editor.find_element_by_class_name("WB_editor_iframe_new")
        wb_editor_iframe_new_text = wb_editor_iframe_new.get_attribute('innerHTML')
        html_text = main_toppic_text + wb_editor_iframe_new_text
        md_text = html2markdown(html_text, ext="pretty")
        return md_text

