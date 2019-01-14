#!/usr/bin/env python
# coding: utf-8

import requests as req
import json
import pandas as pd
import warnings
from IPython.display import clear_output
from time import sleep
from abc import *
warnings.filterwarnings("ignore")


class BigwingAPIProcessor(metaclass=ABCMeta) :
    ''' 빅윙추상클래스 '''
    @abstractmethod
    def __fetch(self) :
        pass
    @abstractmethod
    def run(self) :
        pass
    
    def insert(self, data, col) :
        '''DataFrame 자료형의 데이터 입력받고, 검색키워드가 있는 컬럼명을 인수로 받습니다.
        '''
        self._check("url") # 인증키 유효성 확인
    
        # 데이터 유효성 확인 및 삽입
        if data.__class__ != pd.DataFrame().__class__ :
            print("FAILED : 입력하신 데이터는 pandas 데이터프레임이 아닙니다.")
        else :
            if col not in data.columns :
                print("FAILED : 입력하신 데이터에 해당 컬럼이 존재하지 않습니다.")
            else :
                self.data = data
                self.col = col
                print("SUCCEEDED : 데이터를 삽입했습니다.")
        return self
    
    def run(self, limit=True) :
        '''api 호출을 일괄실행시킵니다.
        limit 인수는 Boolean 자료형을 받습니다. Default는 True입니다.
        limit이 True일경우, 처리상태가 "OK"인 행데이터는 Skip하고 연속진행합니다.'''
        self._check("data") #데이터 삽입여부 확인
        self._check("url") # 인증키 유효성 확인

        data = self.data.copy()
        if (limit == True) & ("처리상태" in data.columns) :
            data = data[data["처리상태"] != "OK"]
        data_size = len(data)
        succeed_cnt = 0
        if data_size != 0 :
            for idx, keyword in enumerate(data[self.col]) :
                #변환 및 저장
                values = self.__fetch(keyword)
                if values[0] == "OK" :
                    succeed_cnt += 1
                for value in values[1:] :
                    self.data.loc[self.data[self.col]==keyword, value[0]] = value[1]
                self.data.loc[self.data[self.col]==keyword, "처리상태"] = values[0]
                #결과 출력
                print("{} / {} ... {}%".format(idx+1,data_size, round((idx+1)/data_size*100),1))
                print("{} --> {}".format(keyword,values))
                clear_output(wait=True)
        print("처리완료!")
        print("추가정상처리건수 : ", succeed_cnt)
        self.summary()
    
    def takeout(self) :
        
        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        return self.data
    
    def get_param(self) :
        
        try:
            self.params
        except NameError:
            raise RuntimeError("FAILED : 인수를 설정하지 않았습니다.")
        return self.params.items()
    
    def _set_param(self) :

        param_str = ""       
        for param_nm, param_val in self.params.items() :
            param_str = param_str + "&" + param_nm + "=" + param_val
        self.url = self.base_url + param_str
    #처리결과요약 함수
    def summary(self) :
        
        try:
            self.data
        except NameError:
            raise RuntimeError("FAILED : 처리된 데이터가 없습니다.")
        print("- 처리 건수 : ",self.data.shape[0])
        print("- 성공 건수 : ",sum(self.data.처리상태 == "OK"))
        print("- 실패 건수 : ",sum(self.data.처리상태 != "OK"))
        print("- 성공율 : {}%".format(round(sum(self.data.처리상태 == "OK")/self.data.shape[0]*100,1)))
        
    def _check(self, attr) :

        try:
            getattr(self, attr)
        except AttributeError:
            raise RuntimeError("FAILED : {} 를 확인해주세요.".format(attr))

####브이월드지오코더####
class Vwolrd_Geocoder(BigwingAPIProcessor) :
     #지오코딩 API 서비스 사이트 URL 설정
      
    def __init__(self, key, crs="EPSG:5181",type_="ROAD") :
        
        #파라미터 설정
        self.base_url = "http://api.vworld.kr/req/address?service=address&request=getCoord"
        self.params = {}
        self.params["key"] = key #인증키 설정
        self.params['crs'] = crs #좌표계 설정
        self.params['type'] = type_ #도로명 또는 지번 설정 (ROAD or PARCEL)
        self.params['simple'] = "true" #간단한 출력설정
        self._set_param()
        
        #인증키 유효성 확인
        status = self.__fetch("서울특별시 종로구 세종로 1")[0]     
        if status != "OK" :
            del self.params['key'], self.url
            print("KEY " + status + " : 인증키를 다시 확인해주세요.")
        else :
            print("KEY " + status + " : 인증키 유효성 확인 성공!")
                    
    def __fetch(self, address) :
        
        values = {}
        fetch_url = self.url +"&address="+ address
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)

        status = resp['response']['status'] #상태코드 조회
        if status == 'OK' :
            #반환데이터 변수저장
            values = resp['response']['result']['point']
            return tuple([status] + [value for value in values.items()])
        else :
            return tuple(["NOT_FOUND"])

        
####구글지오코더####
class Google_Geocoder(BigwingAPIProcessor) :
             
    def __init__(self, key) :
        
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
        self.params = {}
        self.params["key"] = key #인증키 설정
        self._set_param()
        
        #인증키 유효성 확인
        status = self.__fetch("서울특별시 종로구 세종로 1")[0]    
        if status != "OK" :
            del self.params['key'], self.url
            print("KEY " + status + " : 인증키를 다시 확인해주세요.")
        else :
            print("KEY " + status + " : 인증키 유효성 확인 성공!")

    
    def __fetch(self, keyword) :
        
        values = {}
        fetch_url = self.url +"&address="+ keyword
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)
        status = resp['status'] #상태코드 조회
        if status == 'OK' :
            values = resp['results'][0]['geometry']['location']
            return tuple([status] + [value for value in values.items()])
        else :
            return tuple(["NOT_FOUND"])
            
### 행정안전부 도로명주소변환기 ####
class AddressConverter(BigwingAPIProcessor) :

    def __init__(self, key) :
        
        self.base_url = "http://www.juso.go.kr/addrlink/addrLinkApi.do?"
        self.params = {}
        self.params["confmKey"] = key #인증키 설정
        self.params['currentPage'] = "1" 
        self.params['countPerPage'] = "10"
        self.params['resultType'] = "json" 
        self._set_param()
        
        #인증키 유효성 확인
        status = self.__fetch("서울특별시 종로구 세종로 1")[0]
        if status != "OK" :
            del self.params['confmKey'], self.url
            print("KEY " + status + " : 인증키를 다시 확인해주세요.")
        else :
            print("KEY " + status + " : 인증키 유효성 확인 성공!")   
    
    def __fetch(self, keyword) :
        
        values = {}
        fetch_url = self.url +"&keyword="+ keyword
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)
        
        status = "OK" if resp['results']['juso'] != [] else "NOT_FOUND" #상태코드 조회
        if status == 'OK' :
            values = resp['results']['juso'][0]
            return tuple([status] + [value for value in values.items()])
        else :
            return tuple(["NOT_FOUND"])    

### API호출기 ####
class SuperAPICaller(BigwingAPIProcessor) :

    def __init__(self, base_url, **params) :
        
        self.base_url = base_url
        self.params = params
        self._set_param()
        
    #검색어 태그 이름을 설정합니다.
    def set_tagname(name) :
        
        self.tagname = name
        
    #상태코드 위치와 정상코드를 설정합니다.
    def set_status(status_loc, OK) :
        
        self.status_loc = status_loc
        self.OK = OK
        
    #호출할 json 딕셔너리 위치를 설정합니다.
    def set_values(values) :
        
        self.values = values
        
    def __fetch(self, keyword) :
        
        values = {}
        fetch_url = self.url +"&" + self.tagname + "="+ keyword
        
        for cnt in range(10) :
            try :     
                resp = req.get(fetch_url).text
            except :
                print("{}번째 Fetch".format(cnt+2))
                sleep(3)
                continue
            break
        resp = json.loads(resp)
        
        status = "OK" if self.status_loc != self.OK else "NOT_FOUND" #상태코드 조회
        if status == 'OK' :
            return tuple([status] + [value for value in self.values.items()])
        else :
            return tuple(["NOT_FOUND"])    
