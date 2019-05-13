# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
    )

import os
import sys
import zipfile

__all__ = [
    "Pinyin",
]

class Pinyin:
    _dict = None

    def __init__(self, datfile=None):
        """ 类初始化
        如果拼音字典未加载，则加载之
        """
        datfile = datfile or "pinyin.dat"
        if Pinyin._dict is None:
            Pinyin._load_dict(datfile)

    @staticmethod
    def _load_dict(datfile):
        """ 加载拼音字典
        支持zip压缩的字典文件
        """
        # 检查文件存在
        if not os.path.isfile(datfile):
            raise RuntimeError("missing pinyin file. {}".format(datfile))
        Pinyin._dict = {}
        zf, f = None, None
        try:
            # 检查是否zip文件
            if zipfile.is_zipfile(datfile):
                zf = zipfile.ZipFile(datfile, "r")
                if datfile not in zf.namelist():
                    datfile = zf.namelist()[0]
                f = zf.open(datfile, "r")
            else:
                f = open(datfile, "rb")
            # 循环读取加载字典
            for line in f:
                k, v = line.strip().split(":",1)
                knum = int("0x{}".format(k), 0)  # 16进制转为整数
                Pinyin._dict[knum] = v.split(":")[0][:-1]
        finally:
            if f:
                f.close()
            if zf:
                zf.close()

    @staticmethod
    def _pinyin_generator(s, initial=False):
        """ 拼音串生成器
        传入为unicode字符串
        """
        # 预处理：全角转半角
        ustring = ""
        for uchar in s:
            ucode = ord(uchar)
            if ucode==12288:  # 全角空格转换
                ucode = 32
            elif ucode>=65281 and ucode<=65374:  # 全角符号转换
                ucode -= 65248
            ustring += unichr(ucode)
        # 中文转拼音处理
        ascii_str, hz_pinyin = u"", u""
        for uchar in ustring:
            if uchar.isalnum():  # 有效字符
                # ASCII字符处理，简单拼接即可
                if ord(uchar)<255:
                    ascii_str += uchar.lower()
                    continue
                # 非ASCII字符处理
                hz_pinyin = Pinyin._dict.get(ord(uchar), u"")
            if ascii_str==u"" and hz_pinyin==u"":
                continue
            if ascii_str!=u"":
                yield ascii_str
                ascii_str = u""
            if hz_pinyin!=u"":
                yield hz_pinyin[0] if initial else hz_pinyin
                hz_pinyin = u""

    @staticmethod
    def pinyin(s, delimiter=None, initial=None):
        """ 拼音
        """
        delimiter = delimiter or ("" if initial else "_")
        initial   = initial or False
        if not isinstance(s, unicode):
            s = unicode(s, "utf-8")
        return delimiter.join(Pinyin._pinyin_generator(s, initial=initial))


def _main(*argv, **kwargs):
    """
    _main()

    :return: exit code
    """
    # 解析命令行参数
    args = list(*argv)[1:]
    if len(args)!=1:
        print("usage: python pinyin.py <text>")
        print("this is a sample.")
        text = "Arxiv 20２３年 自动 驾驶 & AI 报 告..."
    else:
        text = args[0]

    pinyin = Pinyin()
    print("[source] {}".format(text))
    print("[pinyin] {}".format(pinyin.pinyin(text)))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))

