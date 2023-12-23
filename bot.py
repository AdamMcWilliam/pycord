"""
Run a Discord bot that takes the !gas command and shows the status in an embed + shows the prices in the sidebar
"""
# Example:
# python3 gas_bot.py -s etherscan

#from asyncio.windows_events import NULL
from __future__ import print_function
from typing import Tuple
import os
import string
import random
import sqlite3
import math
import logging
import yaml
import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import Bot
import argparse
import requests
import schedule
import sched
import time
import datetime
from tinydb import TinyDB, Query
from tinydb.operations import delete
from tinydb import where
import requests
import json
from types import SimpleNamespace
import re
from requests import Request, Session
import requests
from google_images_search import GoogleImagesSearch
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.request import urlopen
from json import dumps
from dateutil.parser import parse



conn = sqlite3.connect('bot.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS games(
   guildid TEXT,
   gamestatus INT,
   guesses INT,
   answer TEXT,
   charset TEXT,
   starttime INT);
""")
conn.commit()

db = TinyDB('db.json')
table = Query()
dbMed = TinyDB('meddb.json')
dbHackScore = TinyDB('hackScore.json')


def p5js_to_image(sketch):
    #remove last }
    sketch = sketch[:-1]
    # Create a new Python file and write some code to it
    with open("p5Output.py", "w") as f:
        f.write('import p5 \n' + sketch + '\n save("result.png")}')

    # Run the newly created Python file
    os.system("p5Output.py")
    

def get_NFT_image(url):
    ##givenURL will look like https://opensea.io/assets/0x10064373e248bc7253653ca05df73cf226202956/11211
    ##strip after assets/
    asset = url.split("assets/")
    asset = asset[1]
    asset = asset.split("?")
    asset = asset[0]
    #print(asset)
    ##add to api url
    APIurl = "https://api.opensea.io/api/v1/asset/"+asset

    response = requests.request("GET", APIurl)
    #print(response.text)

    x = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))
    #print(x.name, x.hometown.name, x.hometown.id)

    
    if x.image_original_url != None and x.image_original_url.startswith('https://ipfs.io') != True and x.image_original_url.endswith('.svg') != True and "." in x.image_original_url[len(x.image_original_url) -4]:
        print(x.image_original_url)
        return x.image_original_url
    else:
        print(x.image_url)
        return x.image_url
    
#for 10k10k   
def fetch_adj_or_animal(type, aliteration, animal): 

    if(aliteration == True and type =="adjective"):
        animalFirst = animal[0]
        url = f"https://random-word-form.herokuapp.com/random/{type}/{animalFirst}"
    else:
        url = f"https://random-word-form.herokuapp.com/random/{type}"

    print(url)
    r = requests.get(url)
    result = r.json()[0]
    return result

def get_gas_from_etherscan(key: str,
                           verbose: bool = False) -> Tuple[int, int, int]:
    """
    Fetch gas from Etherscan API
    """
    r = requests.get('https://api.etherscan.io/api',
                     params={'module': 'gastracker',
                             'action': 'gasoracle',
                             'apikey': key})
    if r.status_code == 200:
        if verbose:
            print('200 OK')
        data = r.json().get('result')
        return int(data['FastGasPrice']), int(data['ProposeGasPrice']), int(data['SafeGasPrice'])
    else:
        if verbose:
            print(r.status_code)
        time.sleep(10)


def get_gas_from_gasnow(verbose: bool = False) -> Tuple[int, int, int]:
    """
    Fetch gas from Gasnow API
    """
    r = requests.get('https://www.gasnow.org/api/v3/gas/price')
    if r.status_code == 200:
        if verbose:
            print('200 OK')
        data = r.json()['data']
        return int(data['fast'] // 1e9), int(data['standard'] // 1e9), int(data['slow'] // 1e9)
    else:
        if verbose:
            print(r.status_code)
        time.sleep(10)


def get_gas_from_ethgasstation(key: str, verbose: bool = False):
    """
    Fetch gas from ETHGASSTATION API
    """
    r = requests.get('https://ethgasstation.info/api/ethgasAPI.json?', params={'api-key': key})
    if r.status_code == 200:
        if verbose:
            print('200 OK')
        data = r.json()
        return int(data['fastest'] / 10), int(data['fast'] / 10), int(data['average'] / 10), int(
            data['safeLow'] / 10), int(data['fastestWait'] * 60), int(data['fastWait'] * 60), int(
            data['avgWait'] * 60), int(data['safeLowWait'] * 60)
    else:
        if verbose:
            print(r.status_code)
        time.sleep(10)

def tokenPrice(token,config):
    #Coinmarketcap call
    coinurl = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    coinparameters = {
      'symbol':token,
      'convert':'USD'
    }
    coinheaders = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': config['coinmarketcapapi'],
    }
    session = Session()
    session.headers.update(coinheaders)
    try:
      response = session.get(coinurl, params=coinparameters).json()
      #print size of response
      print(response)
      
      data = response['data']
      ethdata=data[token]
      pricedata=ethdata['quote']
      usdprice=pricedata['USD']
      ethprice=usdprice['price']
      percentage_1h = usdprice['percent_change_1h']
      percentage_24h = usdprice['percent_change_24h']
      market_cap = data[token]['self_reported_market_cap']

      coinArray = {}
      coinArray['price'] = usdprice['price']
      coinArray['percentage_1h'] = percentage_1h
      coinArray['percentage_24h'] = percentage_24h
      coinArray['market_cap'] = market_cap


      print(usdprice['price'])
      #if USD price empty
      if usdprice['price'] == None:
        #coinmarketcap call faild, try dexscreener
        dexurl = "https://api.dexscreener.com/latest/dex/search/?q=:"+token+"%20SOL"
        dexresponse = requests.get(dexurl)
        dexresponse = dexresponse.json()
        for pair in dexresponse['pairs']:
          base_token_name = pair['baseToken']['name']
          quote_token_name = pair['quoteToken']['name']
          address = pair['pairAddress']
          chain_id = pair['chainId']
          percentage_5m = pair['priceChange']['m5']
          percentage_1h = pair['priceChange']['h1']
          percentage_6h = pair['priceChange']['h6']
          percentage_24h = pair['priceChange']['h24']
          market_cap = pair['fdv']
          price_usd = float(pair['priceUsd'])
          chart_link = f"https://dexscreener.com/{chain_id}/{address}"

          if base_token_name.lower() == token.lower():
              print(f"{base_token_name}/{quote_token_name} Price: ${price_usd:.5f} 5m: {percentage_5m:.2f}% 1h: {percentage_1h:.2f}% 6h: {percentage_6h:.2f}% 24h: {percentage_24h:.2f}% Market Cap: ${market_cap:.2f}")
              #array of all the data
              dexArray = {}
              dexArray['price'] = price_usd
              dexArray['percentage_5m'] = percentage_5m
              dexArray['percentage_1h'] = percentage_1h
              dexArray['percentage_6h'] = percentage_6h
              dexArray['percentage_24h'] = percentage_24h
              dexArray['market_cap'] = market_cap
              dexArray['base_token_name'] = base_token_name
              dexArray['quote_token_name'] = quote_token_name
              dexArray['address'] = address
              dexArray['chart_link'] = chart_link

              return dexArray
        
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e) 
    
    return coinArray


def main(source, verbose=False):
    # 1. Instantiate the bot
    # Allow the command prefix to be either ! or %
    description = """An example bot to showcase the discord.ext.commands extension
    module.

    There are a number of utility commands being showcased here."""

    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = False

    bot = commands.Bot(command_prefix="!", description=description, intents=intents, help_command=None)


        #various getters/setters
    def get_status(guildid):
        tup = c.execute("SELECT gamestatus FROM games WHERE guildid=?", (str(guildid),)).fetchone()
        # new guilds will return None so as not to crash
        if tup is None:
            return None
        return tup[0]

    def update_status(guildid, new_status):
        c.execute("UPDATE games SET gamestatus=? WHERE guildid=?", (new_status, str(guildid),))
        conn.commit()

    def get_answer(guildid):
        return c.execute("SELECT answer FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

    def update_answer(guildid, new_answer):
        c.execute("UPDATE games SET answer=? WHERE guildid=?", (new_answer, str(guildid),))
        conn.commit()

    def get_guesses(guildid):
        return c.execute("SELECT guesses FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

    def update_guesses(guildid, new_guesses):
        c.execute("UPDATE games SET guesses=? WHERE guildid=?", (new_guesses, str(guildid),))
        conn.commit()

    def get_charset(guildid):
        return c.execute("SELECT charset FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

    def update_charset(guildid, new_charset):
        c.execute("UPDATE games SET charset=? WHERE guildid=?", (new_charset, str(guildid),))
        conn.commit()

    def get_starttime(guildid):
        return c.execute("SELECT starttime FROM games WHERE guildid=?", (str(guildid),)).fetchone()[0]

    def update_starttime(guildid, new_starttime):
        c.execute("UPDATE games SET starttime=? WHERE guildid=?", (new_starttime, str(guildid),))
        conn.commit()

    @bot.command(name='hack')
    async def start_hack(ctx, *args):
        """
        Initiates a hacking game.
        Input: variable set of arguments.
        """
        guild = ctx.message.guild
        arg_attempt = 6
        # parse args (or just the one arg, anyway)
        if (len(args) > 0):
            try:
                arg_attempt = int(args[0])
                if arg_attempt < 4 or arg_attempt > 12:
                    raise ValueError
            except:
                await ctx.send("Number of turns must be a number between 4 and 12.")
                return
        # start the hacking process
        if get_status(guild) is None:
            c.execute("INSERT INTO games VALUES (?, ?, ?, ?, ?, ?)", (str(guild), 0, arg_attempt, "", "", 0))
            conn.commit()
        if not get_status(guild):
            char_list = "".join([string.ascii_letters,string.digits])
            # remove 0, O, l, I since their discord equivalents look too similar
            char_list.replace("l", "")
            char_list.replace("I", "")
            char_list.replace("0", "")
            char_list.replace("O", "")
            #get answer
            array = random.sample(char_list, 6)
            update_answer(guild, "".join(random.sample(array, 3)))
            char_response = ""
            update_guesses(guild, arg_attempt)
            for item in array:
                char_response = "".join([char_response, item])
            response = ("The available letters are: `{0}`\nYou have {1} guesses.").format(char_response, str(get_guesses(guild)))
            update_charset(guild, char_response)
            update_status(guild, True)
            update_starttime(guild, time.perf_counter())
            await ctx.send(response)
        else:
            await ctx.send("A game is already in progress!")

    @bot.command(name='quit')
    async def quit(ctx):
       """
       Quits the current game.
       """
       guild = ctx.message.guild
       if get_status(guild) == False:
           await ctx.send("No game is in progress!")
       else:
           await ctx.send("Game has been stopped. Answer was: `{0}`".format(get_answer(guild)))
           update_status(guild, False)
    
    @bot.event
    async def on_thread_join(thread):
        await thread.join()
        # print(thread.members)
        # botid = thread.get_member(892495224629231617)
        # if(botid == NULL):
        #     await thread.send("Im here!")

    @bot.event
    async def on_message(message):
        guild = message.guild
        #print(guild)
        #print(message.content)
        #tokenPrice

        if message.author != bot.user:
            if len((message.content.split(" ")[0])) <= 10 and message.content.startswith("$"):
                
                # if message.startswith("$") and len(message) <= 5:
            
                text = message
                text = text.content.split(" ")
                print(text)
                if(len(text)>1):
                    amount = text[1]
                else:
                    amount = 0  
                #remove command
                token = text[0]
                token = token.split("$")
                token = token[1]
                token = token.upper()
                print(token)
                #print(amount)

                # 2. Load config
                filename = 'config.yaml'
                with open(filename) as f:
                    config = yaml.load(f, Loader=yaml.Loader)

                price = tokenPrice(token,config)
                embed = discord.Embed(title=f"Current {token} price")
                
     
                if 'base_token_name' not in price:
                    embed.add_field(name=f"1 {token} = ", value=f"${price['price']}", inline=True) 
                
                if(amount!=0):
                    print(amount)
                    if 'base_token_name' not in price:
                        embed.add_field(name=f"{amount} {token} = ", value=f"${price['price']*float(amount)}", inline=True)
                #if usdprice array is not empty
                #if price is dict
                embed.add_field(name=f"1 {token} = ", value=f"${price['price']:.5f}", inline=True)
                if(amount!=0): 
                    embed.add_field(name=f"{amount} {token} = ", value=f"${price['price']*float(amount):.5f}", inline=True)
                if 'base_token_name' in price:    
                    embed.add_field(name=f"5m: ", value=f"{price['percentage_5m']:.2f}%", inline=True)
                embed.add_field(name=f"1h: ", value=f"{price['percentage_1h']:.2f}%", inline=True)
                if 'base_token_name' in price:
                    embed.add_field(name=f"6h: ", value=f"{price['percentage_6h']:.2f}%", inline=True)
                embed.add_field(name=f"24h: ", value=f"{price['percentage_24h']:.2f}%", inline=True)
                if price['market_cap'] != None:
                    embed.add_field(name=f"Market Cap: ", value=f"${price['market_cap']:.2f}", inline=True)
                if 'base_token_name' in price:
                    embed.add_field(name=f"Chart Link: ", value=f"{price['chart_link']}", inline=True)

                await message.channel.send(embed=embed)
            #else:
                #await message.channel.send("nope")

        #hacking game
        """
        Process the given message, check if it is three characters long, and compare it against the answer.
        """
        
        if message.author != bot.user:
            if get_status(guild) and len(message.content) == 3:
                correct = ""
                if message.content == get_answer(guild):
                    diff = time.perf_counter() - get_starttime(guild)
                    min = math.floor(diff/60)
                    sec = diff % 60
                    #Add win to database leaderboard
                    winner = message.author.id
                    #insert
                    guesses = str(get_guesses(guild))
                    #dbMed.insert({'meditationNum': 1, 'meditationUser': f'{meditationUser}', 'meditationChannel': f'{meditationChannel}'})
                    dbHackScore.insert({'User': f'{winner}', 'Guesses': f'{guesses}', 'time': f'{str(min)}:{int(sec)}'})
                    await message.channel.send("Correct!\nTime taken: {}:{:0>2d}".format(str(min), int(sec)))
                    update_status(guild, False)
                else:
                    charset = get_charset(guild)
                    for i in range(3):
                        char = message.content[i]
                        if charset.find(char) != -1:
                            for j in range(3):
                                if message.content[i] == get_answer(guild)[j]:
                                    if i == j:
                                        correct = "".join([correct, "!"])
                                    else:
                                        correct = "".join([correct, "?"])
                        else:
                            await message.channel.send("Invalid character(s)!")
                            return
                    update_guesses(guild, get_guesses(guild) - 1)
                    if get_guesses(guild) == 0:
                        await message.channel.send("You have run out of guesses. The answer was: `{0}`".format(get_answer(guild)))
                        update_status(guild, False)
                        return
                    correct = ("".join(sorted(correct)))[::-1] # reverse this string to fit with tachyons notation
                    await message.channel.send("**[{0}]**\nGuesses left: {1}".format(correct, str(get_guesses(guild))))
            await bot.process_commands(message)

    # @bot.event
    # async def on_message(message):

    #     openseaAssetURL = "https://opensea.io/assets"
    #     if openseaAssetURL in message.content:
    #         #pull URL only from message
    #         apiImageUrl = re.search("(?P<url>https?://[^\s]+)", message.content).group("url")
    #         imgURL = get_NFT_image(apiImageUrl)
    #         print(imgURL)
    #         #print(message.channel)
    #         await message.channel.send(f"{imgURL}")
    #     await bot.process_commands(message)

    @bot.command(name='p5js')
    async def p5js(ctx):
        message = ctx.message.content
        message = message.split("!p5js ")
        message = message[1]

        p5js_to_image(message)
        time.sleep(3)
        
        with open('result.png', 'rb') as f:
            picture = discord.File(f)
            await message.channel.send(file=picture)


    @bot.command(name='hackhelp')
    async def hackhelp(ctx):
        await ctx.send("""```Guess the correct 3-character answer from the provided 6 characters to win. Similar to Mastermind/Bulls and Cows/Wordle.
    - !hack: start a new game   
        - optional: number of turns, from 4 to 12
    - !quit: quits current game
    - !help: displays this message
    '?' - right character, wrong place
    '!' - right character, right place```""")

    @bot.command(pass_context=True, brief="Get Community map of our group !community {community id}")
    async def community(ctx):
        
        message = ctx.message.content
        community = message.split("!community ")
        community = community[1]


        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        # The ID and range of a sample spreadsheet.
        SAMPLE_SPREADSHEET_ID = '1a6xZ2LfJAYj9G3lY7VxdGkyS-rqmSYUzjyXonMUGYow'
        SAMPLE_RANGE_NAME = 'Data-Land!A2:D'

        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])

            if not values:
                print('No data found.')
                return

            
            #community = "36"
            link = "https://wolfland.live/"+community+"#"
            lastname = ""
            nextname = ""
            #print('Name, Major:')
            list = []
            for row in values:
                if row[3] == community:
                    list.append([row[0],row[2]])
            print(list)

            for index, row in enumerate(list):
                if index + 1 < len(list):
                    nextEle = list[index+1]
                    nextname = nextEle[0]

                name = row[0]
                landid = row[1]
                
                print("currentName" + name)
                print("nextName" + nextname)
                if name == lastname:
                    #beginbot=7195,7197,7196,7199,7198&Ravonus=7133
                    link = link +','+landid 
                else:
                    link = link + name +'='+landid
                if name != nextname and nextname !="":
                    link = link +"&" 
                lastname = name
                    #print(row[0])
                # Print columns A and E, which correspond to indices 0 and 4.
                #print('%s, %s' % (row[0], row[3]))
        except HttpError as err:
            print(err)
        
        #link = "complete"
        await ctx.send(link)

    @bot.command(pass_context=True, brief="Get live animal population of !pop {community id}")
    async def pop(ctx):
        message = ctx.message.content
        community = message.split("!pop ")
        community = community[1]

        embed = discord.Embed(title=f"Population of Community: {community}")

        url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"

        # store the response of URL
        response = urlopen(url)
  
        # storing the JSON response 
        # from url in data
        data_json = json.loads(response.read())

        data_json_as_string = dumps(data_json)
        wolfCount = data_json_as_string.count('"WOLF"')
        sheepCount = data_json_as_string.count('"SHEEP"')

        # print the json response
        #print(data_json)

        embed.add_field(name=f"Sheep :", value=f"{sheepCount}", inline=True)
        embed.add_field(name=f"Wolves :", value=f"{wolfCount}", inline=True)

        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get current weather of community !weather {community id}")
    async def weather(ctx):
        message = ctx.message.content
        community = message.split("!weather ")
        community = community[1]

        embed = discord.Embed(title=f"current {community} Weather: ")

        url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"

        # store the response of URL
        response = urlopen(url)
  
        # storing the JSON response 
        # from url in data
        data_json = json.loads(response.read())

        # print the json response
        #print(data_json)

        embed.add_field(name=f"Sheep :", value=f"{data_json['weather']}", inline=True)

        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get weather forecast of community !forecast {community id}")
    async def forecast(ctx):
        message = ctx.message.content
        community = message.split("!forecast ")
        community = community[1]

        embed = discord.Embed(title=f"{community} Weather Forecast: ")

        url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"

        # store the response of URL
        response = urlopen(url)
  
        # storing the JSON response 
        # from url in data
        data_json = json.loads(response.read())

        # print the json response
        #print(data_json)

        forecasts = data_json['forecast']

        for i in forecasts:
            date = i
            weather = forecasts[i]
            embed.add_field(name=f"{date}", value=f"{weather}", inline=True)

        await ctx.send(embed=embed) 


    @bot.command(pass_context=True, brief="Get the levels of a community !level {community id}")
    async def level(ctx):
        message = ctx.message.content
        community = message.split("!level ")
        community = community[1]

        embed = discord.Embed(title=f"{community} Resource Ranks: ")

        url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"

        # store the response of URL
        response = urlopen(url)
  
        # storing the JSON response 
        # from url in data
        data_json = json.loads(response.read())

        # print the json response
        #print(data_json)

        resourceRanks = data_json['resourceRanks']

        for i in resourceRanks:
            typeName = i['type']
            rank = i['currentRank']
            embed.add_field(name=f"{typeName}", value=f"{rank}", inline=True)

        await ctx.send(embed=embed) 

    @bot.command(pass_context=True, brief="Get structures and stats of said structures by community !structures {community id}")
    async def structures(ctx):
        message = ctx.message.content
        community = message.split("!structures ")
        community = community[1]

        embed = discord.Embed(title=f"{community} Structure Stats: ")

        url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"

        # store the response of URL
        response = urlopen(url)
  
        # storing the JSON response 
        # from url in data
        data_json = json.loads(response.read())

        # print the json response
        #print(data_json)

        lands = data_json['lands']

        for l in lands:
            if(l['buildingsAllowed'] == 1 and l['building'] != None):
                print(l['id'])
                print (l['building'])
                embed.add_field(name=f"Land Id: {l['id']}", value=f"Type: {l['building']['type']} , Cost: {l['building']['fee']} $WOOL, Closed?: {l['building']['closed']}", inline=True)

        await ctx.send(embed=embed)
    
    @bot.command(pass_context=True, brief="Check whos animal this is !sheep {sheep id}")
    async def sheep(ctx):
        message = ctx.message.content
        sheepId = message.split("!sheep ")
        sheepId = sheepId[1]

        url = f"https://opensea.io/assets/ethereum/0x7f36182dee28c45de6072a34d29855bae76dbe2f/{sheepId}"

        await ctx.send(url)

    @bot.command(pass_context=True, brief="Check whos animal this is !sheep {sheep id}")
    async def structureStats(ctx):
        denCount=0
        denCost = 0

        barnCount =0
        barnCost =0

        bathhouseCount = 0
        bathhouseCost = 0

        bathhousePeakCount =0
        bathhousePeakCost = 0

        for community in range (1,102):
            url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"

            # store the response of URL
            response = urlopen(url)
            # storing the JSON response 
            # from url in data
            data_json = json.loads(response.read())
            # print the json response
            #print(data_json
            lands = data_json['lands']

            for l in lands:
                if(l['buildingsAllowed'] == 1 and l['building'] != None):
                    #print(l['id'])
                    #print (l['building'])
                    #print(f"Land Id: {l['id']} , Type: {l['building']['type']} , Cost: {l['building']['fee']} $WOOL")
                    if l['building']['type'] == "DEN":
                        denCount +=1
                        denCost += l['building']['fee']
                    elif l['building']['type'] == "BATHHOUSE":
                        if community != 101:
                            bathhouseCount +=1
                            bathhouseCost += l['building']['fee']
                        else:
                            bathhousePeakCount +=1
                            bathhousePeakCost += l['building']['fee']                
                    elif l['building']['type'] == "BARN":
                        barnCount +=1
                        barnCost += l['building']['fee']
                    else:
                        print("oops")

        print(f"BARNS:{barnCount}  DENS:{denCount}  SHEEP BATH HOUSE COUNT:{bathhouseCount}   PEAK BATH HOUSE COUNT:{bathhousePeakCount}  TOTAL BATHHOUSES: {bathhousePeakCount+bathhouseCount}")

        print(f"BARN AVG COST:{barnCost/barnCount}")
        print(f"DEN AVG COST:{denCost/denCount}")
        print(f'BATHHOUSE AVG COST:{bathhouseCost/bathhouseCount}')
        print(f'BATHHOUSEPEAK AVG COST:{bathhousePeakCost/bathhousePeakCount}')

        embed = discord.Embed(title=f"Structure Stats")
        embed.add_field(name=f"Total Barns", value=f"{barnCount}", inline=True)
        embed.add_field(name=f"Total Dens", value=f"{denCount}", inline=True)
        embed.add_field(name=f"Total Sheep Bath Houses", value=f"{bathhouseCount}", inline=True)
        embed.add_field(name=f"Total Wolf Bath Houses", value=f"{bathhousePeakCount}", inline=True)
        embed.add_field(name=f"Total Bath Houses", value=f"{bathhousePeakCount + bathhouseCount}", inline=True)
        embed.add_field(name=f"Barn Avg Cost", value=f"{barnCost/barnCount}", inline=True)
        embed.add_field(name=f"Den Avg Cost", value=f"{denCost/denCount}", inline=True)
        embed.add_field(name=f"SHEEP BATHHOUSE AVG COST", value=f"{bathhouseCost/bathhouseCount}", inline=True)
        embed.add_field(name=f"PEAK BATHHOUSE AVG COST", value=f"{bathhousePeakCost/bathhousePeakCount}", inline=True)


        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get Den closed vs open stats")
    async def denStats(ctx):
        denCount=0
        denCost = 0
        community = 101
        denOpen = 0
        denClosed = 0
       
        url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"
        # store the response of URL
        response = urlopen(url)
        # storing the JSON response 
        # from url in data
        data_json = json.loads(response.read())
        # print the json response
        #print(data_json
        lands = data_json['lands']

        for l in lands:
            if(l['buildingsAllowed'] == 1 and l['building'] != None):
                #print(l['id'])
                #print (l['building'])
                #print(f"Land Id: {l['id']} , Type: {l['building']['type']} , Cost: {l['building']['fee']} $WOOL")
                if l['building']['type'] == "DEN":
                    denCount +=1
                    denCost += l['building']['fee']

                    if l['building']['closed'] == True:
                        denClosed +=1
                    else:
                        denOpen +=1                

        print(f"DEN AVG COST:{denCost/denCount}")
    

        embed = discord.Embed(title=f"Den Stats")
        
        embed.add_field(name=f"Total Dens", value=f"{denCount}", inline=True)
        embed.add_field(name=f"Den Avg Cost", value=f"{denCost/denCount}", inline=True)
        embed.add_field(name=f"Opens Dens", value=f"{denOpen}", inline=True)
        embed.add_field(name=f"Closed Dens", value=f"{denClosed}", inline=True)

        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Show meditation Leaderboard")
    async def meditatedScore(ctx):

        search = dbMed.all()
        #print(search)

        embed = discord.Embed(title=f"Meditation Leaderboard")

        for x in search:
            user = await bot.fetch_user(x['meditationUser'])
            embed.add_field(name=f"{user} :", value=f"{x['meditationNum']}", inline=True) 


        await ctx.send(embed=embed)
        

    @bot.command(pass_context=True, brief="Show hack Leaderboard")
    async def hackScore(ctx):

        search = dbHackScore.all()
        #print(search)

        embed = discord.Embed(title=f"Hack Leaderboard")

        for x in search:
            user = await bot.fetch_user(x['User'])
            embed.add_field(name=f"{user} :", value=f" Guesses: {x['Guesses']}", inline=True)
            embed.add_field(name=f"{user} :", value=f" Time: {x['time']}", inline=True) 


        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get Next Wolf Game Game")
    async def nextGame(ctx):
        
        response = open("peak-game.txt", "r")
        response = response.read()
        # Split the string by newlines to get individual lines
        lines = response.split('\n')

        # Initialize variables
        opt_in_start = None
        starts_at = None
        game = None
        levels = None

        # Iterate over each line and extract the values
        for line in lines:
            if line.startswith('game:'):
                game = line.split(': ')[1].strip()
            if game == "'None'":
                game = "No Game Scheduled"
                opt_in_start = "N/A"
                starts_at = "N/A"
                break
            elif line.startswith('optInStart:'):
                opt_in_start = line.split(': ')[1].strip()
                print(opt_in_start)
                opt_in_start = int(parse(opt_in_start).timestamp())
            elif line.startswith('startsAt:'):
                starts_at = line.split(': ')[1].strip()
                starts_at = int(parse(starts_at).timestamp())
            elif line.startswith('levels:'):
                levels = line.split(': ')[1].strip()

        message = f"Next game is {game} at <t:{starts_at}> and opt in starts at <t:{opt_in_start}> with open levels: {levels}"
        await ctx.send(message)    

    @bot.command(pass_context=True, brief="Get Next Wolf Game Game")
    async def nextWits(ctx):
        
        response = open("nextWolfWits.txt", "r")
        # Split the string by newlines to get individual lines
        response = response.read()
        lines = response.split('Next time for Wolfwits:')
        print(lines)

        # Initialize variables
        starts_at = lines[1]

        # Iterate over each line and extract the values
        #if starts at not N/A
      
        if starts_at == 'N/A':
            message = f"No wits game found."
        else:
            starts_at = int(parse(starts_at).timestamp())
            message = f"Next Wolf Wits game is at <t:{starts_at}> "

        await ctx.send(message) 
    
    @bot.command(pass_context=True, brief="Get Next Wolf Game Game")
    async def nextWall(ctx):

        response = open("nextWaterwall.txt", "r")
        response = response.read()
        # Split the string by newlines to get individual lines
        lines = response.split('Next time for Waterwall:')
        print(lines)

        # Initialize variables
        starts_at = lines[1]

        # Iterate over each line and extract the values
        #if starts at not N/A
      
        if starts_at == 'N/A':
            message = f"No Wall game found."
        else:
            starts_at = int(parse(starts_at).timestamp())
            message = f"Next Water Wall game is at <t:{starts_at}> "
            
        await ctx.send(message)

    
    @bot.command(pass_context=True, brief="Get Next Wolf Game Game")
    async def nextTug(ctx):

        response = open("nextTug.txt", "r")
        response = response.read()
        # Split the string by newlines to get individual lines
        lines = response.split('Next time for Tug:')
        print(lines)

        # Initialize variables
        starts_at = lines[1]

        # Iterate over each line and extract the values
        #if starts at not N/A
      
        if starts_at == 'N/A':
            message = f"No Tug game found."
        else:
            starts_at = int(parse(starts_at).timestamp())
            message = f"Next Tug game is at <t:{starts_at}> "
            
        await ctx.send(message) 

    @bot.command(pass_context=True, brief="Gets projects opensea Graph QL data")
    async def projectStats(ctx):
        message = ctx.message.content
        projectName = message.split("!projectStats ")
        projectName = projectName[1]
        projectName = projectName.replace(" ","-")
        projectName = projectName.lower()
        projectGraphUrl = "https://open-graph.opensea.io/v1/collections/"+projectName

        await ctx.send(projectGraphUrl)

    @bot.command(pass_context=True, brief="get list of servers bot is in")
    async def servers(ctx):
        servers = list(bot.guilds)
        await ctx.send(f"Connected on {str(len(servers))} servers:")
        await ctx.send('\n'.join(guild.name for guild in servers))

    @bot.command(pass_context=True, brief="random artmatt FB post")
    async def randomArtmatt(ctx):
        fbPost = random.choice(list(open('randomartmatt.txt')))
        await ctx.send(fbPost)


    @bot.command(pass_context=True, brief="Log meditations")
    async def meditated(ctx):
        message = ctx.message.content
        meditationUser = ctx.message.author.id
        meditationChannel = ctx.message.channel.id

        #print(ctx.message)
        embed = discord.Embed(title=":pray: Meditation Logged")
        embed.set_author(
            name='{0.display_name}'.format(ctx.author),
            icon_url='{0.avatar.url}'.format(ctx.author)
        )

        #search if user already there
        search = dbMed.search(where('meditationUser') == f'{meditationUser}')
        #if user not already in db
        if not search:
            #insert
            dbMed.insert({'meditationNum': 1, 'meditationUser': f'{meditationUser}', 'meditationChannel': f'{meditationChannel}'})
        else:
            currentMeditationCount = (search[0]['meditationNum'])
            newMedCount = int(currentMeditationCount) + 1
            #update 
            dbMed.remove(where('meditationUser') == f"{meditationUser}")
            dbMed.insert({'meditationNum': f'{newMedCount}', 'meditationUser': f'{meditationUser}', 'meditationChannel': f'{meditationChannel}'})
        #add to text file
        #file1 = open("gasPingLog.txt", "a")
        #file1.write(f"{gasNum} {gasUser} {gasChannel}\n")
        #file1.close()


        await ctx.send(embed=embed)

    # 2. Load config
    filename = 'config.yaml'
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.Loader)

    async def send_update(fastest, average, slow, **kw):
        status = f'⚡{fastest} |🐢{slow} | !help'
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name=status))
                                                            
        for guild in bot.guilds:
            guser = guild.get_member(bot.user.id)
            await guser.edit(nick=f'HelperBot|Gas:{average}')

        #print (f"{guild}")
        print (f"{average}")

        ##search db for gas notification
        notifyList = db.search((Query()['gasNum']) >= average)
        print(f"{notifyList}")

        #loop through notifyList post in discord tagging users of that gas number

        for results in notifyList:
            print(results)
            user = results['gasUser']
            channelid = results['gasChannel']
            gas = results['gasNum']

            channel = bot.get_channel(int(channelid))
            print(f"<@{user}>, Gwei is now {gas}")
           
            #delete from database
            #db.update(delete, Query()['gasUser'] == f"{user}")
            db.remove(where('gasUser') == f"{user}")
            #remove from LIST
            #notifyList.pop(idx)
            
            await channel.send(f"<@{user}>, Gwei is now {gas} or less.")



        await asyncio.sleep(config['updateFreq'])  # in seconds

    
    async def getPeakGame():

        #read local text file
       
        #read local text file peak-game.txt

        curr_response = open("peak-game.txt", "r")
        curr_response = curr_response.read()
        # Split the string by newlines to get individual lines
        curr_lines = curr_response.split('\n')

        # Initialize current variables
        curr_opt_in_start = None
        curr_starts_at = None
        curr_game = None
        curr_levels = None

        # Iterate over each line and extract the values
        for line in curr_lines:
            if line.startswith('game:'):
                curr_game = line.split(': ')[1].strip()
            if curr_game == "'None'":
                curr_curr_game = "No Game Scheduled"
                curr_opt_in_start = "N/A"
                curr_starts_at = "N/A"
                break
            elif line.startswith('optInStart:'):
                curr_opt_in_start = line.split(': ')[1].strip()
                curr_optTime = datetime.datetime.strptime(curr_opt_in_start, "%Y-%m-%dT%H:%M:%S.%fZ")
                curr_optTime = curr_optTime.strftime("%H:%M")
                #print(opt_in_start)
                curr_opt_in_start = int(parse(curr_opt_in_start).timestamp())
            elif line.startswith('startsAt:'):
                curr_starts_at = line.split(': ')[1].strip()
                curr_startTime  = datetime.datetime.strptime(curr_starts_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                curr_startTime = curr_startTime.strftime("%H:%M")
                curr_starts_at = int(parse(curr_starts_at).timestamp())
            elif line.startswith('levels:'):
                curr_levels = line.split(': ')[1].strip()

        urlPrevious = open("peak-game-previous.txt", "r")
        urlPrevious = urlPrevious.read()

        # Split the string by newlines to get individual lines
        pre_lines = urlPrevious.split('\n')
    
        #Initialize previous variables
        pre_opt_in_start = None
        pre_starts_at = None
        pre_game = None
        pre_levels = None
        pre_optTime = None
        pre_startTime = None

        for line in pre_lines:
            if line.startswith('game:'):
                pre_game = line.split(': ')[1].strip()
            if pre_game == "'None'":
                pre_game = "No Game Scheduled"
                pre_opt_in_start = "N/A"
                pre_starts_at = "N/A"
                break
            elif line.startswith('optInStart:'):
                pre_opt_in_start = line.split(': ')[1].strip()
                pre_optTime = datetime.datetime.strptime(pre_opt_in_start, "%Y-%m-%dT%H:%M:%S.%fZ")
                pre_optTime = pre_optTime.strftime("%H:%M")
                #print(opt_in_start)
                pre_opt_in_start = int(parse(pre_opt_in_start).timestamp())
            elif line.startswith('startsAt:'):
                pre_starts_at = line.split(': ')[1].strip()
                pre_startTime  = datetime.datetime.strptime(pre_starts_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                pre_startTime = pre_startTime.strftime("%H:%M")
                pre_starts_at = int(parse(pre_starts_at).timestamp())
            elif line.startswith('levels:'):
                pre_levels = line.split(': ')[1].strip()

        #switch case on game
        if curr_game == "WOLF_WITS":
            #alertRole = 1149156059131424888
            curr_alertRole = 1149152050391822336
        elif curr_game == "WATER_WALL":
            #alertRole = 1149168100168704120
            curr_alertRole = 1149151491211411567
        elif curr_game == "TUG_OF_WOOL":
            #alertRole = 1149168129507872769
            curr_alertRole = 1149152166586626128
        else:
            curr_alertRole = ""

         #switch case on game
        if pre_game == "WOLF_WITS":
            #alertRole = 1149156059131424888
            pre_alertRole = 1149152050391822336
        elif pre_game == "WATER_WALL":
            #alertRole = 1149168100168704120
            pre_alertRole = 1149151491211411567
        elif pre_game == "TUG_OF_WOOL":
            #alertRole = 1149168129507872769
            pre_alertRole = 1149152166586626128
        else:
            pre_alertRole = ""
           
               
        if curr_alertRole != "" or pre_alertRole != "":

            #send to irlalpha wolf-game channel
            channel = bot.get_channel(969249236464050187)
            #test channel
            #channel = bot.get_channel(1081472865360171090)

            print(f'CUR OPT TIME {curr_optTime}')
            print(f'CUR START TIME {curr_startTime}')

            print(f'PRE OPT TIME {pre_optTime}')
            print(f'PRE START TIME {pre_startTime}')

            # Get the current time as a datetime object
            current_time = datetime.datetime.utcnow()
            #current_time = current_time + datetime.timedelta(hours=1)
            # get just hrs and mins
            current_time_str = current_time.strftime("%H:%M")
            print(current_time_str)

            # Define the start and end times (8 am and 2 pm) in UTC
            noPingStart = datetime.time(8, 0)
            noPingEnd = datetime.time(14, 0)

            #no ping 
            if  noPingStart <= current_time.time() < noPingEnd:
                if current_time_str == curr_optTime:
                    message = f"OPT FOR {curr_game} NOW <t:{curr_opt_in_start}> with open levels: {curr_levels} the game starts at <t:{curr_starts_at}>"
                    print (message)
                    await channel.send(message, delete_after=600)
                if current_time_str == pre_startTime:
                    message = f"A new round of {curr_game} has been created! The game begins at <t:{curr_starts_at}> and opt in starts at <t:{curr_opt_in_start}> with open levels: {curr_levels}"
                    print (message)
                    await channel.send(message, delete_after=7200)
            #ping
            else:
                if current_time_str == curr_optTime:
                    message = f"OPT FOR <@&{curr_alertRole}> NOW <t:{curr_opt_in_start}> with open levels: {curr_levels} the game starts at <t:{curr_starts_at}>"
                    print (message)
                    await channel.send(message, delete_after=600)
                if current_time_str == pre_startTime:
                    message = f"A new round of {curr_game} has been created! The game begins at <t:{curr_starts_at}> and opt in starts at <t:{curr_opt_in_start}> with open levels: {curr_levels}"
                    print (message)
                    await channel.send(message, delete_after=7200)
                

        peakHrs = 40
        #peakHrs = (config['peakFreq'] * 60) *60
        await asyncio.sleep(peakHrs)  # in seconds
       


    @bot.command(pass_context=True, brief="Get APE price")
    async def ape(ctx):
        price = tokenPrice('APE',config)
        embed = discord.Embed(title="<:apecoin:954387364824899665> Current APE price")
        embed.add_field(name=f"1 $APE = ", value=f"${price}", inline=True) 
    
        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get WOOL price")
    async def wool(ctx):
        price = tokenPrice('WOOL',config)
        embed = discord.Embed(title=":sheep: Current wool price")
        embed.add_field(name=f"1 $WOOL = ", value=f"${price}", inline=True) 
    
        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get CFTI price")
    async def cfti(ctx):
        price = tokenPrice('CFTI',config)
        embed = discord.Embed(title="<:raidparty:939195769024557186> Current CFTI price")
        embed.add_field(name=f"1 $CFTI = ", value=f"${price}", inline=True) 
    
        await ctx.send(embed=embed)


    @bot.command(pass_context=True, brief="Get LOOKS price")
    async def looks(ctx):
        price = tokenPrice('LOOKS',config)
        embed = discord.Embed(title=":eyes: Current LOOKS price")
        embed.add_field(name=f"1 LOOKS = ", value=f"${price}", inline=True) 
    
        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get custom Token price")
    async def customToken(ctx):
        message = ctx.message.content
    
        #trim end off
        trimmed = message.rstrip()
        #remove command
        token = trimmed.split("!customToken ")
        token = token[1]
        token = token.upper()
        print(token)

        price = tokenPrice(token,config)
        embed = discord.Embed(title=f"Current {token} price")
        embed.add_field(name=f"1 {token} = ", value=f"${price}", inline=True)

    
        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get ETH gas prices")
    async def gas(ctx):
        #print(vars(ctx))
        embed = discord.Embed(title=":fuelpump: Current gas prices")
        if source == 'ethgasstation':
            fastest, fast, average, slow, fastestWait, fastWait, avgWait, slowWait = get_gas_from_ethgasstation(
                config['ethgasstationKey'],
                verbose=verbose)
            embed.add_field(name=f"Slow :turtle: | {slowWait} seconds", value=f"{round(float(slow), 1)} Gwei",
                            inline=True)
            embed.add_field(name=f"Average :person_walking: | {avgWait} seconds",
                            value=f"{round(float(average), 1)} Gwei", inline=True)
            embed.add_field(name=f"Fast :race_car: | {fastWait} seconds", value=f"{round(float(fast), 1)} Gwei",
                            inline=True)
            embed.add_field(name=f"Quick :zap: | {fastestWait} seconds", value=f"{round(float(fastest), 1)} Gwei",
                            inline=True)
        else:
            if source == 'etherscan':
                fast, average, slow = get_gas_from_etherscan(config['etherscanKey'], verbose=verbose)
            else:
                fast, average, slow = get_gas_from_gasnow(verbose=verbose)
            embed.add_field(name=f"Slow :turtle:", value=f"{slow} Gwei", inline=True)
            embed.add_field(name=f"Average :person_walking:", value=f"{average} Gwei", inline=True)
            embed.add_field(name=f"Fast :zap:", value=f"{fast} Gwei", inline=True)
        embed.set_footer(text=f"Fetched from {source}\nUse help to get the list of commands")
        embed.set_author(name='{0.display_name}'.format(ctx.author),
            icon_url='{0.avatar.url}'.format(ctx.author)
        )
        
        await ctx.send(embed=embed)

    @bot.command(pass_context=True, brief="Get the cost for each tx type")
    async def fees(ctx):
        calculate_eth_tx = lambda gwei, limit: round(gwei * limit * 0.000000001, 4)
        fast, standard, slow = get_gas_from_gasnow(verbose=verbose)
        eth_price = \
            requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd').json()[
                'ethereum'][
                'usd']
        simple_tx_fee_eth = calculate_eth_tx(fast, 21000)
        simple_tx_fee_usd = round(simple_tx_fee_eth * eth_price, 2)
        token_approve_eth = calculate_eth_tx(fast, 51000)
        token_approve_usd = round(token_approve_eth * eth_price, 2)
        token_transfer_eth = calculate_eth_tx(fast, 48000)
        token_transfer_usd = round(token_transfer_eth * eth_price, 2)
        range1_uniswap_eth = calculate_eth_tx(fast, 120000)
        range1_uniswap_usd = round(range1_uniswap_eth * eth_price, 2)
        range2_uniswap_eth = calculate_eth_tx(fast, 200000)
        range2_uniswap_usd = round(range2_uniswap_eth * eth_price, 2)
        fees_eth = f"**Fast: {fast}** **Standard: {standard}** **Slow: {slow}**\n"\
                   f"Simple ETH TX: **${simple_tx_fee_usd}** ({simple_tx_fee_eth} Ξ)\n" \
                   f"Token Approval (ERC20): **${token_approve_usd}** ({token_approve_eth} Ξ)\n" \
                   f"Token Transfer (ERC20): **${token_transfer_usd}** ({token_transfer_eth} Ξ)\n" \
                   f"Uniswap Trades: **${range1_uniswap_usd} - ${range2_uniswap_usd}** ({range1_uniswap_eth} Ξ - {range2_uniswap_eth} Ξ)\n"

        await ctx.send(fees_eth)

    @bot.command(pass_context=True, brief="Get list of commands")
    async def help(ctx, args=None):
        help_embed = discord.Embed(
            title="Gas Tracker",
            colour=discord.Colour.from_rgb(206, 17, 38))
        help_embed.set_author(
            name='{0.display_name}'.format(ctx.author),
            icon_url='{0.avatar.url}'.format(ctx.author)
        )
        command_list = [x for x in bot.commands if not x.hidden]

        def sortCommands(value):
            return value.name

        command_list.sort(key=sortCommands)
        if not args:
            help_embed.add_field(
                name="Command Prefix",
                value="`!`",
                inline=True)
            help_embed.add_field(
                name="List of supported commands:",
                value="```" + "\n".join(['{:>2}. {:<14}{}'.format(str(i + 1), x.name, x.brief) for i, x in
                                         enumerate(command_list)]) + "```",
                inline=True
            )
        else:
            help_embed.add_field(
                name="Nope.",
                value="Don't think I got that command, boss."
            )

        help_embed.set_footer(text="For any inquiries, suggestions, or bug reports, get in touch with @Zanuss#1483")
        await ctx.send(embed=help_embed)


    @bot.command(pass_context=True, brief="Generates new 10k inspiration")
    async def new10k(ctx):
        
        message = ctx.message.content

        #trim end off
        trimmed = message.rstrip()
        #remove command
        arg = trimmed.split("!new10k ")
        print(arg)
        try:
            arg = arg[1]
        except IndexError:
            arg = ""
        
        #fetch_adj_or_animal(type, aliteration, animal)

        if arg == "-a":
            animal = fetch_adj_or_animal("animal", False, False)
            adj = fetch_adj_or_animal("adjective", True, animal)
        else:
            animal = fetch_adj_or_animal("animal", False, False)
            adj = fetch_adj_or_animal("adjective", False, animal)
        
        
        gis = GoogleImagesSearch(config['gkey'], config['gcs_cx'])

        _search_params = {
        'q': f'{animal} animal',
        'num': 1,
        'fileType': 'png',
        'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived'
        }

        gis.search(search_params=_search_params)
        r = gis.results()   

        output10k = f"{adj} {animal}'s {gis.results()[0].url}"

        await ctx.send(output10k)

    @bot.command(pass_context=True, brief="Get alerted of a specific gas amount !gasping 10")
    async def gasping(ctx):
        
        message = ctx.message.content

        #trim end off
        trimmed = message.rstrip()
        #remove command
        gasNum  = trimmed.split("!gasping ")
        print (gasNum)
        if int(gasNum[1]) >= 0:
            gasNum = int(gasNum[1])
            gasUser = ctx.message.author.id
            gasChannel = ctx.message.channel.id

            #print(ctx.message)

            embed = discord.Embed(title=":fuelpump: GasPing Logged")

            fast, average, slow = get_gas_from_etherscan(config['etherscanKey'],verbose=verbose)
            embed.add_field(name=f"I'll let you know when it hits ", value=f"{gasNum} Gwei", inline=True)
            embed.set_footer(text=f"Fetched from {source}\nUse help to get the list of commands")
            embed.set_author(
                name='{0.display_name}'.format(ctx.author),
                icon_url='{0.avatar.url}'.format(ctx.author)
            )

        
            print(f"Gas watch: {gasNum}")
            print(f"Gas User: {gasUser}")

            #search if user already there
            search = db.search(where('gasUser') == f'{gasUser}')

            #if user not already in db
            if not search:
                #insert
                db.insert({'gasNum': gasNum, 'gasUser': f'{gasUser}', 'gasChannel': f'{gasChannel}'})
            else:
                #update 
                db.remove(where('gasUser') == f"{gasUser}")
                db.insert({'gasNum': gasNum, 'gasUser': f'{gasUser}', 'gasChannel': f'{gasChannel}'})

            #add to text file
            #file1 = open("gasPingLog.txt", "a")
            #file1.write(f"{gasNum} {gasUser} {gasChannel}\n")
            #file1.close()


            await ctx.send(embed=embed)
        elif gasNum[1] != None:
            await ctx.send("please provide a gas value greater than or equal to 0 ```!gasing 100```")
        else:
            await ctx.send("STFU stupac")
            

    # 2. Load config
    filename = 'config.yaml'
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.Loader)

    async def send_update(fastest, average, slow, **kw):
        status = f'⚡{fastest} |🐢{slow} | !help'
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name=status))
                                                            
        for guild in bot.guilds:
            guser = guild.get_member(bot.user.id)
            await guser.edit(nick=f'HelperBot|Gas:{average}')

        #print (f"{guild}")
        print (f"{average}")

        ##search db for gas notification
        notifyList = db.search((Query()['gasNum']) >= average)
        print(f"{notifyList}")

        #loop through notifyList post in discord tagging users of that gas number

        for results in notifyList:
            print(results)
            user = results['gasUser']
            channelid = results['gasChannel']
            gas = results['gasNum']

            channel = bot.get_channel(int(channelid))
            print(f"<@{user}>, Gwei is now {gas}")
           
            #delete from database
            #db.update(delete, Query()['gasUser'] == f"{user}")
            db.remove(where('gasUser') == f"{user}")
            #remove from LIST
            #notifyList.pop(idx)
            
            await channel.send(f"<@{user}>, Gwei is now {gas} or less.")



        await asyncio.sleep(config['updateFreq'])  # in seconds



    @bot.event
    async def on_ready():

        messageSent = False

        """
        When discord client is ready
        """
        while True:
            # 3. Fetch gas
            try:
                if source == 'etherscan':
                    gweiList = get_gas_from_etherscan(config['etherscanKey'],
                                                      verbose=verbose)
                elif source == 'gasnow':
                    gweiList = get_gas_from_gasnow(verbose=verbose)
                elif source == 'ethgasstation':
                    gweiList = get_gas_from_ethgasstation(config['ethgasstationKey'])
                    await send_update(gweiList[0], gweiList[2], gweiList[3])
                    continue
                else:
                    raise NotImplemented('Unsupported source')
                # 4. Feed it to the bot
                await send_update(*gweiList)
                
            except Exception as exc:
                logger.error(exc)
                continue    
            
            await getPeakGame()
            

    bot.run(config['discordBotKey'])


if __name__ == '__main__':
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source',
                        choices=['etherscan', 'gasnow', 'ethgasstation'],
                        default='etherscan',
                        help='select API')

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='toggle verbose')
    args = parser.parse_args()
    main(source=args.source,
         verbose=args.verbose)
