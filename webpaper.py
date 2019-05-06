#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import time
import traceback

from paper import load_paper

__all__ = [
]

reload(sys)
sys.setdefaultencoding("utf-8")


def main(*argv, **kwargs):
    """
    main()

    :return: exit code
    """
    # 解析命令行参数
    args = list(*argv)[1:]
    if len(args)!=1:
        print("usage: webpaper.py <url>")
        return -1

    url = args[0]

    # todo: 通过配置文件，或者`git config --local --list`获取git配置信息
    # 自动提交github
    git_conf = {
        "repository": "git@github.com:majia29/webdigg.git",
        "user.name" : "majia29",
        "user.email": "majia29@gmail.com",
        "local"     : "../webdigg",  # web页面存放地址
    }

    # 开始执行
    page = load_paper(url=url)
    save_opts = {
        "include_index": "true",
        "include_image": "true",
    }
    if git_conf.get("local"):
        save_opts["root_dir"] = git_conf.get("local")
    page.save(options=save_opts)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

