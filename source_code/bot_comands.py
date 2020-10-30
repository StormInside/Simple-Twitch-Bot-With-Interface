from twitchio.ext import commands

import sys
# import vlc
import asyncio
import requests
import json

from datetime import datetime
from dateutil.parser import parse
from playsound import playsound

with open('temp.txt', 'w', encoding="utf-8") as f:
    f.write("")

def log(text):
    with open('temp.txt', 'a+', encoding="utf-8") as f:
        f.write("\n"+datetime.now().strftime("%H:%M")+" --> "+str(text)+"\n")

with open('bot_config.json', 'r', encoding="utf-8") as f:

    data = json.load(f)

    IRC_TOKEN = data["IRC_TOKEN"]
    CLIENT_ID = data["CLIENT_ID"]
    SECRET_TOKEN = data["SECRET_TOKEN"]
    ACCESS_TOKEN = data["ACCESS_TOKEN"]
    INITIAL_CHANELS = data["INITIAL_CHANELS"]
    SOUND_LOCATION = data["SOUND_LOCATION"]
    MESSAGE_SOUND_NAME = data["MESSAGE_SOUND_NAME"]
    MESSAGE_SOUND_BLACKLIST = data["MESSAGE_SOUND_BLACKLIST"]
    MUSIC_MESSAGE_TIMEOUT = int(data["MUSIC_MESSAGE_TIMEOUT"])
    MUSIC_MESSAGE_TEXT = data["MUSIC_MESSAGE_TEXT"]
    MUSIC_COMMANDS = data["MUSIC_COMMANDS"]
    MESSAGE_SOUND = bool(data["MESSAGE_SOUND"])
    MUSIC_MESSAGE = bool(data["MUSIC_MESSAGE"])
    FOLLOW_COMMANDS = data["FOLLOW_COMMANDS"]
    CLIP_COMMANDS = data["CLIP_COMMANDS"]


class Player():

    def __init__(self, soundLocation):

        self.soundLocation = soundLocation

    def play_sound(self, sound):
        sound = self.soundLocation+"/"+sound#+".wav"
        # vlc.MediaPlayer(sound).play()
        try:
            playsound(sound)
        except Exception as ex:
            print(f"Error playing sound, probably uncorrect sound location or name\n{ex}")
            log(f"Error playing sound, probably uncorrect sound location or name\n{ex}")

class Bot(commands.Bot):

    def __init__(self):
            super().__init__(irc_token=IRC_TOKEN, 
                            prefix='!',
                            client_id= CLIENT_ID,
                            nick = INITIAL_CHANELS[0],
                            initial_channels=INITIAL_CHANELS
                            )
            self.player = Player(SOUND_LOCATION)
            self.client_id = CLIENT_ID
            self.CHANELS_BLACKLIST = MESSAGE_SOUND_BLACKLIST
            self.CHANELS_BLACKLIST.append(self.nick)
            self.total_followers = 0
            self.last_follow = None
            self.ctx = None
            # self.last_follow = parse('2020-9-1T13:35:07Z')
            print(f"Blacklist:\n{self.CHANELS_BLACKLIST}")
            log(f"Blacklist:\n{self.CHANELS_BLACKLIST}")

    
    
    async def event_ready(self):

        print(f'Ready | {self.nick}')
        log(f'Ready | {self.nick}')
        self.user_id = await self._get_user_id(INITIAL_CHANELS[0])
        # await self.follow_cahnnel("ozmakate")
        await self.runner()


    async def runner(self):

        t = 150

        while True:
            
            if MUSIC_MESSAGE and t >= MUSIC_MESSAGE_TIMEOUT:
                t = 0
                await self.send_message(MUSIC_MESSAGE_TEXT)

            await self._get_followers()

            t+=1
            await asyncio.sleep(0.5)

    async def event_message(self, message):
        t = True
        for n in self.CHANELS_BLACKLIST:
            if n.lower() == message.author.name:
                t = False
        if t:
            # print(message.author.name)
            # print(self.CHANELS_BLACKLIST)
            print(f'{message.author.name} -> {message.content}')
            log(f'{message.author.name} -> {message.content}')
            if MESSAGE_SOUND:
                self.player.play_sound(MESSAGE_SOUND_NAME)
                
        await self.handle_commands(message)

    @commands.command(name="start")
    async def start(self, ctx):
        self.ctx = ctx
        await ctx.send("Started")

    @commands.command(name=MUSIC_COMMANDS[0], aliases=MUSIC_COMMANDS[1:])
    async def music(self, ctx):
        self.ctx = ctx
        await ctx.send(MUSIC_MESSAGE_TEXT)

    @commands.command(name=FOLLOW_COMMANDS[0], aliases=FOLLOW_COMMANDS[1:])
    async def fff(self, ctx):
        self.ctx = ctx
        if await self._check_follow(ctx.author.name):

            await self.follow_channel(ctx.author.name)
        else:
            await ctx.send("You are not followed to my chanel!")


    @commands.command(name=CLIP_COMMANDS[0], aliases=CLIP_COMMANDS[1:])
    async def clip(self, ctx):
        self.ctx = ctx

        token = ACCESS_TOKEN

        headers={'Authorization': f'Bearer {token}',
                    'client-id': self.client_id}


        r = requests.post(f'https://api.twitch.tv/helix/clips?broadcaster_id={self.user_id}', headers=headers)

        if r.status_code == 202:
            url = r.json()["data"][0]["edit_url"]
            await self.send_message(f"Successful created clip : {url}")

        else:
            print("Failed to create clip \n"+ r.text)
            log("Failed to create clip \n"+ r.text)


    async def follow_channel(self, username):

        token = ACCESS_TOKEN

        headers={'Accept': 'application/vnd.twitchtv.v5+json',
                'client-id': self.client_id,
                'Authorization': f"Bearer {token}",
                "notifications": "true"}


        r = requests.post(f'https://api.twitch.tv/helix/users/follows', data={
                                                                            "to_id": await self._get_user_id(username),
                                                                            "from_id":self.user_id,
                                                                            "allow_notifications":"true"
                                                                            }, headers=headers)

        if r.status_code == 204:

            await self.send_message(f"Successful followed cahnnel : {username}")

        else:
            print("Failed to follow \n"+ r.text)
            log("Failed to follow \n"+ r.text)

    async def send_message(self, message):
        if self.ctx:
            await self.ctx.send(message)
        else:
            print("You need to init bot by <!start> command")
            log("You need to init bot by <!start> command")

    async def _get_followers(self):

        r = requests.post("https://id.twitch.tv/oauth2/token", data={"client_id":self.client_id,
                                                                     "client_secret":SECRET_TOKEN,
                                                                     "grant_type":"client_credentials"})
        if r.status_code == 200:                                                             

            token = r.json()['access_token']

            headers={'client-id': self.client_id,
                    'Accept': 'application/vnd.twitchtv.v5+json',
                    'Authorization': f'Bearer {token}'}

            r = requests.get(f'https://api.twitch.tv/helix/users/follows?to_id={self.user_id}', headers=headers)

            if r.status_code == 200:
                _json = r.json()
                total_followers = _json['total']
                las_follow_index = None

                for i in range(total_followers):

                    last_follow_date = parse(_json["data"][i]["followed_at"])

                    if not self.last_follow:
                        self.last_follow = last_follow_date
                        break
                    elif self.last_follow < last_follow_date and self.last_follow >= parse(_json["data"][i+1]["followed_at"]):
                        las_follow_index = i
                        # print(las_follow_index)
                    elif self.last_follow >= last_follow_date:
                        break  
                    else:
                        pass
                
                if las_follow_index or las_follow_index == 0:
                    for i in range(las_follow_index + 1, 0, -1):
                        # print(i-1)
                        last_follow_date = parse(_json["data"][i-1]["followed_at"])
                        self.last_follow = last_follow_date
                        print(f"New Follower!!! // {_json['data'][i-1]['from_name']} //")
                        log(f"New Follower!!! // {_json['data'][i-1]['from_name']} //")
                        await self.send_message(f"{_json['data'][i-1]['from_name']} Thank You For Follow!!!")
                        self.player.play_sound(MESSAGE_SOUND_NAME)


                # with open('data.json', 'w') as f:
                #     json.dump(r.json(), f)
            else:
                print("Failed to get followers \n"+ r.text)
                log("Failed to get followers \n"+ r.text)
        else:
            print("Failed to get Access Token \n"+ r.text)
            log("Failed to get Access Token \n"+ r.text)
    # await self._check_follow("ksusha_sama")
    async def _check_follow(self, username):
        

        r = requests.post("https://id.twitch.tv/oauth2/token", data={"client_id":self.client_id,
                                                                    'Accept': 'application/vnd.twitchtv.v5+json',
                                                                     "client_secret":SECRET_TOKEN,
                                                                     "grant_type":"client_credentials"})

        if r.status_code == 200:                                                             

            token = r.json()['access_token']

            headers={'client-id': self.client_id,
                    'Accept': 'application/vnd.twitchtv.v5+json',
                    'Authorization': f'Bearer {token}'}


            to_id = await self._get_user_id(username)
            
            r = requests.get(f'https://api.twitch.tv/kraken/users/{to_id}/follows/channels/{self.user_id}', headers=headers)# 39154778

            if r.status_code == 200:

                return True
            elif r.status_code == 404 and r.json()["message"] == "Follow not found":

                return False
            else:
                print("Failed to get info \n"+ r.text)
                log("Failed to get info \n"+ r.text)
        else:
            print("Failed to get Access Token \n"+ r.text)
            log("Failed to get Access Token \n"+ r.text)

    async def _get_user_id(self, username):
        r = requests.post("https://id.twitch.tv/oauth2/token", data={"client_id":self.client_id,
                                                                     "client_secret":SECRET_TOKEN,
                                                                     "grant_type":"client_credentials"})
        
        if r.status_code == 200:
            token = r.json()['access_token']

            headers={'client-id': self.client_id,
                        'Accept': 'application/vnd.twitchtv.v5+json',
                        'Authorization': f'Bearer {token}'}

            r = requests.get(f'https://api.twitch.tv/kraken/users?login={username}', headers=headers)

            if r.status_code == 200:
                if len(r.json()["users"])>0:
                    user_id = r.json()["users"][0]["_id"]
                    return(user_id)
                else:
                    print("No such user ", username)
                    log("No such user ", username)
            else:
                print("Failed to get User Id \n"+ r.text)
                log("Failed to get User Id \n"+ r.text)
        else:
            print("Failed to get Access Token \n"+ r.text)
            log("Failed to get Access Token \n"+ r.text)

def start_bot(loop):
    
    asyncio.set_event_loop(loop)
    Bot().run()


if __name__ == "__main__":
    Bot().run()
    
# https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<client_id>&redirect_uri=http://localhost&scope=clips:edit user:edit:follows