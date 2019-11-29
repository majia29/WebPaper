# -*- coding: utf-8 -*-
# util.py

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    )

import codecs
import os
import re
import shlex
import subprocess
import threading
import time
import traceback
from ConfigParser import ConfigParser
from datetime import datetime, timedelta
from urlparse import urlparse, parse_qs as urlparse_query

from html2text import HTML2Text
from selenium import webdriver as WebDriver

__all__ = [
    "today",
    "shellexec",
    "init_webdriver",
    "text2date",
    "html2markdown",
    "pretty_markdown",
    "convert_image",
    "markdown_remove_redirect",
]


def today(fmt=None):
    fmt = fmt or "%Y%m%d"
    return datetime.today().strftime(fmt)


def shellexec(cmd, shell=None, env=None, cwd=None, raiseonerror=None, timeout=None):
    """ Shell命令行执行
    关于超时，可参考
    https://stackoverflow.com/questions/1191374/using-module-subprocess-with-timeout @sussudio
    """
    # 缺省参数
    shell = False if shell is None else shell
    env   = env or os.environ
    cwd   = cwd or None
    raiseonerror = True if raiseonerror is None else raiseonerror
    timeout      = int(timeout or 0)
    # cmd转换为list
    if isinstance(cmd, (list,)):
        args = cmd
    else:
        args = shlex.split(cmd)
    shell_opts = {
        "args"  : args,
        "bufsize": 20971520,  # 20M
        "shell" : shell,
        "env"   : env,
        "cwd"   : cwd,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "preexec_fn": os.setpgrp,  # os.setpgrp/os.setsid
        "close_fds" : True,
    }
    proc = subprocess.Popen(**shell_opts)
    # 设定超时
    if timeout<=0:
        deadline = 0
    else:
        deadline = time.time() + timeout
    # 等待执行结束
    try:
        while proc.poll() is None:
            #print("exec...")
            if deadline>0 and time.time()>=deadline:
                #print("kill...")
                proc.kill()  # terminate()
            time.sleep(1)
    except KeyboardInterrupt as exc:  # ctrl+c
        traceback.print_exc()
        proc.kill()
        if raiseonerror:
            raise RuntimeError("Timeout Error.")      
    except:
        traceback.print_exc()
        if raiseonerror:
            raise
    # 执行结果
    outs, errs = proc.communicate()
    rets = proc.returncode
    if rets!=0 and raiseonerror:
        raise RuntimeError("[Shell Execute] Error #{}: {}".format(rets, errs))
    return rets, outs, errs if rets!=0 else None


def myconfig(configfile=None, fileformat=None, autocast=None):
    def _loadini(configfile, autocast=True):
        configfile, fileformat = configfile, "ini"
        autocast = True if autocast is None else autocast
        config = {}
        parser = ConfigParser()
        parser.list_values = False
        with codecs.open(configfile,"r","utf-8") as fp:
            parser.readfp(fp)
        for section in parser.sections():
            for itemkey, itemvalue in parser.items(section):
                confkey = "{}.{}".format(section.lower(), itemkey.lower())
                if autocast:
                    # 移走首尾引号
                    if len(itemvalue)>1 and itemvalue.startswith("\"") and itemvalue.endswith("\""):
                        itemvalue = itemvalue[1:-1]
                    elif len(itemvalue)>1 and itemvalue.startswith("'") and itemvalue.endswith("'"):
                        itemvalue = itemvalue[1:-1]
                    # 转换bool类型
                    if itemvalue.lower()=="true":
                        itemvalue = True
                    elif itemvalue.lower()=="false":
                        itemvalue = False
                    # 转换null类型
                    elif itemvalue.lower()=="none":
                        itemvalue = None
                    elif itemvalue.lower()=="null":
                        itemvalue = None
                    # 转换数值
                    elif itemvalue.isdigit():
                        itemvalue = int(itemvalue)
                    elif itemvalue.isdecimal():
                        itemvalue = float(itemvalue)
                config[confkey] = itemvalue
        return config

    def _loadxml(configfile, autocast=True):
        return {}
   
    def _loadyaml(configfile, autocast=True):
        return {}

    autocast = True if autocast is None else autocast
    if configfile is None:
        return {}
    if fileformat is None:
        ext = os.path.splitext(configfile)[1].lower()
        if ext==".ini":
            self._fileformat ="ini"
        elif ext==".xml":
            self._fileformat ="xml"
        elif ext==".yaml":
            self._fileformat ="yaml"
        else:
            self._fileformat ="ini"
    elif fileformat in ["ini", "xml", "yaml"]:
        fileformat = fileformat
    else:  # todo: 自动探测配置文件格式
        raise RuntimeError("[myconfig] unsupported config file. {}".format(fileformat))
    # 加载配置文件
    if fileformat=="ini":
        return _loadini(configfile, autocast=autocast)


def init_webdriver(driverclass, driverpath=None):
    """ 初始化Selenium WebDriver
    """
    chrome_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
    safari_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15"
    firefox_agent= "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:60.0) Gecko/20100101 Firefox/60.0"
    service_log = "{}.log".format(driverclass.lower())
    if driverclass.lower()=="chrome":
        chrome_path = driverpath
        # chrome config
        chrome_options = WebDriver.chrome.options.Options()
        chrome_options.add_argument("--lang=zh_CN.UTF-8")
        chrome_options.add_argument("--user-agent={}".format(chrome_agent))
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("–-disable-geolocation")
        #chrome_options.add_argument('--allow-running-insecure-content')
        #chrome_options.add_argument('--disable-dev-shm-usage')
        #chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument('--disable-infobars')
        #chrome_options.add_argument('--disable-web-security')
        #chrome_options.add_argument('--no-referrers')
        #chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument("--start-maximized")
        #chrome_options.add_argument("--headless")
        # 以下参数用于配置站点允许运行Flash，仅适用老版本Chrome 69
        chrome_options.add_argument("--disable-features=EnableEphemeralFlashPermission")
        chrome_prefs = {
            # 0- Default 1- Allow 2- Block
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 1,
            "profile.managed_default_content_settings.plugins": 1,
        }
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        # webdriver instance
        if chrome_path:
            driver = WebDriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options, service_log_path=service_log)
        else:
            driver = WebDriver.Chrome(chrome_options=chrome_options, service_log_path=service_log)
    elif driverclass.lower()=="firefox":
        firefox_path = driverpath
        firefox_options = WebDriver.FirefoxOptions()
        firefox_options.set_preference("media.volume_scale", "0.0");
        firefox_options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "true")
        firefox_options.set_preference("plugin.state.flash", 2)
        if firefox_path:
            driver = WebDriver.Firefox(executable_path=firefox_path, firefox_options=firefox_options, service_log_path=service_log)
        else:
            driver = WebDriver.Firefox(firefox_options=firefox_options, service_log_path=service_log)
    else:
        raise RuntimeError("Unsupported DriverClass. {}".format(driverclass))
    #driver.implicitly_wait(3)
    return driver


def text2date(desctext, fmt=None):
    """ 将日期描述文本转换为具体日期
    支持格式：今天、昨天、前天、n分钟前、n小时前、n天前、n周前、
    yyyy年mm月dd日、yy年mm月dd日、mm月dd日、
    yyyy-mm-dd、yy-mm-dd、mm-dd、
    yyyy/mm/dd、yy/mm/dd、mm/dd、
    """
    fmt = fmt or "%Y%m%d"
    if desctext=="今天" or desctext=="Today":
        text = datetime.today().strftime(fmt)
    elif desctext=="昨天" or desctext=="Yesterday":
        text = (datetime.today() - timedelta(days=1)).strftime(fmt)
    elif desctext=="前天":
        text = (datetime.today() - timedelta(days=2)).strftime(fmt)
    elif desctext.endswith("分钟前"):
        text = datetime.today().strftime(fmt)
    elif desctext.endswith("小时前"):
        text = datetime.today().strftime(fmt)
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
        if y<100:
            y += 2000
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
        if y<100:
            y += 2000
        text = datetime(y, m, d).strftime(fmt)
    elif len(desctext.split("-"))==2:
        y = datetime.today().year
        m = int(desctext.split("-")[0])
        d = int(desctext.split("-")[1])
        text = datetime(y, m, d).strftime(fmt)
    elif len(desctext.split("/"))==3:
        y = int(desctext.split("/")[0])
        m = int(desctext.split("/")[1])
        d = int(desctext.split("/")[2])
        if y<100:
            y += 2000
        text = datetime(y, m, d).strftime(fmt)
    elif len(desctext.split("/"))==2:
        y = datetime.today().year
        m = int(desctext.split("/")[0])
        d = int(desctext.split("/")[1])
        text = datetime(y, m, d).strftime(fmt)
    else:
        text = desctext
    return text


def html2markdown(html, ext=None):
    """ 将html格式转markdown格式。使用html2text库。
    """
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
        text = pretty_markdown(text)
    return text


def pretty_markdown(mdtext):
    """ 将markdown文本格式美化
    美化处理以下内容：
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
    """ 转换图片格式。缺省转为JPEG格式。
    """
    fmt = (fmt or "jpeg").lower()
    src_fmt = img.format.lower()
    if fmt==src_fmt:
        return img
    elif fmt=="webp":
        return img.convert("RGBX")
    elif fmt in ["png", "jpg", "jpeg"]:
        return img.convert("RGB")
    return img


def markdown_remove_redirect(mdtext, redirect_url):
    """ 将markdown文本中的重定向链接移除
    """
    #抽取url，替换
    url_regext = re.compile(r".*?\[.*?\]\(([http\://|https\://].+?)\)", re.IGNORECASE|re.UNICODE|re.LOCALE|re.DOTALL)
    urls = url_regext.findall(mdtext)
    for url in urls:
        dest_url = _get_redirect_dest(url, redirect_url)
        if dest_url<>url:
            mdtext = mdtext.replace(url, dest_url)
    return mdtext

def _get_redirect_dest(url, redirect_url):
    """ 抽取重定向链接中的目的url
    """
    # 重定向链接元信息
    redir_info = urlparse(redirect_url)
    redir_scheme = redir_info.scheme
    redir_host   = redir_info.netloc
    redir_path   = redir_info.path
    redir_query  = urlparse_query(redir_info.query, keep_blank_values=True).keys()[0]
    # 抽取重定向链接中的目的url
    url_info = urlparse(url)
    url_scheme = url_info.scheme
    url_host   = url_info.netloc
    url_path   = url_info.path
    url_querys = urlparse_query(url_info.query, keep_blank_values=True)
    # 如果链接是重定向链接，抽取重定向链接中的目的url
    if redir_host==url_host and redir_path==url_path:
        if redir_query in url_querys:
            url = url_querys[redir_query][0]
    return url
