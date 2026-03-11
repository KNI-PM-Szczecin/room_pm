import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Example usage:
# room_finder = RoomFinder(URL, KEY)
# room_finder.findEmptyRooms("2026-03-11 12:00", BUILDING_NAME)
# will find empty rooms in BUILDING_NAME from 12:00 to 13:00 on 2026-03-11
# returns a list of dictionaries with room names and their buildings, e.g.:
# [
#     {"name": room_name_0, "building": BUILDING_NAME},
#     {"name": room_name_1, "building": BUILDING_NAME},
#     ...
# ]

class RoomFinder:

    def __init__(self, URL: str, KEY: str, _debug: bool = False ):
        self.DEBUG = _debug
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        self.db = create_client(URL, KEY)

    def findBusyRooms(self, startTime: datetime, _building: str, endTime: datetime | None = None) -> list:
        if self.DEBUG:
            print(f"Finding full rooms in {_building} from {startTime} to {endTime}")
        result = (
            self.db.table("roomschedule")
            .select("*")
            .overlaps("during", f"[{startTime.isoformat(sep=' ')}, {endTime.isoformat(sep=' ')}]")
            .eq("name", _building)
            .execute()
        )
        if self.DEBUG:
            print(*result.data, sep="\n")
        return result.data

    def findEmptyRooms(self, _date: str, _building: str, _endTime: str | None = None) -> list:

        startTime = datetime.strptime(_date, '%Y-%m-%d %H:%M')
        if not _endTime:
            endTime = startTime + timedelta(hours=1)
        else:
            endTime = datetime.strptime(_endTime, '%Y-%m-%d %H:%M')
        
        busy_rooms = self.findBusyRooms(startTime, _building, endTime)
        busy_room_names = {room["room"] for room in busy_rooms}

        all_rooms_result = (
            self.db.table("rooms")
            .select("name, building!inner(name)")
            .eq("building.name", _building)
            .execute()
        )
        all_rooms = all_rooms_result.data
        empty_rooms = [room for room in all_rooms if room["name"] not in busy_room_names]

        for room in empty_rooms:
            room["building"] = room["building"]["name"]

        if self.DEBUG:
            print(*empty_rooms, sep="\n")

        return empty_rooms