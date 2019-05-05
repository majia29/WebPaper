# WebPaper

将微信公众号/微博/infoq等文章转换为标准html页面。主要是因为微信公众号/微博/infoq等发布出来的文章地址很不人性，而且其中的图片有的使用webp，很多网页摘取工具不支持。我的目标:  

1. 传入一个微信公众号/微博/infoq等文章地址，输出一个符合通常的web logger页面命名规范的html页面，并将其中的图片格式转换为png/jpeg等常见格式。
2. 页面上传到github.io，直接做为一个internet web页面供正常的浏览查看以及网摘。

**v0.1更新内容**

完成:

* 网页文章html抽取转换markdown（由于微信公众号的html格式繁杂，目前先完成了比较简单的infoq文章抽取，后续再进行扩展）
* 网页文章下载后，同步维护索引页面
* 网页中的图片下载到本地，并转换页面img地址为本地（目前仅做了下载，还未做图片格式转换，重点是支持webp转jpg/png）

一点想法:

* 加入机器学习内容(自然语言处理相关)，做文章摘要，文章标签生成。

**使用方式**

如果只做页面爬取，附带图片下载，则只需要命令行执行`python`脚本即可:

``` sh
python webpaper.py https://www.infoq.cn/article/oZCcFAC7J4-01yFTG5r3
```

如果也想发布到github.io，则需要做以下简单步骤即可:

1. clone repo;
2. repo setting "GitHub Pages" enable, "Pages Source" select "docs";
3. run webpaper.py <url>
4. git commit/push

ok.
