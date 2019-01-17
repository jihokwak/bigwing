from bs4 import BeautifulSoup
import warnings; warnings.filterwarnings("ignore")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from IPython.display import clear_output
import re, os, time
import pandas as pd
import numpy as np
import threading

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
        self.browser = browser
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
            self.set_driver(url, browser)
            self.html = self.driver.page_source
        except AttributeError as e:
            print("사이트 브라우징이 실패했습니다.")

    def reset_html(self) :
        '''
        문자열타입 html 문서를 현재 selenium broswer 객체를 기준으로 업데이트하는 함수
        :return: 없음
        '''
        self.html = self.driver.page_source

    def get_html(self):
        '''
        문자열타입 html 문서를 리턴하는 Getter 함수
        :return: 문자열 타입 html 변수
        '''
        return self.html

    def set_driver(self, url, browser="Chrome"):
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
                self.driver = webdriver.Chrome(browser_file, chrome_options=option)
            else :
                self.driver = webdriver.Chrome(browser_file)
            self.driver.get('about:blank')
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
            self.driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

        else:
            browser_file = browser_dir + "/PhantomJS.exe"
            self.driver = webdriver.PhantomJS(browser_file)

        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        self.driver.implicitly_wait(3)
        self.driver.get(url)

    def get_driver(self):
        '''
        Selenium Browser Driver 객체를 리턴하는 Getter 함수
        :return: 문자열 타입 html 변수
        '''
        return self.driver

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
        self.driver.close()
        self.driver.quit()

class EPLCrawler(BigwingCrawler):

    def __init__(self, url='about:blank', page_range=None,  page_nm="all", page_type="Stat", browser='Chrome', headless=True, n_jobs=1):
        '''
        EPL사이트의 Stat 정보를 가져오는 크롤러 클래스 생성자
        :param url: 페이지 url 입력 인수
        :param page_nm: 전체(all) 또는 최근시즌(recently) 옵션 입력 인수 (Default : all)
        :param browser: 사용 브라우저 입력 인수 (Default : Chrome)
        :param headless: 헤드리스 모드 옵션 입력 인수 (Default : True)
        '''
        self.page_nm = page_nm
        self.page_type = page_type
        self.browser = browser
        self.data = None
        self.n_jobs = n_jobs
        self.partitions = self.partitioner(page_range[0], page_range[1], n_jobs) if page_range != None else {}
        self.error_pages = []
        super().__init__(url, browser, headless)
        if page_type=="Stat" :
            self.url = url
            self.set_stat_page(self.page_nm)

        elif page_type=="Results" :
            self.url = url
            pass

        elif page_type=="Lineup" :
            self.url = "https://www.premierleague.com/match/"
            self.first_match = page_range[0]
            self.last_match = page_range[1]
            self.set_lineup_page(self.first_match)

        elif page_type=="Matchs" :
            self.url = "https://www.premierleague.com/match/"
            self.first_match = page_range[0]
            self.last_match = page_range[1]
            self.set_matchstats_page(self.first_match)
        else :
            pass

        time.sleep(2)

    def partitioner(self, start, end, divide):

        partitions = {}
        partition_sp = np.linspace(start - 1, end, divide + 1).astype(int)
        for i in range(len(partition_sp) - 1):
            partitions[(partition_sp[i] + 1, partition_sp[i + 1])] = pd.DataFrame()
        return partitions

    def set_level_results_page(self, level):
        for i in range(10) :
            try :
                self.driver.get(self.url)
                if level == "First Team" :
                    pass

                elif level == "PL2" :

                    self.driver.find_element_by_xpath("//*[@id='mainContent']/header/div/div[1]/div/ul/li[2]").click()
                    self.driver.refresh()

                elif level == "U18" :
                    self.driver.find_element_by_xpath("//*[@id='mainContent']/header/div/div[1]/div/ul/li[3]").click()
                    self.driver.refresh()
                self.reset_soup()
                time.sleep(3)
                break;
            except:
                print("재시도합니다. 재시도횟수 {}번".format(i + 1))
                time.sleep(0.5)

                break;

    def set_league_results_page(self, league, level):
        '''
        EPL사이트 Results 동적자바스크립트페이지를 특정 메뉴탭을 선택하여 크롤링대상 웹페이지를 세팅하는 함수
        :param league: 경기리그 옵션 입력 인수
        :return: 없음
        '''
        level_idx = ["First Team", "PL2", "U18"].index(level) + 1
        league_list = self.__results_league_menu_scanner(level)
        league_idx = league_list.index(league) + 1
        print("league_index : ",league_idx)
        for i in range(10) :
            try :
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[1]/div[2]".format(level_idx)).click()
                time.sleep(0.5)
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[1]/ul/li[{}]".format(level_idx, league_idx)).click()
                self.reset_soup()
                time.sleep(2)
                break;
            except Exception as e:
                print(e)
                print("재시도합니다. 재시도횟수 {}번".format(i+1))
                time.sleep(0.5)

                continue;

    def set_season_results_page(self, season, level):
        '''
        EPL사이트 Results 동적자바스크립트페이지를 특정 메뉴탭을 선택하여 크롤링대상 웹페이지를 세팅하는 함수
        :param season: 경기시즌 옵션 입력 인수
        :return: 없음
        '''
        level_idx = ["First Team", "PL2", "U18"].index(level) + 1
        season_list = self.__results_season_menu_scanner(level)
        season_idx = season_list.index(season) + 1
        print("season_index : ", season_idx)
        for i in range(10) :
            try:
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[2]/div[2]".format(level_idx)).click()
                time.sleep(1)
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[2]/ul/li[{}]".format(level_idx,season_idx)).click()
                for i in range(30) :
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.1)

                self.driver.execute_script("window.scrollTo(0, 0);")
                self.reset_soup()
                time.sleep(2)
                break;
            except :
                print("재시도합니다. 재시도횟수 {}번".format(i+1))
                time.sleep(1)
                continue;

    def set_stat_page(self, page_nm):
        '''
        EPL사이트 동적자바스크립트 페이지의 특정 메뉴탭을 선택하여 크롤링대상 웹페이지를 세팅하는 함수
        :param page_nm: 전체(all) 또는 최근시즌(recently) 옵션 입력 인수 (Default : all)
        :return: 없음
        '''
        if page_nm == 'all' :
            self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/div[2]").click()
            self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/ul/li[1]").click()

        elif page_nm == 'recently' :
            self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/div[2]").click()
            self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div/div[2]/div[1]/section/div[1]/ul/li[2]").click()

        else :
            return
        self.reset_soup()

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
        btn_elem = self.driver.find_element_by_class_name(btn_class_nm)
        #return btn_elem
        print('click!', btn_class_nm)
        self.driver.execute_script("arguments[0].click();", btn_elem)

    def __results_season_menu_scanner(self, level):
        for i in range(10):
            try:
                level_idx = ["First Team", "PL2", "U18"].index(level)+1
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[2]/div[2]".format(level_idx)).click()
                time.sleep(0.5)
                ul = self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[2]/ul".format(level_idx))
                lis = ul.find_elements_by_tag_name("li")
                season_list = [li.text for li in lis]
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[2]/div[2]".format(level_idx)).click()
                return season_list
            except Exception as e:
                print(e)
                print("시즌메뉴탭 클릭 재시도횟수 {}번".format(i + 1))
                time.sleep(1)
                continue;

    def __results_league_menu_scanner(self,level):
        for i in range(10) :
            try :
                level_idx = ["First Team", "PL2", "U18"].index(level) + 1
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[1]/div[2]".format(level_idx)).click()

                time.sleep(0.5)
                ul = self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[1]/ul".format(level_idx))
                lis = ul.find_elements_by_tag_name("li")
                league_list = [li.text for li in lis]
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/div[{}]/section/div[1]/div[2]".format(level_idx)).click()
                return league_list

            except Exception as e:
                print(e)
                print("리그메뉴탭 클릭 재시도횟수 {}번".format(i + 1))
                time.sleep(1)
                continue;

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
        if self.page_type == "Stat" :
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

        elif self.page_type == "Results" :
            #빈 데이터프레임 생성
            self.data = pd.DataFrame([''] * 20).T.drop(0)

            level_list = ["First Team", "PL2", "U18"]

            for level in level_list :

                self.set_level_results_page(level)
                print(level)
                league_list = self.__results_league_menu_scanner(level)
                print(league_list)
                for league in league_list :
                    if league == "All Competitions" : continue;
                    #리그 페이지 세팅
                    self.set_league_results_page(league, level)
                    season_list = self.__results_season_menu_scanner(level) #현 리그 시즌 리스트로 업데이트
                    print(season_list)
                    for season in season_list :
                        #시즌 페이지 세팅
                        print("{}의 {}의 {}시즌 경기결과를 수집합니다.".format(level, league, season))
                        self.set_season_results_page(season, level)
                        #문서 뭉치 받기
                        result = self.fetch("span", "span")
                        #문서 뭉치 크롤링
                        for i in range(len(result)):
                            if len(result[i]) > 10 : # 데이터 리스트 길이로 필터링
                                tmp = [""] * 20 # 빈리스트 생성
                                for j in range(len(result[i])):
                                    tmp[j] = result[i][j].strip()
                                    tmp[0] = league
                                    tmp[1] = season
                                    tmp[3] = level
                                self.data.loc[self.data.shape[0]] = tmp
            #데이터 처리
            self.data = self.data.iloc[:, [3, 0, 1, 2, 4, 6, 9]]
            self.data.columns = ['level','league','season','home','score','away','stadium']
            print("데이터 수집을 완료했습니다.")

        elif self.page_type == "Lineup" :

            print("{} 개 프로세스로 작동합니다.".format(len(self.partitions.keys())))
            for partition_key in self.partitions.keys():
                t = threading.Thread(target=self.crawl, args=partition_key)
                t.start()

        elif self.page_type == "Matchs":
            try :
                # 데이터 크롤링
                matchstats = self.scrap_matchstats()

                # 연속적으로 다음페이지 넘어가기
                while self.first_match != self.last_match:
                    self.first_match += 1
                    self.set_matchstats_page(self.first_match)
                    matchstats = matchstats.append(self.scrap_matchstats()).fillna("")

                self.data = matchstats
                self.data = self.data.reset_index(drop=True)
                self.reset_soup()
                print("데이터 수집을 완료했습니다.")
            except :
                print("경기내용이 아직 없습니다. 데이터 수집을 종료합니다.")
                return;

    def crawl(self, cur_page, last_page):

        if self.page_type == "Lineup" :
            while cur_page != (last_page + 1):

                for i in range(3):
                    try:
                        self.set_lineup_page(cur_page)
                        lineup_home = self.scrap_lineup("home")
                        lineup_away = self.scrap_lineup("away")
                        self.partition[(cur_page, last_page)] = pd.concat(
                            [self.partition[(cur_page, last_page)], lineup_home, lineup_away])
                        self.partition[(cur_page, last_page)] = self.partition[(cur_page, last_page)].reset_index(drop=True)
                        self.reset_soup()
                        cur_page += 1
                        print("{}번째 매치 라인업정보 수집완료!".format(cur_page))
                        break
                    except:
                        print("{}번째 매치 라인업정보를 수집하지 못했습니다. 재시도({})".format(cur_page, i))
                        if i == 2: self.error_page.append(cur_page)  # 에러페이지 기록
                        continue
        else :
            pass;

        print("데이터 수집을 완료했습니다.")

    def scrap_matchstats(self):

        # 매치 기본 정보
        matchInfo = self.driver.find_element_by_class_name("matchInfo").text.split("\n")
        # 매치 클럽 이름
        home_nm = self.driver.find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[1]/a[2]/span[1]").text
        away_nm = self.driver.find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[3]/a[2]/span[1]").text
        # 경기 스코어
        score = self.driver.find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[2]/div").text
        dataset = self.fetch("tr", "td")
        cols = ["matchinfo_"+str(i+1) for i in range(len(matchInfo))] + ["home_team", "score", "away_team"] + ["home_" + data[1] for data in dataset] + ["away_" + data[1] for data in dataset]
        vals = matchInfo + [home_nm, score, away_nm] + [data[0] for data in dataset] + [data[2] for data in dataset]
        matchstats = pd.DataFrame(columns=cols)
        matchstats.loc[0] = vals
        return matchstats

    def scrap_lineup(self, team):

        hora_idx = 0 if team == "home" else 1
        # 매치 기본 정보
        matchInfo = self.driver.find_element_by_class_name("matchInfo").text.split("\n")
        # 매치 클럽 이름
        team_idx = 1 if hora_idx == 0 else 3
        team_nm = self.driver.find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[{}]/a[2]/span[1]".format(team_idx)).text
        # 경기 스코어
        score = self.driver.find_element_by_xpath(
            "//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[2]/div").text
        # 라인업 정보
        lineup_elems = self.driver.find_elements_by_class_name("matchLineupTeamContainer")
        position_elems = lineup_elems[hora_idx].find_elements_by_tag_name('h3')
        players_by_position_elems = lineup_elems[hora_idx].find_elements_by_tag_name('ul')
        positions = [position.text for position in position_elems]
        members_by_position_text = [members.text.replace('Shirt number', '').replace("Team Captain\nC\n", '') for
                                    members in players_by_position_elems]

        # 라인업 정보 데이터 처리
        lineup = pd.DataFrame(
            columns=["matchinfo_"+str(i+1) for i in range(len(matchInfo))] + ["club", "position", "start", "number",
                     "name", "nationality", "sub", "sub_time", "goal", "card"])

        for idx, members_text in enumerate(members_by_position_text):

            p = re.compile(
                    r'(\n(?P<player>[\d]+[\D]+[\d\n\'+ ]*[\D]+)(?=\n\n\d{1,2}\n))|(\n(?P<player2>[\d]+[\D]+[\d\n\'+ ]*[\D]+)$)')
            m = p.finditer(members_text)
            players = []
            for player in m:
                player1 = player.group("player")
                player2 = player.group("player2")
                if player1 != None:  players.append(player.group("player"))
                if player2 != None:  players.append(player.group("player2"))
            players = [player.split("\n") for player in players]

            for player in players:
                index = idx if idx <= 3 else 4
                start = "substitue" if index == 4 else "start"  # 주전/후보여부
                nationality = player[-2] if index == 4 else player[-1]  # 국적
                position = player[-1] if index == 4 else positions[index]  # 포지션
                sub = "On" if "Substitution On" in player else (
                    "Off" if "Substitution Off" in player else "")  # 교체여부
                sub_time = ""
                for factor in player:
                    if factor.find("\'") != -1: sub_time = factor  # 교체시간
                goal = str(player.count("Goal"))  # 골 수
                # 경고, 퇴장 여부
                try:
                    player.index("Yellow Card")
                    card = "Yellow"
                except:
                    try:
                        player.index("Red Card")
                        card = "Red"
                    except:
                        card = ""

                # 데이터 저장
                lineup.loc[lineup.shape[0]] = matchInfo + [team_nm,  # 경기 및 팀 정보 입력
                     position, start, player[0], player[1], nationality, sub, sub_time, goal, card]  # 선수 정보 입력
        return lineup

    def set_lineup_page(self, page_nm) :

        dst_url = self.url + str(page_nm)
        self.driver.get(dst_url)
        time.sleep(0.3)
        for i in range(10) :
            try :
                self.driver.find_element_by_class_name("matchCentreSquadLabelContainer").click()
                home = self.driver.find_element_by_xpath("//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[1]/a[2]/span[1]").text
                away = self.driver.find_element_by_xpath("//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[3]/a[2]/span[1]").text
                print("{}번째 ({} VS {}) 매치 페이지 로드 완료!".format(page_nm,home, away))
                break;
            except :
                print("재시도 횟수 : {}".format(i+1))
                continue


    def set_matchstats_page(self, page_nm):

        dst_url = self.url + str(page_nm)
        self.driver.get(dst_url)
        time.sleep(0.3)
        for i in range(10):
            try:
                self.driver.find_element_by_xpath("//*[@id='mainContent']/div/section/div[2]/div[2]/div[1]/div/div/ul/li[3]").click()
                home = self.driver.find_element_by_xpath("//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[1]/a[2]/span[1]").text
                away = self.driver.find_element_by_xpath("//*[@id='mainContent']/div/section/div[2]/section/div[3]/div/div/div[1]/div[3]/a[2]/span[1]").text
                print("{}번째 ({} VS {}) 매치 페이지 로드 완료!".format(page_nm,home, away))
                break;
            except:
                print("재시도 횟수 : {}".format(i + 1))
                continue

    def takeout(self):
        '''
        크롤링한 데이터셋을 리턴하는 함수
        :return: data (타입 : 데이터프레임)
        '''
        if self.page_type == "Lineup" :
            if self.n_jobs == 1 :
                return self.partitions.pop()
            else :
                return self.partitions
        else :
            return self.data
