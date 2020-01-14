from CreatingDBs.CreateDB import *
from RetrieveEventsFromApi import *
from EventDBManagement import *

if __name__ == "__main__":
    Events = EventsDBManager()
    Events.delete_Event_table()
    Events.drop_table()
    create_databases()
    download_and_clean()
