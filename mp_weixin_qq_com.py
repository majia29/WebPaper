# -*- coding: utf-8 -*-


from pinyin import Pinyin

__all__ = [
    "load_paper",
    "MpPaper",
]

reload(sys)
sys.setdefaultencoding("utf-8")


def _init_webdriver(driverclass, driverpath=None):
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
        raise BrowserError("Unsupported DriverClass. {}".format(driverclass))
    #driver.implicitly_wait(3)
    return driver


def _text2date(desctext, fmt=None):
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
    else:
        text = desctext
    return text


def _pretty_markdown(mdtext):
    """ 将markdown文本格式化
    """
    return mdtext


def load_paper(*args, **kwargs):
    """ 网络文章类实例化
    用于扩展支持多个网站文章
    """
    url = kwargs.get("url", args[0] if args else None)
    if url:
        if url.find("://")==-1:
            url = "http://{}".format(url)
        urls = urlsplit(url)
        if urls.netloc=="mp.weixin.qq.com":
            return MPPaper(*args, **kwargs)
        elif urls.netloc=="mp.weixin.qq.com":
            return MPPaper(*args, **kwargs)
        else:
            raise RuntimeError("unsupported site. {}".format(urls.netloc))
    else:
        raise RuntimeError("missing url")


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

