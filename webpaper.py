#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    )

import sys

from paper import load_paper
from util import myconfig

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

    # 读取配置(目前只包括git)
    git_conf = myconfig("webpaper.conf", fileformat="ini")

    # 开始执行
    page = load_paper(url=url)
    save_opts = {
        "include_index": "true",
        "include_image": "true",
    }
    save_opts = dict(save_opts, **git_conf)
    page.save(options=save_opts)
    # 如果有git配置信息
    if git_conf.get("git.repository"):
        page.publish(git_conf)
    # 返回
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

