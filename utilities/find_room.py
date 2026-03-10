import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
db = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def find_empty_room(_date, _building=None):
    date = datetime.strptime(_date, '%Y-%m-%d')
    print(date)
    result = (
        db.table("classes")
        .select("startTime, rooms(name), building.name")
        .eq("building(name)", _building)
        .gt("startTime", date)
        
        .execute()
    )
    print(result.data)
    # building = db.table("building").select("id").eq("name", _building).execute()
    # print(building.data)
    # rooms = db.table("rooms").select("*").eq("building", building.data[0]["id"]).neq("id", [room["room"] for room in result.data]).execute()
    # print(rooms.data)
    

find_empty_room("2026-04-03", "WChrobrego")