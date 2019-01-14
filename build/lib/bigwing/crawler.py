from bs4 import BeautifulSoup
import warnings; warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from IPython.display import clear_output
import re, os, time
import pandas as pd
from bigwing.db import BigwingMysqlDriver

class BigwingCrawler():

    def __init__(self, url, browser='Chrome', headless=True):

        self.url = url
        self.headless = headless
        self.set_soup(self.url, browser)
        print("사이트 브라우징이 성공했습니다.")

    def fetch(self, keyword):
        pass

    def insert(self, data, col):

        self.data = data
        self.col = col

    def run(self, limit=True):

        self._check("data")  # 데이터 삽입여부 확인
        data = self.data.copy()
        if (limit == True) & ("검색상태" in data.columns):
            data = data[data["검색상태"] != "OK"]
        data_size = len(data)
        succeed_cnt = 0
        for idx, keyword in enumerate(data[self.col]) :
            info = {}
            try:
                info = self.fetch(keyword)
            except:
                self.data.loc[self.data[self.col] == keyword, '검색상태'] = "NOT_FOUND"
            else:
                self.data.loc[self.data[self.col] == keyword, '검색상태'] = "OK"
                succeed_cnt += 1
                for col in info.keys() :
                    if info[col].__class__ == [].__class__ :
                        for i, detail_info in enumerate(info[col]):
                            self.data.loc[self.data[self.col] == keyword, '검색%s%d' % (col, i + 1)] = detail_info
                    else :
                        self.data.loc[self.data[self.col] == keyword, '검색%s' % col] = info[col]
            finally:
                print("{} / {} ... {}%".format(idx + 1, data_size, round((idx + 1) / data_size * 100), 1))
                print("{} --> {}".format(self.data.loc[idx, self.col], info))
                clear_output(wait=True)
        print("크롤링완료!")
        print("추가정상 크롤링건수 : ", succeed_cnt)
        self.summary()

    def takeout(self):

        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        return self.data

    def summary(self):

        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        print("- 처리 건수 : ", self.data.shape[0])
        print("- 성공 건수 : ", sum(self.data.검색상태 == "OK"))
        print("- 실패 건수 : ", sum(self.data.검색상태 != "OK"))
        print("- 성공율 : {}%".format(round(sum(self.data.검색상태 == "OK") / self.data.shape[0] * 100, 1)))

    def _check(self, attr) :

        try:
            getattr(self, attr)
        except AttributeError:
            raise RuntimeError("FAILED : {} 를 확인해주세요.".format(attr))

    def set_soup(self, url, browser="PhantomJS"):

        self.set_html(url, browser)
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def reset_soup(self):

        self.reset_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def get_soup(self):

        return self.soup

    def set_html(self, url, browser="PhantomJS"):

        try :
            self.set_browser(url, browser)
            self.html = self.browser.page_source
        except AttributeError as e:
            print("사이트 브라우징이 실패했습니다.")

    def reset_html(self) :

        self.html = self.browser.page_source

    def get_html(self):

        return self.html

    def set_browser(self, url, browser="Chrome"):

        option = Options()
        option.add_argument('headless')
        option.add_argument('window-size=1920x1080')
        option.add_argument("disable-gpu")
        # Headless숨기기1
        option.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        option.add_argument("lang=ko_KR")


        cur_dir = os.path.abspath(os.path.dirname(__file__))
        browser_dir = os.path.join(cur_dir, "browser")

        if browser == "Chrome":
            browser_file = browser_dir + "/chromedriver.exe"
            if self.headless == True :
                self.browser = webdriver.Chrome(browser_file, chrome_options=option)
            else :
                self.browser = webdriver.Chrome(browser_file)
            self.browser.get('about:blank')
            self.browser.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
            self.browser.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

        else:
            browser_file = browser_dir + "/PhantomJS.exe"
            self.browser = webdriver.PhantomJS(browser_file)

        self.browser.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        self.browser.implicitly_wait(3)
        self.browser.get(url)

    def get_browser(self):

        return self.browser

    def get_text(self):

        html = self.get_html()
        text = ""
        p = re.compile(r'(<.{1,5}/?>)(?P<content>[^<\n]+)(</.{1,5}>)', re.M)
        m = p.finditer(html)
        lines = [line.group("content").strip() for line in m]
        for line in lines :
            text = text + "\n" + line
        return text

    def get_alltags(self):
        alltags = self.soup.find_all(True)
        alltags = [tag.name for tag in alltags]
        alltags = list(set(alltags))
        return alltags

    def __del__(self) :
        print("사이트 브라우징이 종료되었습니다.")
        self.browser.close()

class EPLCrawler(BigwingCrawler):

    def __init__(self, url,  page_nm="all",  browser='Chrome', headless=True):
        import time
        self.url = url
        super().__init__(self.url, browser, headless)
        time.sleep(2)
        self.set_page(page_nm)

    def set_page(self, page_nm):

        if page_nm == 'all' :
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/div[2]").click()
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/ul/li[1]").click()

        elif page_nm == 'recently' :
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/div[2]").click()
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/ul/li[2]").click()

        else :
            return

    def fetch(self, parant_tag, child_tag=None):

        self.reset_soup()
        tags = self.soup.select(parant_tag)

        results = []
        for tag in tags :
            if child_tag != None :
                tag = tag.select(child_tag)
                tag = [data.text.strip() for data in tag]

            if tag == [] :
                continue
            results.append(tag)
        return results

    def page_skipper(self):

        self.reset_soup()
        attrs = self.get_all_attr()
        btns = self.get_next_page_btn(*attrs)
        btn = next(btns)
        btn_class_nm = btn.get_attribute_list('class')[-1]
        btn_elem = self.browser.find_element_by_class_name(btn_class_nm)
        #return btn_elem
        print('click!', btn_class_nm)
        self.browser.execute_script("arguments[0].click();", btn_elem)


    def get_next_page_btn(self, *attrs):

        self.reset_soup()
        next_page_btns = []
        for attr in attrs :
            result = self.soup.find_all(True, {attr: re.compile(r'[/w]*(next)[/w]*', re.I)})
            if result != [] :
                next_page_btns.extend(result)
        for next_page_btn in next_page_btns :
            yield next_page_btn

    def get_all_attr(self):

        tags = self.soup.find_all(True)
        attrs_list = [[attr for attr in tag.attrs.keys()] for tag in tags]
        attrs = []
        for attr in attrs_list:
            attrs.extend(attr)
        attrs = list(set(attrs))
        return attrs

    def run(self):

        cur_page = ""
        page_nm = 0
        tabs = self.fetch('tr', 'th')[0]
        self.data = pd.DataFrame(columns=list(tabs))
        self.prev_data = self.fetch('tr', 'td')

        while cur_page != self.html :

            page_nm += 1
            cur_data = self.fetch('tr', 'td')
            if (page_nm >= 2) and (self.prev_data == cur_data) : break;

            for row in cur_data:

                print(self.data.shape[0], row)
                self.data.loc[self.data.shape[0]] = row

            self.prev_data = cur_data

            print('{}번째 페이지 저장완료!'.format(page_nm))
            print('다음페이지로 넘어갑니다.')

            self.page_skipper()
            time.sleep(1)
            self.reset_soup()

    def takeout(self):

        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        return self.data