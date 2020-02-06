from DataManagements.EventDBManagement import EventsDBManager
from DataManagements.UserRatingDBManagement import UserRatingManager
from DataManagements.UserDBManagement import UserDBManager
from DataManagements.BackendAPIStaticList import *
from random import choice,randint

@singleton
class UserRatingSimulator():
    def __init__(self):
        self.userRatingManager = UserRatingManager()
        self.eventDBManager = EventsDBManager()
        self.userDBManager= UserDBManager()
    def simulate_rating(self,number_of_users,number_of_events_each):
        for i in range(number_of_users):
            self.userDBManager.create_new_user('SimuUser'+str(i),'nopsw','i@gmail.com')
            all_large_cates = list(self.eventDBManager.get_catagories_statistics().keys())
            cates_simu = []
            while len(cates_simu) < 3:
                cate = randint(1,49)
                if cate not in cates_simu:
                    cates_simu.append(cate)
            all_those_types_events = []
            for cate in cates_simu:
                all_those_types_events += self.eventDBManager.all_events_of_cates(cate)
            rating_events = []
            while len(rating_events) < number_of_events_each:
                event = choice(all_those_types_events)
                if event not in rating_events:
                    rating_events.append(event)
            user_id = self.userDBManager.return_user_id('SimuUser'+str(i))
            for event in rating_events:
                self.userRatingManager.add_rating(user_id,event['event_id'],randint(1,5))




if __name__ == "__main__":
    userRatingSimulator = UserRatingSimulator()
    userRatingSimulator.simulate_rating(2,3)
    print(userRatingSimulator.userRatingManager.check_database())
