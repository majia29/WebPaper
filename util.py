# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from datetime import datetime, timedelta

from html2text import HTML2Text
from selenium import webdriver as WebDriver

__all__ = [
    "today",
    "init_webdriver",
    "text2date",
    "html2markdown",
    "convert_image",
]


def today(fmt=None):
    fmt = fmt or "%Y%m%d"
    return datetime.today().strftime(fmt)


def init_webdriver(driverclass, driverpath=None):
    """ 初始化Selenium WebDriver
    """
    chrome_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
    safari_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15"
    firefox_agent= "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:60.0) Gecko/20100101 Firefox/60.0"
    if driverclass.lower()=="chrome":
        chrome_path = driverpath
        # chrome config
        chrome_options = WebDriver.chrome.options.Options()
        chrome_options.add_argument("--lang=zh_CN.UTF-8")
        chrome_options.add_argument("--user-agent={}".format(chrome_agent))
        #chrome_options.add_argument('--allow-running-insecure-content')
        #chrome_options.add_argument('--disable-dev-shm-usage')
        #chrome_options.add_argument('--disable-extensions')
        #chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument('disable-infobars')
        #chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument("--mute-audio")
        #chrome_options.add_argument('--no-referrers')
        #chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument("--start-maximized")
        #chrome_options.add_argument("--headless")
        # 以下参数用于配置站点允许运行Flash，仅适用老版本Chrome 69
        chrome_options.add_argument("--disable-features=EnableEphemeralFlashPermission")
        chrome_prefs = {
            "profile.managed_default_content_settings.images": 1,
            "profile.managed_default_content_settings.plugins": 0,
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        # webdriver instance
        if chrome_path:
            driver = WebDriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        else:
            driver = WebDriver.Chrome(chrome_options=chrome_options)
    elif driverclass.lower()=="firefox":
        firefox_path = driverpath
        firefox_options = WebDriver.FirefoxOptions()
        firefox_options.set_preference("media.volume_scale", "0.0");
        firefox_options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "true")
        firefox_options.set_preference("plugin.state.flash", 2)
        if firefox_path:
            driver = WebDriver.Firefox(executable_path=firefox_path, firefox_options=firefox_options)
        else:
            driver = WebDriver.Firefox(firefox_options=firefox_options)
    else:
        raise RuntimeError("Unsupported DriverClass. {}".format(driverclass))
    #driver.implicitly_wait(3)
    return driver


def text2date(desctext, fmt=None):
    """ 将日期描述文本转换为具体日期
    """
    fmt = fmt or "%Y%m%d"
    if desctext=="今天":
        text = datetime.today().strftime(fmt)
    elif desctext=="昨天":
        text = (datetime.today() - timedelta(days=1)).strftime(fmt)
    elif desctext=="前天":
        text = (datetime.today() - timedelta(days=2)).strftime(fmt)
    elif desctext.endswith("天前"):
        delta = int(desctext[ :desctext.index("天前") ])
        text = (datetime.today() - timedelta(days=delta)).strftime(fmt)
    elif desctext.endswith("周前"):
        delta = int(desctext[ :desctext.index("周前") ]) * 7
        text = (datetime.today() - timedelta(days=delta)).strftime(fmt)
    elif desctext.find("年")>0 and desctext.find("月")>0 and desctext.find("日")>0:
        y = int(desctext[ :desctext.index("年") ])
        m = int(desctext[ desctext.index("年")+1:desctext.index("月") ])
        d = int(desctext[ desctext.index("月")+1:desctext.index("日") ])
        text = datetime(y, m, d).strftime(fmt)
    elif desctext.find("月")>0 and desctext.find("日")>0:
        y = datetime.today().year
        m = int(desctext[ :desctext.index("月") ])
        d = int(desctext[ desctext.index("月")+1:desctext.index("日") ])
        text = datetime(y, m, d).strftime(fmt)
    elif len(desctext.split("-"))==3:
        y = int(desctext.split("-")[0])
        m = int(desctext.split("-")[1])
        d = int(desctext.split("-")[2])
        text = datetime(y, m, d).strftime(fmt)
    elif len(desctext.split("/"))==3:
        y = int(desctext.split("/")[0])
        m = int(desctext.split("/")[1])
        d = int(desctext.split("/")[2])
        text = datetime(y, m, d).strftime(fmt)
    else:
        text = desctext
    return text


def html2markdown(html, ext=None):
    # 初始化
    # 更多参数见 https://github.com/Alir3z4/html2text/blob/master/html2text/cli.py
    ext = ext or ""
    ht = HTML2Text()
    ht.ignore_links = False
    ht.escape_all = True
    ht.reference_links = True
    ht.mark_code = True
    ht.default_image_alt = "image"
    ht.body_width = 0  # patch: 避免无谓的分行
    ht.escape_snob = True
    ht.bypass_tables = True
    ht.ignore_tables = True
    ht.single_line_break = False
    ht.skip_internal_links = True
    # 转换
    text = ht.handle(html)
    # 额外操作
    if ext=="pretty":
        text = _pretty_markdown(text)
    return text


def _pretty_markdown(mdtext):
    """ 将markdown文本格式标准化
    标准化处理以下内容：
    1. 多个空行合并为1个
    2. header行的最高级数限制为3级（文章标题为2级header）
    3. image格式规整
    4. [code] 转为```
    5. todo: 数值型列表转化为非列表形式（由于在数值型列表项之间插入其他内容，导致其后的列表项从1开始重新计数，列表项之间断裂）
    """
    text = []
    blank_line = False
    header_indent = ""
    image_regext = re.compile(r"(.*)\!\[.*\]\((.+)\)(.*)", re.IGNORECASE|re.UNICODE|re.LOCALE|re.DOTALL)
    for line in mdtext.split("\n"):
        line = line.strip()
        # 空行合并
        if line=="" and blank_line:
            continue
        elif line=="":
            text.append("")
            blank_line = True
            continue
        blank_line = False
        # 是否存在1,2级header行，存在则根据级数确定header缩进量
        if line.startswith("# "):
            header_indent = "##"
        elif line.startswith("## ") and header_indent=="":
            header_indent = "#"
        # 当前为header行，则进行header缩进
        if line.startswith("#"):
            line = header_indent + line
        ## image格式规整 bug???
        image_info = image_regext.match(line)
        if image_info:
            if image_info.groups()[0]!="":
                text.append(image_info.groups()[0])
            if image_info.groups()[1]!="":
                text.append("![image]({})".format(image_info.groups()[1]))
            if image_info.groups()[2]!="":
                text.append(image_info.groups()[2])
            continue
        line = line.replace("[code]","\n```").replace("[/code]","```")
        text.append(line)
    return "\n".join(text)


def convert_image(img, fmt=None):
    fmt = (fmt or "jpeg").lower()
    src_fmt = img.format.lower()
    if fmt==src_fmt:
        return img
    elif fmt=="webp":
        return img.convert("RGBX")
    elif fmt in ["png", "jpg", "jpeg"]:
        return img.convert("RGB")
    return img

