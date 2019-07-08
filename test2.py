from bigwing.api import Bigwing_Geocoder
import pandas as pd

ROAD_JUSO_API_KEY = "U01TX0FVVEgyMDE5MDYyNjExNTAzMTEwODgzODE="
VWORLD_KEY = "38142259-7809-3397-B1FD-2D96417DE3EB"
dict = {
    "address": ["서울특별시 강남구 역삼동 709 테헤란IPARK 105동502호"]
}

data = pd.DataFrame(dict)
big = Bigwing_Geocoder(vkey=VWORLD_KEY, ckey=ROAD_JUSO_API_KEY)

big.insert(data, "address")
big.run()
data.info()

