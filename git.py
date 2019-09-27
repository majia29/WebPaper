# -*- coding: utf-8 -*-
# git.py

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    )

import getpass
import os
import socket
import subprocess
import sys
import time
import traceback

__all__ = [ 
    "GitRepo",
]


class GitRepo():
    """ git repo操作类
    """
    def __init__(self, repo_dir=None, executable_path=None):
        """ git repo类初始化
        """
        ENV_PATH_SEP = ":"
        # 标准类变量
        self._class_name = self.__class__.__name__
        # 输入参数检查
        self.repo_dir = os.path.abspath(repo_dir or ".")
        # 如果配置了有效的执行路径，则抽取git命令信息，并修改git执行时的环境变量
        self.env = os.environ
        if executable_path is None:
            self.git_dir = None
            self.git_bin = "git"
        elif os.path.exists(executable_path) and os.path.isfile(executable_path):
            self.git_dir = os.path.dirname (os.path.abspath(executable_path))  # git 命令所在目录
            self.git_bin = os.path.basename(os.path.abspath(executable_path))  # git 命令
            # 如果PATH环境变量中没有git命令所在目录，则修改之
            env_paths = self.env.get("PATH","").split(ENV_PATH_SEP)
            if self.git_dir not in env_paths:
                env_paths.append(self.git_dir)
                self.env["PATH"] = ENV_PATH_SEP.join(env_paths)
        else:
            raise RuntimeError("Invalid executable_path. {}".format(executable_path))
        # 检查git是否存在
        if not self._exists_git(self.git_bin, self.env):
            raise RuntimeError("Not found git.")
        # 创建内部对象
        self._conf = self._get_conf("")

executable_path
executable_path

    def __enter__(self):
        return self._driver

    def __str__(self):
        cls_str = ""
        cls_str += "class: {}\n".format(self._class_name)
        cls_str += "title: {}\n".format(self.title)
        cls_str += "publish_info:\n{}\n".format("\n".join(self.publish_info))
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

    def config(self):
        """ 读取repo config
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
        # 如果有git信息，则web根目录由git配置决定
        if options.get("git.local"):
            options["root_dir"] = options.get("git.local")
        # 下载图片，并改写markdown image地址为本地（所以要先做图片下载，再做文档保存）
        if options["include_image"]=="true" or options["include_image"]==True:
            image_files = self._save_images(options)
        if options["format"]=="markdown":
            doc_file = self._save_as_md(options)
        # 维护索引文件
        if options["include_index"]=="true" or options["include_index"]==True:
            index_file = self._write_index(options)
        # 操作git
        if self._check_git(options):
            self._git_publish(options)
        # 返回保存过程涉及的文件
        return dict( image_files.items() + doc_file.items() + index_file.items() )

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
        doc_format = "md"
        doc_path = options["doc_path"]  # doc目录在web root的相对地址
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
        # 写文章文件
        doc_file = os.path.join(doc_dir, "{}.{}".format(doc_name, doc_format))
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
        print("[debug] doc_file:", doc_file)
        doc_result = { doc_file : {"path": os.path.join(doc_path, "{}.{}".format(doc_name, doc_format)), } }
        return doc_result

    def _save_images(self, options):
        image_path = options["image_path"]  # image目录在web root的相对地址
        image_dir = os.path.abspath(os.path.join(options["root_dir"], image_path))  # image目录在本地文件系统中的绝对路径
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
                "path"  : None,
                "refcnt": 1,
            }
            # 下载图片
            chrome_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
            headers = requests.utils.default_headers()
            headers.update( { "User-Agent": chrome_agent, } )
            #headers = { "User-Agent": chrome_agent }
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
                image_result[image_url]["path"] = os.path.join(image_path, "{}.{}".format(image_name, image_format))
                # 替换原文中的web地址为本地站点相对地址
                self.markdown = self.markdown.replace(image_url, image_result[image_url]["path"])
        return image_result

    def _write_index(self, options):
        index_name, index_format = "index", "md"
        doc_path = options["doc_path"]  # doc目录在web root的相对地址
        doc_dir = os.path.abspath(os.path.join(options["root_dir"], doc_path))  # doc目录在本地文件系统中的绝对路径
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
        index_file = os.path.join(doc_dir, "{}.{}".format(index_name, index_format))
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
        index_result = { index_file : {"path": os.path.join(doc_path, "{}.{}".format(index_name, index_format)), } }
        return index_result

    def _check_git(self, options):
        # 检查git配置
        git_repository = options.get("git.repository") or ""
        if git_repository=="":
            return False  # 未配置git repo，不做git操作
        git_local = options.get("git.local") or ""
        if git_local=="":
            return False  # 未配置git local，不做git操作
        # 检查本地git repo是否与配置一致
        git_cwd = os.path.abspath(git_local)
        check_cmd = "git status"
        rets, outs, errs = _shell_exec(check_cmd, cwd=git_cwd, raiseonerror=False, timeout=120)
        #print("$>", check_cmd)
        #print(outs or "")
        #print(errs or "")
        return True if rets==0 else False

    def _git_publish(self, options):
        # 检查git配置
        git_repository = options.get("git.repository") or ""
        if git_repository=="":
            raise RuntimeError("git repository missing.")
        git_local = options.get("git.local") or ""
        if git_local=="":
            raise RuntimeError("git local missing.")
        # 
        git_cwd = os.path.abspath(git_local)
        # 先检查repo本地配置
        list_cmd = "git config --local --list"
        rets, outs, errs = _shell_exec(list_cmd, cwd=git_cwd, raiseonerror=False, timeout=120)
        print("$>", list_cmd)
        print(outs or "")
        print(errs or "")
        if rets!=0:
            return rets
        for line in outs.split("\n"):
            if line.strip()=="":
                continue
            key, value = line.split("=", 1)
            if key=="remote.origin.url":
                git_repository = options.get("git.repository") or ""
                # 如果没有配置git.repository信息，则不检查及处理git user.name
                if git_repository=="":
                    raise RuntimeError("ERROR: 没有配置git repo")
                if value==git_repository:
                    continue
                return -1002  # 配置的git repo与本地路径下的repo不一致
            if key=="user.name":
                git_user_name = options.get("git.user.name") or ""
                # 如果没有配置git.user.name信息，则不检查及处理git user.name
                if git_user_name=="":
                    continue
                if value==git_user_name:
                    continue
                set_cmd = "git config --local user.name \"{}\"".format(git_user_name)
                _shell_exec(set_cmd, cwd=git_cwd, raiseonerror=False, timeout=120)
            if key=="user.email":
                git_user_email = options.get("git.user.email") or ""
                # 如果没有配置git.user.name信息，则不检查及处理git user.name
                if git_user_email=="":
                    continue
                if value==git_user_email:
                    continue
                set_cmd = "git config --local user.email \"{}\"".format(git_user_email)
                _shell_exec(set_cmd, cwd=git_cwd, raiseonerror=False, timeout=120)
        # 本地repo提交
        commands = "git config --local --list; git status; git add .; git commit -m \"add paper\"; git push;"
        for cmd in commands.split(";"):
            if cmd.strip()=="":
                continue
            rets, outs, errs = _shell_exec(cmd, cwd=git_cwd, raiseonerror=False, timeout=120)
            print("$>", cmd)
            print(outs or "")
            print(errs or "")
            if rets!=0:
                break
        return rets


def _get_default_identity(env=None):
    """ 
    """
    env = env or os.environ
    # 取user
    user = env.get("USER") or ""
    if user=="":
        user = getpass.getuser()
    # 取email
    email = env.get("EMAIL") or ""
    if email=="":
        domain = socket.gethostname()
        email = "{}@{}".format(user, domain)
    return (user, email)

