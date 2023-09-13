import requests
import sched
import time
import datetime
import yaml
import shutil

s = sched.scheduler(time.time, time.sleep)

def update_file(sc):
    # 2. Load config
    filename = 'config.yaml'
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.Loader)


    web3Token = config['peakUrl'] + "session.txt"
    web3Token = requests.request("GET", web3Token)
    

    url = "https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/peak-game/status"

    payload = {}
    
    web3Token = f.read()
    # remove " from the string
    web3Token = web3Token.replace('"', '')

    print(web3Token)

    # set web3-token header to the value of the session.txt file
    headers = {
        'web3-token': web3Token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()

    print(data)

    # Extract the values from the dictionary if there is a next round
    opt_in_start = "'None'"
    starts_at = "'None'"
    game = "'None'"
    peaksOpen = "'None'"

    # if data error key exists
    if "error" in data:
        print("Unauthorized")
    # check if array is empty
    elif data["season"]["current"]["nextRound"] != {}:
        print(data["season"]["current"]["nextRound"])
        opt_in_start = data["season"]["current"]["nextRound"]["optInStart"]
        starts_at = data["season"]["current"]["nextRound"]["startsAt"]
        game = data["season"]["current"]["nextRound"]["game"]
        peak1status = data["season"]["current"]["currentRound"]['levels'][0]['active']
        peak2status = data["season"]["current"]["currentRound"]['levels'][1]['active']
        peak3status = data["season"]["current"]["currentRound"]['levels'][2]['active']

        peaksOpen = ""
        if peak1status:
            peaksOpen += "Base"
        if peak2status:
            peaksOpen += ",Slope"
        if peak3status:
            peaksOpen += ",Summit"

    # Read the current content of peak-game.txt
    with open('peak-game.txt', 'r') as current_file:
        current_content = current_file.read()

    # Read the current content of peak-game-previous.txt
    with open('peak-game-previous.txt', 'r') as previous_file:
        previous_content = previous_file.read()

    # Check if the current content is different from the previous content
    if current_content != f"game: {game}\noptInStart: {opt_in_start}\nstartsAt: {starts_at}\nlevels: {peaksOpen}":
        # If they are different, copy the current content to peak-game-previous.txt
        with open('peak-game-previous.txt', 'w') as previous_file:
            previous_file.write(current_content)

        # Write the new data to peak-game.txt
        with open('peak-game.txt', 'w') as file:
            file.write(f"game: {game}\noptInStart: {opt_in_start}\nstartsAt: {starts_at}\nlevels: {peaksOpen}")

    # Calculate the time until the next zero-minute boundary
    now = datetime.datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    delay = (next_hour - now).seconds

    # Run the function again at the next zero-minute boundary
    s.enter(delay, 1, update_file, (sc,))

# Run the function immediately when the script starts
s.enter(0, 1, update_file, (s,))
s.run()
