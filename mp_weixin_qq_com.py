# -*- coding: utf-8 -*-


from pinyin import Pinyin

__all__ = [
    "MpPaper",
]

reload(sys)
sys.setdefaultencoding("utf-8")


class MPPaper:
    def __init__(self, url, driver=None):
        """ 微信公众号文章类初始化
        """
        # 标准类变量
        self._class_name = self.__class__.__name__
        # 输入参数处理
        self._checkurl(url)
        # 创建内部对象
        self._driver = driver or _init_webdriver("chrome", "drivers/chromedriver")
        self.open(url)

    def __enter__(self):
        return self._driver

    def __exit__(self, type, value, trace):
        if self._driver:
            self._driver.quit()

    @property
    def url(self):
        return self._driver.current_url

    @property
    def html_source(self):
        return self._driver.page_source

    @staticmethod
    def _checkurl(url):
        """ 检查url是否是微信公众号文章url
        """
        # 如果url不带协议头://，则补上缺省协议http://
        if url.find("://")==-1:
            url = "http://{}".format(url)
        urls = urlsplit(url)
        assert urls.netloc=="mp.weixin.qq.com"        

    def _get_title(self):
        """ 抽取微信公众号文章标题
        微信公众号文章的html title恶心的只有发布者名字，不提供正文title，故需要做文章标题抽取
        """
        title = self._driver.title
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <h2 class="rich_media_title" id="activity-name">
            rich_media_title = page_content.find_element_by_class_name("rich_media_title")
            title = rich_media_title.get_attribute('innerHTML').strip()
        except:
            traceback.print_exc()
            pass
        return title

    def _get_publish_info(self):
        """ 抽取微信公众号文章发布信息
        微信提供的发布日期根据阅读时间，显示为昨天，前天，几天前，几周前等，不提供具体的日期，故需要做日期格式转换
        """
        publish_info = ""
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <div id="meta_content" class="rich_media_meta_list">
            meta_content = page_content.find_element_by_id("meta_content")
            # <span class="rich_media_meta rich_media_meta_text">
            # <span class="rich_media_meta rich_media_meta_nickname" id="profileBt">
            # <em id="publish_time" class="rich_media_meta rich_media_meta_text">
            rich_media_meta_elements = meta_content.find_elements_by_class_name("rich_media_meta")
            for rich_media_meta in rich_media_meta_elements:
                # 获取元素id
                element_id = rich_media_meta.get_attribute("id")
                if element_id=="profileBt":
                    js_name = rich_media_meta.find_element_by_id("js_name")
                    js_name_text = js_name.get_attribute('innerHTML').strip()
                    rich_media_meta_text = js_name_text
                elif element_id=="publish_time":
                    publish_time_text = rich_media_meta.get_attribute('innerHTML').strip()
                    rich_media_meta_text = _text2date(publish_time_text, fmt="%Y-%m-%d")
                else:
                    rich_media_meta_text = rich_media_meta.get_attribute('innerHTML').strip()
                publish_info += rich_media_meta_text + " "
        except:
            traceback.print_exc()
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取微信公众号文章发布日期
        微信提供的发布日期根据阅读时间，显示为昨天，前天，几天前，几周前等，不提供具体的日期，故需要做日期格式转换
        """
        publish_date = datetime.today().strftime("%Y%m%d")
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <em id="publish_time" class="rich_media_meta rich_media_meta_text">
            publish_time = page_content.find_element_by_id("publish_time")
            publish_time_text = publish_time.get_attribute('innerHTML').strip()
            # 发布日期转换
            publish_date = _text2date(publish_time_text, fmt="%Y%m%d")
        except:
            traceback.print_exc()
            pass
        return publish_date

    def _gen_markdown(self):
        md_text = ""
        # init html2text
        ht = HTML2Text()
        ht.bypass_tables = True
        ht.escape_all = True
        ht.ignore_links = False
        ht.mark_code = True
        ht.reference_links = True
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <div class="rich_media_content " id="js_content">
            rich_media_content = page_content.find_element_by_class_name("rich_media_content")
            rich_media_content_text = ht.handle(rich_media_content.get_attribute('innerHTML'))
            md_text = pretty_markdown(rich_media_content_text)
        except:
            traceback.print_exc()
            pass
        return md_text

    def _gen_tags(self):
        pass

    def open(self, url):
        self._checkurl(url)
        self._driver.get(url)
        pinyin = Pinyin()
        self.title = self._get_title()
        self.title_full = pinyin.pinyin(self.title)
        self.title_abbr = pinyin.pinyin(self.title, initial=True)
        self.publish_info = self._get_publish_info()
        self.publish_date = self._get_publish_date()
        self.markdown     = self._gen_markdown()

    def save(self, options=None):
        default_options = {
            "format"       : "markdown",
            "include_image": "true",
            "image_format" : "png",
            "doc_dir"      : ".",
            "image_dir"    : ".",
        }
        options = options or {}
        options = dict(default_options, **options)
        title = pinyin(self.title, format="strip", delimiter="_")
        print(options)



class InfoQPaper:
    def __init__(self, url, driver=None):
        """ 微信公众号文章类初始化
        """
        # 标准类变量
        self._class_name = self.__class__.__name__
        # 输入参数处理
        self._checkurl(url)
        # 创建内部对象
        self._driver = driver or _init_webdriver("chrome", "drivers/chromedriver")
        self.open(url)

    def __enter__(self):
        return self._driver

    def __exit__(self, type, value, trace):
        if self._driver:
            self._driver.quit()

    @property
    def url(self):
        return self._driver.current_url

    @property
    def html_source(self):
        return self._driver.page_source

    @staticmethod
    def _checkurl(url):
        """ 检查url是否是微信公众号文章url
        """
        # 如果url不带协议头://，则补上缺省协议http://
        if url.find("://")==-1:
            url = "http://{}".format(url)
        urls = urlsplit(url)
        assert urls.netloc=="mp.weixin.qq.com"        

    def _get_title(self):
        """ 抽取微信公众号文章标题
        微信公众号文章的html title恶心的只有发布者名字，不提供正文title，故需要做文章标题抽取
        """
        title = self._driver.title
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <h2 class="rich_media_title" id="activity-name">
            rich_media_title = page_content.find_element_by_class_name("rich_media_title")
            title = rich_media_title.get_attribute('innerHTML').strip()
        except:
            traceback.print_exc()
            pass
        return title

    def _get_publish_info(self):
        """ 抽取微信公众号文章发布信息
        微信提供的发布日期根据阅读时间，显示为昨天，前天，几天前，几周前等，不提供具体的日期，故需要做日期格式转换
        """
        publish_info = ""
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <div id="meta_content" class="rich_media_meta_list">
            meta_content = page_content.find_element_by_id("meta_content")
            # <span class="rich_media_meta rich_media_meta_text">
            # <span class="rich_media_meta rich_media_meta_nickname" id="profileBt">
            # <em id="publish_time" class="rich_media_meta rich_media_meta_text">
            rich_media_meta_elements = meta_content.find_elements_by_class_name("rich_media_meta")
            for rich_media_meta in rich_media_meta_elements:
                # 获取元素id
                element_id = rich_media_meta.get_attribute("id")
                if element_id=="profileBt":
                    js_name = rich_media_meta.find_element_by_id("js_name")
                    js_name_text = js_name.get_attribute('innerHTML').strip()
                    rich_media_meta_text = js_name_text
                elif element_id=="publish_time":
                    publish_time_text = rich_media_meta.get_attribute('innerHTML').strip()
                    rich_media_meta_text = _text2date(publish_time_text, fmt="%Y-%m-%d")
                else:
                    rich_media_meta_text = rich_media_meta.get_attribute('innerHTML').strip()
                publish_info += rich_media_meta_text + " "
        except:
            traceback.print_exc()
            pass
        return publish_info

    def _get_publish_date(self):
        """ 抽取微信公众号文章发布日期
        微信提供的发布日期根据阅读时间，显示为昨天，前天，几天前，几周前等，不提供具体的日期，故需要做日期格式转换
        """
        publish_date = datetime.today().strftime("%Y%m%d")
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <em id="publish_time" class="rich_media_meta rich_media_meta_text">
            publish_time = page_content.find_element_by_id("publish_time")
            publish_time_text = publish_time.get_attribute('innerHTML').strip()
            # 发布日期转换
            publish_date = _text2date(publish_time_text, fmt="%Y%m%d")
        except:
            traceback.print_exc()
            pass
        return publish_date

    def _gen_markdown(self):
        md_text = ""
        # init html2text
        ht = HTML2Text()
        ht.bypass_tables = True
        ht.escape_all = True
        ht.ignore_links = False
        ht.mark_code = True
        ht.reference_links = True
        try:
            # <div id="page-content" class="rich_media_area_primary">
            page_content = self._driver.find_element_by_id("page-content")
            # <div class="rich_media_content " id="js_content">
            rich_media_content = page_content.find_element_by_class_name("rich_media_content")
            rich_media_content_text = ht.handle(rich_media_content.get_attribute('innerHTML'))
            md_text = _pretty_markdown(rich_media_content_text)
        except:
            traceback.print_exc()
            pass
        return md_text

    def _gen_tags(self):
        pass

    def open(self, url):
        self._checkurl(url)
        self._driver.get(url)
        pinyin = Pinyin()
        self.title = self._get_title()
        self.title_full = pinyin.pinyin(self.title)
        self.title_abbr = pinyin.pinyin(self.title, initial=True)
        self.publish_info = self._get_publish_info()
        self.publish_date = self._get_publish_date()
        self.markdown     = self._gen_markdown()

    def save(self, options=None):
        default_options = {
            "format"       : "markdown",
            "include_image": "true",
            "image_format" : "png",
            "doc_dir"      : ".",
            "image_dir"    : ".",
        }
        options = options or {}
        options = dict(default_options, **options)
        title = pinyin(self.title, format="strip", delimiter="_")
        print(options)


def main(*argv, **kwargs):
    """
    main()

    :return: exit code
    """
    # 解析命令行参数
    args = list(*argv)[1:]
    if len(args)!=1:
        print("usage: mp2html.py <url>")
        return -1

    url = args[0]

    # todo: 通过配置文件，或者`git config --local --list`获取git配置信息
    git_conf = {
        "repository": "git@github.com:majia29/mp2html.git",
        "user.name" : "majia29",
        "user.email": "majia29@gmail.com",
        "local": ".",
    }

    # 开始执行
    page = load_paper(url=url)
    print("title:", page.title)
    print("title_full:", page.title_full)
    print("title_abbr:", page.title_abbr)
    print("publish_info:", page.publish_info)
    print("publish_date:", page.publish_date)
    #print("markdown:", page.markdown)
    save_opts = {
        "doc_dir"  : os.path.join(git_conf.get("local","."), "docs"),
        "image_dir": os.path.join(git_conf.get("local","."), "docs/images"),
    }
    time.sleep(3600)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

