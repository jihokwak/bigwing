from bs4 import BeautifulSoup
import warnings; warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from IPython.display import clear_output
import re, os

class BigwingCrawler():

    def __init__(self, url, browser='PhantomJS'):

        self.url = url
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

    def set_browser(self, url, browser="PhantomJS"):

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
        if browser == "PhantomJS":
            browser_file = browser_dir + "/PhantomJS.exe"
            self.browser = webdriver.PhantomJS(browser_file)
        else:
            browser_file = browser_dir + "/chromedriver.exe"
            self.browser = webdriver.Chrome(browser_file)
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

    def __del__(self) :

        self.browser.Quit()

#교보문고 국내도서 결과 크롤러
class KyoboCrawler(BigwingCrawler):

    def __init__(self, browser='PhantomJS'):

        self.url = "http://www.kyobobook.co.kr/search/SearchKorbookMain.jsp"
        super().__init__(self.url, browser)

    def fetch(self, keyword):

        self.browser.find_element_by_xpath("// *[@id='searchKeyword']").send_keys(keyword)
        self.browser.find_element_by_xpath("//*[@id='searchTop']/div[1]/div/input").click()
        self.reset_soup()
        result = {
            "카테고리":  self.browser.find_element_by_xpath("//*[@id='container']/div[8]/form/table/tbody/tr[1]/td[2]/div[2]/a/span").text.strip(),
            "도서명":  self.browser.find_element_by_xpath("//*[@id='container']/div[8]/form/table/tbody/tr[1]/td[2]/div[2]/a/strong").text.strip(),
            "상세": [x.strip() for x in  self.browser.find_element_by_xpath("//*[@id='container']/div[8]/form/table/tbody/tr[1]/td[2]/div[4]").text.split("|")],
            "가격":  self.browser.find_element_by_xpath("//*[@id='container']/div[8]/form/table/tbody/tr[1]/td[4]/div[2]/strong").text.strip()
         }
        self.browser.find_element_by_xpath("// *[@id='searchKeyword']").clear()
        return result

    def __del__(self) :

        self.browser.Quit()







