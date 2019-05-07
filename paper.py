# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
import codecs
import inspect
import os
import re
import requests
import string
import time
import traceback
from urlparse import urlsplit

from PIL import Image
from selenium.common.exceptions import TimeoutException as WebTimeoutException
from selenium.webdriver.common.by import By as WebBy
from selenium.webdriver.common.keys import Keys as WebKeys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as WebEC

from pinyin import Pinyin
from util import *

__all__ = [ 
    "load_paper",
    "Paper",
]


class Paper():
    """ 一个空的网络文章类，作为各个具体网站文章的根类
    具体各个网站文章内容的抽取，由各个具体文章类实现。
    """
    def __init__(self, url, driver=None):
        """ InfoQ文章类初始化
        """
        # 标准类变量
        self._class_name = self.__class__.__name__
        # 输入参数检查
        self._check_url(url, site=self._website, path=self._paperpath)
        # 创建内部对象
        self._driver = driver or init_webdriver("chrome", "drivers/chromedriver")
        self.open(url)

    def __enter__(self):
        return self._driver

    def __str__(self):
        cls_str = ""
        cls_str += "class: {}\n".format(self._class_name)
        cls_str += "title: {}\n".format(self.title)
        cls_str += "publish_info:\n"
        for line in self.publish_info:
            cls_str += "{}\n".format(line)
        cls_str += "publish_date: {}\n".format(self.publish_date)
        cls_str += "markdown:\n{}\n".format(self.markdown)
        return cls_str

    def __exit__(self, type, value, trace):
        if self._driver:
            self._driver.quit()

    @property
    def url(self):
        return self._driver.current_url

    @property
    def html_source(self):
        return self._driver.page_source

    def open(self, url):
        """ 读取文章，并生成文章对象属性
        """
        self._check_url(url, self._website, self._paperpath)
        self._driver.get(url)
        print("[paper] load page ...")
        # patch: 等待页面加载完成
        try:
            WebDriverWait(self._driver, 10).until(WebEC.presence_of_element_located((WebBy.TAG_NAME, "img")))
        except WebTimeoutException:
            traceback.print_exc()
            raise
        # patch: 处理图片lazy-loading
        print("[paper] load image ...")
        image_elements = self._driver.find_elements_by_tag_name("img")
        for image_element in image_elements:
            self._driver.execute_script('return arguments[0].scrollIntoView(true);', image_element)
            time.sleep(2)
        # 抽取文章信息
        print("[paper] extract info ...")
        pinyin = Pinyin()
        self.title = self._get_title()
        self.title_full = pinyin.pinyin(self.title)
        self.title_abbr = pinyin.pinyin(self.title, initial=True)
        self.publish_info = self._get_publish_info()
        self.publish_date = self._get_publish_date()
        self.markdown     = self._gen_markdown()

    def save(self, options=None):
        default_options = {
            "format"       : "markdown",  # 保存格式 markdown/html
            "include_index": "true",  # 是否更新索引文件
            "include_image": "true",  # 是否下载图像文件
            "image_format" : "jpeg",  # 将webp图像转换存储格式
            "doc_name_format"  : "${yymm}-${title_full}",
            "image_name_format": "${yymm}-${title_abbr}-${image_sn}",
            "root_dir"     : "./docs",   # web根目录
            "doc_path"     : "",         # doc目录的Web相对路径
            "image_path"   : "images",   # image目录的Web相对路径
        }
        options = options or {}
        options = dict(default_options, **options)
        print("[paper] save paper ...")
        if options["format"]=="markdown":
            self._save_as_md(options)

    def close(self):
        self.__exit__()

    @staticmethod
    def _check_url(url, site, path):
        """ 检查url是否特定网站文章url
        """
        # 如果url不带协议头://，则补上缺省协议http://
        site = site or ""
        path = path or "/"
        if url.find("://")==-1:
            url = "http://{}".format(url)
        urls = urlsplit(url)
        assert urls.netloc==site
        assert urls.path==path or os.path.dirname(urls.path)==path

    def _get_title(self):
        """ 抽取文章标题
        """
        pass

    def _get_publish_info(self):
        """ 抽取文章发布信息
        """
        pass

    def _get_publish_date(self):
        """ 抽取文章发布日期
        """
        pass

    def _gen_markdown(self):
        """ 抽取文章正文，并转为markdown
        """
        pass

    def _gen_summary(self):
        """ 生成文章摘要
        """
        return "-摘要功能未实现-"

    def _gen_tags(self):
        """ 生成文章标签列表
        """
        return ["-标签功能未实现-"]

    def _save_as_md(self, options):
        # 
        doc_dir = os.path.abspath(os.path.join(options["root_dir"], options["doc_path"]))  # doc目录在本地文件系统中的绝对路径
        doc_name_formater = lambda _: string.Template(options["doc_name_format"]).safe_substitute(_)
        doc_name_info = {
            # 发布日期相关变量
            "yymm"    : self.publish_date[2:6],
            "yyyymm"  : self.publish_date[0:6],
            "yymmdd"  : self.publish_date[2:8],
            "yyyymmdd": self.publish_date[0:8],
            # 标题相关变量
            "title"     : self.title,
            "title_full": self.title_full,
            "title_abbr": self.title_abbr,
        }
        doc_name  = doc_name_formater(doc_name_info)
        # 下载图片，并改写markdown image地址为本地
        if options["include_image"]=="true" or options["include_image"]==True:
            self._save_images(options)
        # 写文章文件
        doc_file = os.path.join(doc_dir, "{}.md".format(doc_name))
        with codecs.open(doc_file, "w", encoding="utf-8") as f:
            # 写文章标题
            f.write("## {}  \n\n".format(self.title))
            # 写文章发布信息
            for line in self.publish_info:
                if line=="":
                    continue
                f.write("> {}  \n".format(line))
            f.write("\n")
            # 写文章内容
            f.write(self.markdown)
        # 写索引文件
        if options["include_index"]=="true" or options["include_index"]==True:
            self._write_index(options)

    def _save_images(self, options):
        image_dir = os.path.abspath(os.path.join(options["root_dir"], options["image_path"]))  # image目录在本地文件系统中的绝对路径
        image_name_formater = lambda _: string.Template(options["image_name_format"]).safe_substitute(_)
        image_name_info = {
            # 发布日期相关变量
            "yymm"    : self.publish_date[2:6],
            "yyyymm"  : self.publish_date[0:6],
            "yymmdd"  : self.publish_date[2:8],
            "yyyymmdd": self.publish_date[0:8],
            # 标题相关变量
            "title_full": self.title_full,
            "title_abbr": self.title_abbr,
            # 图片序号变量
            "image_sn": 0,
        }
        # 抽取markdown中的image url信息
        image_regext = re.compile(r"\!\[.*?\]\((.+?)\)", re.IGNORECASE|re.UNICODE|re.LOCALE|re.DOTALL)
        image_urls = image_regext.findall(self.markdown)  # use .finditer(self.markdown)
        # 循环处理下载
        image_result, image_sn = {}, -1
        for image_url in image_urls:
            print("[debug] image_url:", image_url)  # use image_url = image_url.groups()[0]
            # 如果已经处理过，跳过
            if image_url in image_result:
                image_result[image_url]["refcnt"] += 1
                continue
            # 图片序号+1
            image_sn += 1
            image_result[image_url] = {
                "url"   : image_url,
                "path"  : None,
                "format": None,
                "refcnt": 1,
            }
            # 下载图片
            chrome_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
            # 404 Client Error, if headers include Host, Referer
            #headers = requests.utils.default_headers()
            #headers.update( { "Host": self._website, "Referer": self.url, "User-Agent": chrome_agent, } )
            headers = { "User-Agent": chrome_agent }
            try:
                resp = requests.get(image_url, headers=headers, stream=True)
            except:
                traceback.print_exc()
                continue
            # patch: https://github.com/python-pillow/Pillow/pull/1151 @mjpieters
            resp.raw.decode_content = True
            try:
                img = Image.open(resp.raw)
            except Exception as exc:
                if not resp.ok:
                    resp.raise_for_status()
                traceback.print_exc()
                continue
            # 下载成功，进一步处理
            if img:
                image_name_info["image_sn"] = image_sn
                image_name  = image_name_formater(image_name_info)
                image_format = img.format.lower()
                # 如果是webp格式，则进行格式转换
                if image_format=="webp":
                    image_format = options["image_format"]
                    img = convert_image(img, fmt=image_format)
                image_file = os.path.join(image_dir, "{}.{}".format(image_name, image_format))
                img.save(image_file, image_format)
                image_result[image_url]["path"] = os.path.join(options["image_path"], "{}.{}".format(image_name, image_format))
                image_result[image_url]["format"] = image_format
                # 替换原文中的web地址为本地站点相对地址
                self.markdown = self.markdown.replace(image_url, image_result[image_url]["path"])
        return image_result

    def _write_index(self, options):
        doc_dir = os.path.abspath(os.path.join(options["root_dir"], options["doc_path"]))  # doc目录在本地文件系统中的绝对路径
        doc_name_formater = lambda _: string.Template(options["doc_name_format"]).safe_substitute(_)
        doc_name_info = {
            # 发布日期相关变量
            "yymm"    : self.publish_date[2:6],
            "yyyymm"  : self.publish_date[0:6],
            "yymmdd"  : self.publish_date[2:8],
            "yyyymmdd": self.publish_date[0:8],
            # 标题相关变量
            "title"     : self.title,
            "title_full": self.title_full,
            "title_abbr": self.title_abbr,
        }
        doc_name  = doc_name_formater(doc_name_info)
        # 生成要处理的索引相关信息
        index_file = os.path.join(doc_dir, "index.md")
        index_section = "**[{}-{}]**".format(self.publish_date[0:4], self.publish_date[4:6])
        # fixed: github index.md show url(include table symbol) error
        index_line = "+ [{}]({}) <sub>[\[{}\]]({})</sub>".format(self.title.replace("|",""), doc_name, self._website, self.url)
        # 变量初始化
        content = []
        exists_index_section = False
        # 如果索引文件存在，则读取索引文件进行处理
        if os.path.exists(index_file):
            with codecs.open(index_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 空行直接跳过
                    if line=="":
                        continue
                    # 遇到重复的文章索引行，跳过
                    if line==index_line:
                        continue
                    # 段行
                    if line.startswith("**["):
                        if line>index_section:
                            content.append("\n"+line+"\n")
                        elif line==index_section:
                            content.append("\n"+index_section+"\n")
                            content.append(index_line)
                            exists_index_section = True
                        else:
                            if exists_index_section==False:
                                content.append("\n"+index_section+"\n")
                                content.append(index_line)
                                exists_index_section = True
                            content.append("\n"+line+"\n")
                    # 文章索引行
                    if line.startswith("+ ["):
                        content.append(line)
        # 如果在文件处理结束，还没有写入当前索引信息，则直接写入
        if exists_index_section==False:
            content.append("\n"+index_section+"\n")
            content.append(index_line)
        # 写入索引文件
        with codecs.open(index_file, "w", encoding="utf-8") as f:
            f.write("\n".join(content))


def load_paper(*argv, **kwargs):
    """ 动态加载游戏具体网站文章类库，并返回带参数的网站文章类实例
    """
    # 解析url参数
    url = kwargs.get("url", argv[0] if argv else None)
    # 将url转库名。网站地址即为文章类库名
    # 为了避免目录结构复杂，不做多级目录，将点字符转下划线
    if url:
        if url.find("://")==-1:
            url = "http://{}".format(url)
        urls = urlsplit(url)
        paperlib = urls.netloc.replace(".","_")
    else:
        raise RuntimeError("missing url")
    # 动态加载
    module = __import__(paperlib)
    for member in inspect.getmembers(module):
        # 判断该成员是否为一个网站文章类，排除根类
        instance_name, instance_class = member[0], member[1]
        if issubclass(instance_class, Paper) and instance_name!="Paper":
            # 带参数实例化
            return instance_class(*argv, **kwargs)
    raise RuntimeError("paper class #{} is not found.".format(paperlib))

