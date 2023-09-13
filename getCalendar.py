import requests
import sched
import time
from datetime import datetime
import pytz
import re
import yaml

# Function to parse ISO 8601 date-time strings that might lack microseconds
def parse_iso8601(s):
    # Append microseconds if they are missing
    if "." not in s:
        s += ".000000Z"

    return datetime.fromisoformat(s)

# Function to fetch game times and write to files
def fetch_game_times_and_write_to_files():
    url = "https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/peak-game/calendar"
    payload = {}

    # 2. Load config
    filename = 'config.yaml'
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.Loader)

    web3Token = config['peakUrl'] + "session.txt"
    web3Token = requests.request("GET", web3Token)
    web3Token = web3Token.text

    headers = {
        'web3-token': web3Token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()

    print(data)

    current_time = datetime.now(pytz.UTC)

    next_times = {}

    for entry in data:
        game = entry["game"]
        starts_at_str = entry["startsAt"].replace("Z", "")
        
        # Parse ISO 8601 date-time strings
        starts_at = parse_iso8601(starts_at_str).replace(tzinfo=pytz.UTC)

        if starts_at > current_time:
            if game not in next_times or starts_at < next_times[game]:
                next_times[game] = starts_at

    print(next_times)

    # Write game times to respective files
    with open("nextTug.txt", "w") as tug_file:
        tug_time = next_times.get('TUG_OF_WOOL', None)
        if tug_time:
            tug_file.write(f"Next time for Tug: {tug_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        else:
            tug_file.write("Next time for Tug: N/A")

    with open("nextWaterwall.txt", "w") as waterwall_file:
        waterwall_time = next_times.get('WATER_WALL', None)
        if waterwall_time:
            waterwall_file.write(f"Next time for Waterwall: {waterwall_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        else:
            waterwall_file.write("Next time for Waterwall: N/A")

    with open("nextWolfwits.txt", "w") as wolfwits_file:
        wolfwits_time = next_times.get('WOLF_WITS', None)
        if wolfwits_time:
            wolfwits_file.write(f"Next time for Wolfwits: {wolfwits_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        else:
            wolfwits_file.write("Next time for Wolfwits: N/A")

# Create a scheduler
scheduler = sched.scheduler(time.time, time.sleep)

# Define the interval for running the code (3 hours)
interval_seconds = 3 * 60 * 60

# Run the code initially
fetch_game_times_and_write_to_files()

# Schedule the code to run every 3 hours
while True:
    scheduler.enter(interval_seconds, 1, fetch_game_times_and_write_to_files, ())
    scheduler.run()
