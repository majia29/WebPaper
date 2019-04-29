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
import string
import traceback
from urlparse import urlsplit

import requests
from PIL import Image

__all__ = [ 
    "load_paper",
    "Paper",
]


class Paper():
    """ 一个空的网络文章类，作为各个具体网站文章的抽象根类
    主要用于加载时，根据具体页面，抽取相关内容。
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def open(self):
        pass

    def save(self, options=None):
        default_options = {
            "format"       : "markdown",
            "include_index": "true",
            "include_image": "true",
            "image_format" : "png",
            "doc_name_format"  : "${yymm}-${title_full}",
            "image_name_format": "${yymm}-${title_abbr}-${image_sn}",
            "root_dir"     : ".",        # web根目录
            "doc_path"     : "",         # doc目录的Web相对路径
            "image_path"   : "images",   # image目录的Web相对路径
        }
        options = options or {}
        options = dict(default_options, **options)
        if options["format"]=="markdown":
            self._save_as_md(options)

    @abc.abstractproperty
    def close(self):
        pass

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
            # ref: https://github.com/python-pillow/Pillow/pull/1151 @mjpieters
            chrome_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
            headers = {"user-agent": chrome_agent}
            resp = requests.get(image_url, headers=headers, stream=True)
            resp.raw.decode_content = True
            try:
                im = Image.open(resp.raw)
            except Exception as exc:
                if not resp.ok:
                    resp.raise_for_status()
                traceback.print_exc()
                im = None
            # 下载成功，进一步处理
            if im:
                image_name_info["image_sn"] = image_sn
                image_name  = image_name_formater(image_name_info)
                image_format = im.format.lower()
                image_file = os.path.join(image_dir, "{}.{}".format(image_name, image_format))
                im.save(image_file)
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
        index_line = "+ [{}]({})".format(self.title, doc_name)
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
    #解析url参数，获取网站地址
    url = kwargs.get("url", argv[0] if argv else None)
    if url:
        if url.find("://")==-1:
            url = "http://{}".format(url)
        urls = urlsplit(url)
        # patch
        paperlib = urls.netloc.replace(".","_")  # 网站地址即为文章类库名（点字符转下划线）
    else:
        raise RuntimeError("missing url")
    # 动态加载
    module = __import__(paperlib)
    for member in inspect.getmembers(module):
        # 判断该成员是否为一个网站文章类，排除游戏抽象根类
        instance = member[1]
        if issubclass(instance, Paper) and not inspect.isabstract(instance):
            # 带参数实例化
            return instance(*argv, **kwargs)
    raise RuntimeError("paper class #{} is not found.".format(paperlib))

