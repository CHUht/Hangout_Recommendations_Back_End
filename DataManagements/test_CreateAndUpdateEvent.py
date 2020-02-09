from DataManagements.CreateDB import *
from DataManagements.RetrieveEventsFromApi import *

"""
this is for starting the construction of our local database
"""
if __name__ == "__main__":
    # eventsDBManager = EventsDBManager()
    # eventsDBManager.delete_Event_table()
    # eventsDBManager.drop_table()
    create_databases()
    download_and_clean()
