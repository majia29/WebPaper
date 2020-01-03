#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import platform
import re
import requests
import sys
import xml.etree.ElementTree as xmlet
import zipfile  
from io import BytesIO

__all__ = [
]

reload(sys)
sys.setdefaultencoding("utf-8")

def download(url, local=None, showbar=True, chunksize=65536):
    # 参数处理
    if local is None or local=="":
        local = os.path.basename(url)
    if local=="":
        local = "index.html"
    if chunksize is None:
        chunksize = 65536
    if chunksize<8192:
        chunksize = 8192
    # requests
    headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:68.0) Gecko/20100101 Firefox/68.0"}
    resp = requests.get(url=url, headers=headers, timeout=5, stream=True)
    if resp.status_code!=200:
        resp.raise_for_status()
    # simple progress bar
    if showbar:
        sys.stdout.write("downloading ...")
        sys.stdout.flush()
    with open(local, "wb") as f:
        for chunk in resp.iter_content(chunk_size=chunksize):
            f.write(chunk)
            if showbar:
                sys.stdout.write(".")
                sys.stdout.flush()
    if showbar:
        print("")
    return local

def extractZip(source, subfile, basedir=None):
    """
    抽取zip文件中的单个文件  
    """
    files = []
    if basedir is None:
        basedir = os.path.dirname(os.path.expanduser(source))
    else:
        basedir = os.path.abspath(os.path.expanduser(basedir))
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    with zipfile.ZipFile(source) as zobj:
        for item in zobj.namelist():
            if item==subfile:
                item_file = os.path.join(basedir, item)
                item_dir = os.path.dirname(item_file)
                if not os.path.exists(item_dir):
                    os.mkdir(item_dir)
                with open(item_file, "wb") as fp:
                    fp.write(zobj.read(item))
                files.append(item_file)
                break
    return files

def main(*argv, **kwargs):
    """
    main()

    :return: exit code
    """
    # todo: 解析命令行参数
    args = list(*argv)[1:]
    p_driver = "chrome"
    p_version = "latest"
    if len(args)==0:
        p_version = "latest"
    elif len(args)==1 and args[0].isdigit():
        p_version = args[0]
    else:
        print("usage: update_chrome.py [version]")
        print("sample: update_chrome.py 79")
        return -1
    print("update", p_driver, p_version)
    
    drivers_path = "drivers/"
    # 补充当前操作系统信息
    p_os = platform.system()  # Windows/Linux/Darwin
    if p_os=="Windows":
        p_os = "win"
    elif p_os=="Darwin":
        p_os = "mac"
    else:
        p_os = p_os.lower()
    p_bit, _ = platform.architecture()  # 64bit/32bit
    # patch: 移除bit
    if p_bit.endswith("bit"):
        p_bit = p_bit[:-3]
    p_platform = "%s%s" % (p_os,p_bit)
    print("platform:", p_platform)

    # 获取list xml
    index_url = "https://chromedriver.storage.googleapis.com/"
    headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:68.0) Gecko/20100101 Firefox/68.0"}
    resp = requests.get(url=index_url, headers=headers, timeout=5, stream=True)
    if resp.status_code!=200:
        print("resp status:", resp.status_code)
        resp.raise_for_status()
    print("resp header:", resp.headers)
    print("resp encode:", resp.encoding)
    # simple progress bar
    sys.stdout.write("receiving index ...")
    sys.stdout.flush()
    # 由于index页面不会太大，改为内存方式，不写磁盘文件
    with BytesIO() as mem:
        for chunk in resp.iter_content(chunk_size=64*1024):
            mem.write(chunk)
            sys.stdout.write(".")
            sys.stdout.flush()
        index_xml = mem.getvalue()
    print("")

    # 解析xml，抽取driver zip，并抽取latest_version
    files, latest_version = [], [0]
    xmlroot = xmlet.fromstring(index_xml) #xmlet.parse("index.dat").getroot()
    # patch: 移除xml tag namespace
    def _removeNamespace(tag):
        return re.sub(r'{.*?}', '', tag)
    for node in xmlroot:
        # 只处理Contents节点
        if _removeNamespace(node.tag)=="Contents":
            for item in node:
                # 只处理Key项
                if _removeNamespace(item.tag)=="Key":
                    # 只处理chromedriver*.zip
                    matchobj = re.match(r"(^.*)/chromedriver.*\.zip", item.text)
                    if matchobj:
                        # 抽取version
                        #version = [int(v) for v in item.text.split("/")[0].split(".")]
                        version = [int(v) for v in matchobj.groups()[0].split(".")]
                        if cmp(version, latest_version)==1:
                            latest_version = version
                        files.append((item.text, version))
    print("latest version:", latest_version)
    if p_version=="latest" or p_version=="" or p_version is None:
        p_version = latest_version[0]
    else:
        p_version = int(p_version)

    # 找出符合条件的文件
    files = filter(lambda item: item[0].find(p_driver)>=0, files)
    files = filter(lambda item: item[0].find(p_platform)>=0, files)
    files = filter(lambda item: item[1][0]==p_version, files)
    if len(files)==0:
        print("mismatch", p_driver, p_platform, p_version)
        return -1
    # 基于版本号，逆序排序，取最新的
    def _getversion(item):
        return item[1]
    files.sort(key=_getversion, reverse=True)
    driver_file, driver_version = files[0]

    # 下载文件
    download_url = "https://chromedriver.storage.googleapis.com/" + driver_file
    print("download url:", download_url)
    p_version = reduce(lambda x,y:"{}.{}".format(x,y), driver_version)   #driver_file.split("/")[0]
    download_file = "{}{}driver-{}-{}.zip".format(drivers_path, p_driver, p_version, p_platform)
    print("download file:", download_file)
    download(url=download_url, local=download_file)
    
    # 解压
    print("unzip ...")
    extractZip(download_file, "chromedriver")

    # 返回
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
