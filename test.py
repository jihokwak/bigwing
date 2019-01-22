
'''1~9999번 경기 라인업정보 스크랩
결과 : 8524번 페이지는 누락되어 있어 스크랩되지 못함'''
from bigwing.crawler import EPLCrawler
epl = EPLCrawler(page_range=(1,9999), page_type="Lineup", n_jobs=10)
epl.start()
epl.monitor()
epl.save()
epl.backup()
lineup = epl.takeout()

#데이터를 로컬파일에서 로드하고 문자열로 데이터 처리
import pandas as pd
lineup = pd.read_csv("D:\Kwak\Doc\git/bigwing/backup/0122_2243/Lineup/data/total_Lineup_1_9999.csv", encoding="utf8", index_col=False)
lineup = lineup.iloc[:,1:-2]
for col in lineup.columns :
    lineup[col] = lineup[col].astype(str)
#DB저장
from bigwing.db import BigwingMysqlDriver
db = BigwingMysqlDriver(host = "121.130.100.175",user = "bigwing",dbname = "bigwingdb",passwd = "bigdream!")
db.show()
db.create('Lineups_1_9999', tuple(lineup.columns))
db.insert_bulk("Lineups_1_9999", lineup)
db.commit()
db.close()
epl.close()
del epl

'''10000~16000번 경기 라인업정보 스크랩'''
from bigwing.crawler import EPLCrawler
epl = EPLCrawler(page_range=(10000,16000), page_type="Lineup", n_jobs=1)
epl.start()
epl.monitor()
epl.save()
epl.backup()
lineup = epl.takeout()

#데이터를 로컬파일에서 로드하고 문자열로 데이터 처리
import pandas as pd
lineup = pd.read_csv("D:/Kwak/Doc/git/bigwing/tmpdata/Lineup/data/total_Lineup_10000_16000.csv", encoding="utf8", index_col=False)
lineup = lineup.iloc[:,1:-2]
for col in lineup.columns :
    lineup[col] = lineup[col].astype(str)
#DB저장
from bigwing.db import BigwingMysqlDriver
db = BigwingMysqlDriver(host = "121.130.100.175",user = "bigwing",dbname = "bigwingdb",passwd = "bigdream!")
db.show()
db.create('Lineups_10000_16000', tuple(lineup.columns))
db.insert_bulk("Lineups_10000_16000", lineup)
db.commit()
db.close()
epl.close()
del epl



'''22300~37020번 경기 라인업정보 스크랩'''
from bigwing.crawler import EPLCrawler
epl = EPLCrawler(page_range=(22300,37020), page_type="Lineup", n_jobs=1)
epl.start()
epl.monitor()
epl.save()
epl.backup()
lineup = epl.takeout()

#데이터를 로컬파일에서 로드하고 문자열로 데이터 처리
import pandas as pd
lineup = pd.read_csv("D:/Kwak/Doc/git/bigwing/tmpdata/Lineup/data/total_Lineup_22300_37020.csv", encoding="utf8", index_col=False)
lineup = lineup.iloc[:,1:-2]
for col in lineup.columns :
    lineup[col] = lineup[col].astype(str)
#DB저장
from bigwing.db import BigwingMysqlDriver
db = BigwingMysqlDriver(host = "121.130.100.175",user = "bigwing",dbname = "bigwingdb",passwd = "bigdream!")
db.show()
db.create('Lineups_22300_37020', tuple(lineup.columns))
db.insert_bulk("Lineups_22300_37020", lineup)
db.commit()
db.close()
epl.close()
del epl