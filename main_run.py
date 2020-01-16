from CreatingDBs.CreateDB import *
from RetrieveEventsFromApi import *
from EventDBManagement import *

if __name__ == "__main__":
    # eventsDBManager = EventsDBManager()
    # eventsDBManager.delete_Event_table()
    # eventsDBManager.drop_table()
    create_databases()
    download_and_clean()
