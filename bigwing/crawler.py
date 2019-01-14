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
        '''
        크롤러 클래스 생성자
        :param url:
        :param browser: 헤드리스 브라우저 지정 Chrome(Default) or PhantomJS
        :param headless: 헤드리스 모드 설정 True(Default) or False
        '''
        self.url = url
        self.headless = headless
        self.set_soup(self.url, browser)
        print("사이트 브라우징이 성공했습니다.")

    def fetch(self, keyword):
        '''
        추상화 함수 : 단일 레코드 크롤링 함수
        :param keyword: 검색어
        :return: 없음
        '''
        pass

    def insert(self, data, col):
        '''
        검색대상 데이터셋 입력함수
        :param data: 데이터셋 (타입 : 데이터프레임)
        :param col: 검색 키워드 Column 지정 (타입 : 문자열)
        :return: 없음
        '''
        self.data = data
        self.col = col

    def run(self, limit=True):
        '''
        검색데이터셋의 키워드들을 근거로 일괄 크롤링하는 함수
        :param limit: 검색이 기존에 성공한 데이터를 스킵할지 옵션지정 True(Defalut)는 스킵. False는 검색
        :return: 없음
        '''
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
        '''
        크롤링한 데이터셋을 리턴하는 함수
        :return: data (타입 : 데이터프레임)
        '''
        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        return self.data

    def summary(self):
        '''
        처리결과요약을 출력하는 함수
        :return: 없음
        '''
        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        print("- 처리 건수 : ", self.data.shape[0])
        print("- 성공 건수 : ", sum(self.data.검색상태 == "OK"))
        print("- 실패 건수 : ", sum(self.data.검색상태 != "OK"))
        print("- 성공율 : {}%".format(round(sum(self.data.검색상태 == "OK") / self.data.shape[0] * 100, 1)))

    def _check(self, attr) :
        '''
        클래스 속성이 존재하는지 검사하는 함수(클래스 내부사용)
        :param attr: 속성 변수
        :return: 없음
        '''
        try:
            getattr(self, attr)
        except AttributeError:
            raise RuntimeError("FAILED : {} 를 확인해주세요.".format(attr))

    def set_soup(self, url, browser="Chrome"):
        '''
        BeautifulSoup 객체를 생성하는 Setter 함수
        :param url: url 문자열 값 입력 받는 인수
        :param browser: 헤드리스 브라우저 지정(Default : Chrome) #PhantomJs 사용가능
        :return: 없음
        '''
        self.set_html(url, browser)
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def reset_soup(self):
        '''
        BeautifulSoup 객체를 현재 selenium broswer 객체를 기준으로 업데이트하는 함수
        :return: 없음
        '''
        self.reset_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def get_soup(self):
        '''
         BeautifulSoup 객체를 리턴하는 Getter 함수
        :return: BeautifulSoup 객체
        '''
        return self.soup

    def set_html(self, url, browser="Chrome"):
        '''
        문자열 타입 html 문서를 저장하는 Setter 함수
        :param url:
        :param browser:
        :return: 없음
        '''
        try :
            self.set_browser(url, browser)
            self.html = self.browser.page_source
        except AttributeError as e:
            print("사이트 브라우징이 실패했습니다.")

    def reset_html(self) :
        '''
        문자열타입 html 문서를 현재 selenium broswer 객체를 기준으로 업데이트하는 함수
        :return: 없음
        '''
        self.html = self.browser.page_source

    def get_html(self):
        '''
        문자열타입 html 문서를 리턴하는 Getter 함수
        :return: 문자열 타입 html 변수
        '''
        return self.html

    def set_browser(self, url, browser="Chrome"):
        '''
        selenium 패키지의 browser driver 모듈을 세팅하는 함수
        :param url: 문자열타입 url 주소를 입력받는 인수
        :param browser: 브라우저를 지정하는 인수 (Default : Chrome) # PhantomJS 도가능
        :return: 없음
        '''
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
        '''
        Selenium Browser Driver 객체를 리턴하는 Getter 함수
        :return: 문자열 타입 html 변수
        '''
        return self.browser

    def get_text(self):
        '''
        인스턴스의 html 변수의 텍스트 정보를 얻어오는 함수
        :return: 문자열 타입 text
        '''
        html = self.get_html()
        text = ""
        p = re.compile(r'(<.{1,5}/?>)(?P<content>[^<\n]+)(</.{1,5}>)', re.M)
        m = p.finditer(html)
        lines = [line.group("content").strip() for line in m]
        for line in lines :
            text = text + "\n" + line
        return text

    def get_alltags(self):
        '''
        인스턴스의 html 변수의 사용된 tag 문자열 리스트를 리턴하는 함수
        :return: 문자열들의 list 타입
        '''
        alltags = self.soup.find_all(True)
        alltags = [tag.name for tag in alltags]
        alltags = list(set(alltags))
        return alltags

    def __del__(self) :
        print("사이트 브라우징이 종료되었습니다.")
        self.browser.close()

class EPLCrawler(BigwingCrawler):

    def __init__(self, url,  page_nm="all",  browser='Chrome', headless=True):
        '''
        EPL사이트의 Stat 정보를 가져오는 크롤러 클래스 생성자
        :param url: 페이지 url 입력 인수
        :param page_nm: 전체(all) 또는 최근시즌(recently) 옵션 입력 인수 (Default : all)
        :param browser: 사용 브라우저 입력 인수 (Default : Chrome)
        :param headless: 헤드리스 모드 옵션 입력 인수 (Default : True)
        '''
        import time
        self.url = url
        super().__init__(self.url, browser, headless)
        time.sleep(2)
        self.set_page(page_nm)

    def set_page(self, page_nm):
        '''
        EPL사이트 동적자바스크립트 페이지의 특정 메뉴탭을 선택하여 크롤링대상 웹페이지를 세팅하는 함수
        :param page_nm: 전체(all) 또는 최근시즌(recently) 옵션 입력 인수 (Default : all)
        :return: 없음
        '''
        if page_nm == 'all' :
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/div[2]").click()
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/ul/li[1]").click()

        elif page_nm == 'recently' :
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/div[2]").click()
            self.browser.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/ul/li[2]").click()

        else :
            return

    def fetch(self, parant_tag, child_tag=None):
        '''
        웹페이지에서 검색대상 정보가 있는 태그를 설정하고 웹페이지 전체 데이터를 가져오는 함수
        :param parant_tag: 상위 태그 설정 인수
        :param child_tag: 하위 태그 설정 인수 (Default : None)
        :return: list타입의 list타입 변수
        '''
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
        '''
        다음페이지 버튼을 누르고 넘어가는 이벤트를 발생시키는 함수
        :return: 없음
        '''
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
        '''
        다음페이지 버튼을 검색하여 그 태그의 속성명을 반환하는 함수
        :param attrs: 속성명 지정(ex. class, div 등)
        :return: 문자열 제네레이터 변수
        '''
        self.reset_soup()
        next_page_btns = []
        for attr in attrs :
            result = self.soup.find_all(True, {attr: re.compile(r'[/w]*(next)[/w]*', re.I)})
            if result != [] :
                next_page_btns.extend(result)
        for next_page_btn in next_page_btns :
            yield next_page_btn

    def get_all_attr(self):
        '''
        인스턴스의 html변수가 담고 있는 문서의 속성명을 문자열 리스트로 반환하는 함수
        :return: 문자열 list 타입
        '''
        tags = self.soup.find_all(True)
        attrs_list = [[attr for attr in tag.attrs.keys()] for tag in tags]
        attrs = []
        for attr in attrs_list:
            attrs.extend(attr)
        attrs = list(set(attrs))
        return attrs

    def run(self):
        '''
        현재페이지 크롤링 및 다음페이지 스킵 액션을 마지막페이지까지 연속진행하는 함수
        :return: 없음
        '''
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
        '''
        크롤링된 data를 리턴하는 Getter함수
        :return: 데이터프레임 타입 변수
        '''
        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        return self.data