# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from paper import Paper
from util import *

__all__ = [
    "MPPaper",
]


class MPPaper(Paper):
    _website   = "mp.weixin.qq.com"
    _paperpath = "/s"
    _sitename  = "微信公众号"

    def _get_title(self):
        """ 抽取文章标题
        微信公众号文章的html title恶心的只有发布者名字，不提供正文title，故需要做文章标题抽取
        """
        title = self._driver.title
        try:
            #<div id="page-content" class="rich_media_area_primary">
            #   <h2 class="rich_media_title" id="activity-name">
            page_content = self._driver.find_element_by_id("page-content")
            rich_media_title = page_content.find_element_by_class_name("rich_media_title")
            title = rich_media_title.get_attribute('innerHTML').strip()
        except:
            traceback.print_exc()
            pass
        return title

    def _get_publish_info(self):
        """ 抽取文章发布信息
        微信提供的发布日期根据阅读时间，显示为昨天，前天，几天前，几周前等，不提供具体的日期，故需要做日期格式转换
        """
        publish_info = []
        try:
            #<div id="page-content" class="rich_media_area_primary">
            #   <div id="meta_content" class="rich_media_meta_list">
            #       <span class="rich_media_meta rich_media_meta_text">
            #       <span class="rich_media_meta rich_media_meta_nickname" id="profileBt">
            #       <em id="publish_time" class="rich_media_meta rich_media_meta_text">
            page_content = self._driver.find_element_by_id("page-content")
            meta_content = page_content.find_element_by_id("meta_content")
            rich_media_meta_elements = meta_content.find_elements_by_class_name("rich_media_meta")
            for rich_media_meta in rich_media_meta_elements:
                # 获取元素id
                element_id = rich_media_meta.get_attribute("id")
                if element_id=="profileBt":
                    js_name = rich_media_meta.find_element_by_id("js_name")
                    js_name_text = js_name.get_attribute('innerHTML').strip()
                    publish_info.append("作者: " + js_name_text)
                elif element_id=="publish_time":
                    rich_media_meta_text = rich_media_meta.get_attribute('innerHTML').strip()
                    rich_media_meta_text = text2date(rich_media_meta_text, fmt="%Y-%m-%d")
                    publish_info.append("发布日期: " + rich_media_meta_text)
                else:
                    rich_media_meta_text = rich_media_meta.get_attribute('innerHTML').strip()
                    publish_info.append(rich_media_meta_text)
        except:
            traceback.print_exc()
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取微信公众号文章发布日期
        微信提供的发布日期根据阅读时间，显示为昨天，前天，几天前，几周前等，不提供具体的日期，故需要做日期格式转换
        """
        publish_date = today(fmt="%Y%m%d")
        try:
            #<div id="page-content" class="rich_media_area_primary">
            #   <em id="publish_time" class="rich_media_meta rich_media_meta_text">
            page_content = self._driver.find_element_by_id("page-content")
            publish_time = page_content.find_element_by_id("publish_time")
            publish_time_text = publish_time.get_attribute('innerHTML').strip()
            # 发布日期转换
            publish_date = text2date(publish_time_text, fmt="%Y%m%d")
        except:
            traceback.print_exc()
            pass
        return publish_date

    def _gen_markdown(self):
        md_text = ""
        #<div id="page-content" class="rich_media_area_primary">
        #   <div class="rich_media_content " id="js_content">
        page_content = self._driver.find_element_by_id("page-content")
        rich_media_content = page_content.find_element_by_class_name("rich_media_content")
        rich_media_content_text = rich_media_content.get_attribute('innerHTML').strip()
        html_text = rich_media_content_text
        md_text = html2markdown(html_text, ext="pretty")
        return md_text

