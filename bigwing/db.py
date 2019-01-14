import pymysql
import numpy as np
import pandas as pd
from pymongo import MongoClient

'''* BigwingMysqlDriver 모듈 클래스 
     - 사용법 : 인스턴스명 = BigwingMysqlDriver("호스트명", "DB명", "유저명", "패스워드")
     - port는 3306 을 디폴트로 사용 (변경시 port=포트번호 를 인수로 넘김) 
'''
class BigwingMysqlDriver() :

    def __init__(self, host, dbname, user, passwd, port=3306):

        self.__host = host
        self.__user = user
        self.__dbname = dbname
        self.db = pymysql.connect(user=self.__user, host=self.__host, db=self.__dbname, passwd=passwd, port=port, charset='utf8')
        self.cursor = self.db.cursor() #커서 객체 생성

        #테이블 정보 로드
        self.tables = {}
        self.cursor.execute("show tables")
        tables_info = self.cursor.fetchall()

        for table_info in tables_info :

            table = table_info[0]
            self.cursor.execute("show columns from `{}`".format(table))
            columns_info = self.cursor.fetchall()
            columns = []
            for column_info in columns_info :
                columns.append(column_info[0])
            columns = tuple(columns)
            self.tables[table] = columns

    def show(self):

        return self.tables

    '''* 테이블을 생성하는 함수
        - 사용법 : 인스턴스명.create('테이블명', (컬럼1, 컬럼2,...) )
        - 특징 : 모든 컬럼은 varchar(50) default null 형으로 일괄 생성됨
    '''
    def create(self, table, *args):

        SQL = " CREATE TABLE """ + table + """ ( """
        cols = []

        for arg in args[0] :
            SQL = SQL + "{} varchar(50) DEFAULT NULL,".format(arg)
        SQL = SQL[:-1] # 쉼표제거
        SQL = SQL + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        print(SQL)
        self.cursor.execute(SQL)
        self.tables[table] = args[0]
        print("{} 테이블이 생성되었습니다.".format(table))

    '''* 특정 테이블을 삭제하는 함수
         - 사용법 : 인스턴스명.delete('테이블명')
     '''
    def delete(self, table):

        SQL = "DROP TABLE {}".format(table)
        self.cursor.execute(SQL)
        del self.tables[table]
        print("{} 테이블이 삭제되었습니다.".format(table))

    '''* 특정 테이블에 데이터를 입력하는 함수
        - 사용법 : 인스턴스명.insert('테이블명')
    '''
    def insert(self, table, *args):

        if table not in self.tables.keys() :
            print("{} 테이블이 존재하지 않습니다.".format(table))
            return;

        if  np.size(self.tables[table]) != np.size(args[0]) :
            print("{} 테이블의 컬럼은 {} 이며 총 {}개 입니다.".format(table, self.tables[table], np.size(self.tables[table])))
            return;

        SQL = "insert into {} (".format(table)
        for col in self.tables[table] :
            SQL = SQL + "{}, ".format(col)
        SQL = SQL[:-2] # 쉼표제거
        SQL = SQL + ") values ("
        for len in range(np.size(self.tables[table])) :
            SQL = SQL + "%s, "
        SQL = SQL[:-2] # 쉼표제거
        SQL = SQL + ")"
        self.cursor.execute(SQL, *args)

    '''* insert()함수 사용후 커밋을 실행하는 함수
        - 사용법 : 인스턴스명.commit()
    '''
    def commit(self):

        self.db.commit()

    '''* 테이블 데이터를 데이터프레임 타입으로 가져오는 함수
        - 사용법 : 인스턴스명.takeout('테이블명')
    '''
    def takeout(self, table):

        self.cursor.execute("select * from {}".format(table))
        df = pd.DataFrame(columns=self.tables[table])
        while True :
            row = self.cursor.fetchone()
            if row == None :
                break;
            df.loc[df.shape[0]] = row
        return df

    def __del___(self):#커서종료

        self.cursor.close()
        #DB커넥터종료
        self.db.close()


'''현재 개발진행중'''
class BigwingMongoDriver() :

    def __init__(self, db, collection):

        self.client = MongoClient()
        self.collection = self.client[db][collection]

    def save(self, **kwargs) :

        print(kwargs)
        try :
            self.collection.insert_one(kwargs)
        except :
            print("저장되지 않았습니다.")
            return

    def find_all(self):

        for n in self.collection.find() :
            yield n
