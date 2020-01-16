from EventDBManagement import EventsDBManager
import json
evenManager = EventsDBManager()
list = [90942,
94400,
93754,
99557,
99814,
98598,
97979,
98130,
85368,
99427,
93529,
99746,
19418,
90531,
93779,
62763,
89728,
86761,
89372,
94220,]
for i in list:
    dict = evenManager.get_event_with_nearest(i)
    with open("./test_texts/"+ str(i) +"'.json","w") as f:
        json.dump(dict,f)
        print(i, "加载入文件完成...")
