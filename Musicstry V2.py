#IMPORTING MODULES

print("--------------------IMPORTING MODULES--------------------")

import discord
import json
import os
import requests
import lyricsgenius as genius
from discord.ext import commands
from mutagen.easyid3 import EasyID3

print("Modules Imported\n")

#GET SECRETS

with open("secrets.json", "rb") as file:
    secrets = json.read(file)
    print("Loaded Secrets\n")

#CONNECTING TO SERVICES

client = commands.Bot(command_prefix = "-")

print("--------------------CONNECTING TO GENIUS--------------------")

api = genius.Genius(secrets['genius'])

print("Connected To Genuis API\n")

#MUSIC CLASS

class Music():
    def __init__(self):
        self.Banned_Words = ["ass", "bastard", "bellend", "bollocks", "bitch", "cock", "cunt", "dick", "fuck", "knob", "piss", "prick", "pussy", "shag", "shit", "tits", "twat", "wanker"]
        self.FalsePositives = ["massive", "glass", "grass", "glasses", "passed", "passing", "assisted", "assembly", "passion", "passions", "class", "pass", "massi", "assigned", "bass", "classy", "passport", "embarrassed"]
        self.SongName = self.Artist = self.SpotifyUrl = self.DeezerUrl = ""
        self.CheckResults = {}
        self.Lyrics = {}

    def CheckLyrics(self, SongName, Artist):
        self.SongName = str(SongName)
        self.Artist = str(Artist)
        if self.SongName.startswith("https://open.spotify.com/track/"):
            self.GetSpotify()
            self.GetDeezer()
        else:
            self.GetDeezer()
            self.GetSpotify()
        self.GetGenius()
        self.GetApiSeeds()
        self.GetChartLyrics()
        self.GetLoloLyrics()
        self.GetCajunLyrics()
        for Source in self.Lyrics.keys():
            self.LyricsCheck(Source)

    def LyricsCheck(self, Source):
        self.CheckResults[Source] = []
        Clean = True
        for lyric in self.Lyrics[Source]:
            for word in self.Banned_Words:
                A = str(lyric.lower()).find(word)
                if A != -1:
                    Clean = False
                    B = lyric.split(" ")
                    BadSentence = []
                    Bad = False
                    for lyric in B:
                        BadWord = False
                        for word in self.Banned_Words:
                            C = str(lyric.lower()).find(word)
                            if C != -1:
                                lyric = lyric.replace(",", "").replace("'", "").replace(":", "").replace(";", "")
                                if not(str(lyric.lower()) in self.FalsePositives):
                                    Bad = True
                                    BadWord = True
                        if BadWord:
                            BadSentence.append("**"+lyric+"**")
                        else:
                            BadSentence.append(lyric)
                    if Bad:
                        BadSentence = " ".join(BadSentence)
                        if not(BadSentence in self.CheckResults[Source]):
                            self.CheckResults[Source].append(BadSentence)
                    else:
                        Clean = True
        if Clean:
            self.CheckResults[Source] = ["Clean"]

    def GetSpotify(self):
        data = {'grant_type': 'client_credentials', 'redirect_uri': 'http://localhost/', 'client_id': "710b5d6211ee479bb370e289ed1cda3d", 'client_secret': secrets['spotify']}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        Data = requests.post("https://accounts.spotify.com/api/token", data, headers).json()
        Token = Data['access_token']
        if self.SongName.startswith("https://open.spotify.com/track/"):
            ID = self.SongName.split("https://open.spotify.com/track/")
            ID = ID[1].split("?si=")
            Data = requests.get('https://api.spotify.com/v1/tracks/'+str(ID[0]), headers={ 'authorization': "Bearer "+Token }).json()
        else:  
            Data = requests.get('https://api.spotify.com/v1/search', headers={ 'authorization': "Bearer "+Token }, params={ 'q': self.Artist+" - "+self.SongName, 'type': 'track', 'limit': "1" }).json()
            Data = Data['tracks']['items']
            if Data != []:
                Data = Data[0]
        if Data != []:
            FoundArtist = Data['artists'][0]['name']
            FoundSong = Data['name'].replace(" - Radio Edit", "")
            if self.SongName.startswith("https://open.spotify.com/track/"):
                self.SongName = str(FoundSong)
                self.Artist = str(FoundArtist)
            if str(FoundArtist).lower() == self.Artist.lower() and str(FoundSong).lower() == self.SongName.lower():
                self.SpotifyUrl = Data['external_urls']['spotify']
                if str(Data['explicit']) == "True":
                    self.CheckResults['Spotify'] = ['Explicit Content Found']
                else:
                    self.CheckResults['Spotify'] = ['Clean']
            else:
                self.CheckResults['Spotify'] = ["Song Not Found"]
        else:
            self.CheckResults['Spotify'] = ["Song Not Found"]

    def GetDeezer(self):
        if self.SongName.startswith("https://www.deezer.com/track/"):
            ID = self.SongName.split("https://www.deezer.com/track/")
            ID = ID[1].split("?utm")
            Data = requests.get('https://api.deezer.com/track/'+str(ID[0])).json()
        else:    
            SongInfo = requests.get('https://api.deezer.com/search?q=artist:"'+self.Artist+'" track:"'+self.SongName+'"').json()
            if SongInfo != []:
                Data = SongInfo['data']
        if Data != []:
            Data = Data[0]
            FoundSong = str(Data['title']).replace(" (Radio Edit)", "").replace("’", "'")
            FoundArtist = Data['artist']['name']
            self.DeezerUrl = str(Data['link'])
            if self.SpotifyUrl != "":
                self.SongName = str(FoundSong)
                self.Artist = str(FoundArtist)
            if self.SongName.lower() == str(FoundSong).lower() and self.Artist.lower() == str(FoundArtist).lower():
                if str(Data['explicit_lyrics']) == 'True' and int(Data['explicit_content_lyrics']) > 0:
                    self.CheckResults['Deezer'] = ['Explicit Content Found']
                else:
                    self.CheckResults['Deezer'] = ['Clean']
            else:
               self.CheckResults['Deezer'] = ['Song Not Found'] 
        else:
            self.CheckResults['Deezer'] = ['Song Not Found']

    def GetApiSeeds(self):
        Lyrics = requests.get("https://orion.apiseeds.com/api/music/lyric/"+self.Artist+"/"+self.SongName+"?apikey="+secrets['apiseeds']).json()
        if not('error' in Lyrics):
            self.Lyrics['ApiSeeds Lyrics'] = str(Lyrics['result']['track']['text']).split("\n")
        else:
            self.CheckResults['ApiSeeds Lyrics'] = ["Song Not Found"]

    def GetGenius(self):
        Song = api.search_song(self.SongName, self.Artist)
        Title = str(Song).split(":")
        FoundSong = Title[0].replace("’", "'")
        if str(FoundSong).lower() == ('"'+self.SongName+'" by '+self.Artist).lower():
            Lyrics = str(Song.lyrics).replace("\2005", " ")
            self.Lyrics['Genius'] = Lyrics.split("\n")
        else:
            self.CheckResults['Genius'] = ["Song Not Found"]

    def GetChartLyrics(self):
        Lyrics = requests.get("http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist="+self.Artist+"&song="+self.SongName, params={'host': 'api.chartlyrics.com'})
        if "200" in str(Lyrics):
            Itterable = Lyrics.iter_lines()
            Lyrics = []
            for item in Itterable:
                Lyrics.append(str(item))
            FoundSong = str(Lyrics[5]).replace("b'  <LyricSong>", "").replace("</LyricSong>", "").replace("'", "")
            FoundArtist = str(Lyrics[6]).replace("b'  <LyricArtist>", "").replace("</LyricArtist>", "").replace("'", "")
            if str(FoundSong).lower() == self.SongName.lower() and str(FoundArtist).lower() == self.Artist.lower():
                Lyrics.pop(-1)
                for i in range(11):
                    Lyrics.pop(0)
                Lyrics = "\n".join(Lyrics)
                Lyrics = Lyrics.replace("b'  <Lyric>", "").replace("</Lyric>'", "").replace("\'", "'").replace("'", '"').replace('b"', "").replace('"', "")
                self.Lyrics['Chart Lyrics'] = Lyrics.split("\n")
            else:
                self.CheckResults['Chart Lyrics'] = ["Song Not Found"]
        else:
            self.CheckResults['Chart Lyrics'] = ["Song Not Found"]

    def GetLoloLyrics(self):
        Lyrics = requests.get("http://api.lololyrics.com/0.5/getLyric?artist="+self.Artist+"&track="+self.SongName)
        if "200" in str(Lyrics):
            Itterable = Lyrics.iter_lines()
            Lyrics = []
            for item in Itterable:
                Lyrics.append(str(item))
            Lyrics.pop(0)
            Lyrics.insert(0, ((str(Lyrics[0]).split("<response>")[1])))
            Lyrics.pop(1)
            Lyrics.append(((str(Lyrics[len(Lyrics)-1]).split("</response>")[0])))
            Lyrics.pop(len(Lyrics)-2)
            Lyrics = "\n".join(Lyrics)
            Lyrics = str(Lyrics).replace("&#13", "").replace("b'", "").replace("'", "")
            self.Lyrics['Lolo Lyrics'] = Lyrics.split("\n")
        else:
            self.CheckResults['Lolo Lyrics'] = ["Song Not Found"]

    def GetCajunLyrics(self):
        Lyrics = requests.get("http://api.cajunlyrics.com/LyricDirectSearch.php?artist="+self.Artist+"&title="+self.SongName)
        if "200" in str(Lyrics):
            if not("<Lyric>Not found</Lyric>" in str(Lyrics.text)):
                ResultData = str(Lyrics.text).replace("<", "\n").replace(">", "\n")
                ResultData = ResultData.split("\n")
                FoundArtist = ResultData[18]
                FoundSong = ResultData[22]
                if str(FoundSong).lower() == self.SongName.lower() and str(FoundArtist).lower() == self.Artist.lower():
                    Lyrics = str(Lyrics.text).split("<Lyric>")
                    Lyrics = Lyrics[1].replace("Lyrics Provided by CajunLyrics.com</Lyric></GetLyricResult>", "")
                    self.Lyrics['Cajun Lyrics'] = Lyrics.split("\n")
                else:
                    self.CheckResults['Cajun Lyrics'] = ["Song Not Found"]
            else:
                self.CheckResults['Cajun Lyrics'] = ["Song Not Found"]
        else:
            self.CheckResults['Cajun Lyrics'] = ["Song Not Found"]


class Errors():
    def __init__(self, client):
        self.client = client

    async def TimedOut(self, Cmd):
        embed = discord.Embed(
            title = Cmd+" Timed Out",
            description = "Please re-run the command.",
            thumbnail = "https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png",
            colour=discord.Colour.green())
        print("["+str(Cmd)+"] Error: Timed Out")
        return embed

    async def Unexpected(self, Cmd):
        embed = discord.Embed(
            title = "An Unexpected Error Occured!",
            description = "Please re-run the command. \nIf this issue persists, please contact the bots owner, Lolo#6699 on Discord.",
            thumbnail = "https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png",
            colour=discord.Colour.green())
        print("["+str(Cmd)+"] Error: Handling Output Of Check")
        return embed
       
Errors = Errors(client)

#SET ACTIVITY 

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="-check"))
    print("Connection Established\nBot Is Now Online & Ready\n")

#CHECK COMMAND

@client.command()
async def check(ctx):
    print("--------------------CHECK INITIALISED--------------------")
    print("[Check] Discord Id: "+str(ctx.author.id))
    Lyrics = Music()
    SearchIcon = client.get_emoji(738865765360599140)
    SpotifyIcon = client.get_emoji(738865749824897077)
    DeezerIcon = client.get_emoji(738865785073696898)
    MusicIcon = client.get_emoji(738865773807665354)
    Stage1 = discord.Embed(
        title = "Please Select What You'd Like To Scan",
        colour = discord.Colour.green())
    Stage1.add_field(name=str(SearchIcon)+" Song Search", value="Enter plain text, and the bot will automatically search and find the closest song to what you enter to scan for explicit content.", inline=False)
    Stage1.add_field(name=str(SpotifyIcon)+" Spotify Link", value="Enter a spotify link, and the bot will return whether or not there is explicit content in that song.", inline=False)
    Stage1.add_field(name=str(DeezerIcon)+" Deezer Link", value="Enter a Deezer link, and the bot will scan that song for explicit langauge and return the result.")
    Stage1.add_field(name=str(MusicIcon)+" MP3 File", value="Upload a MP3 File, and the bot will scan the lyrics of that song for explicit content.", inline=False)
    Stage1.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
    Stage1.set_author(name="Stage 1: Select Input")
    Temp = await ctx.send(embed=Stage1)
    await Temp.add_reaction(emoji=SearchIcon)
    await Temp.add_reaction(emoji=SpotifyIcon)
    await Temp.add_reaction(emoji=DeezerIcon)
    await Temp.add_reaction(emoji=MusicIcon)
    def check(m):
        return m.user_id != 669586333676732464 and m.user_id == ctx.author.id
    try:
        reaction = await client.wait_for("raw_reaction_add", check=check, timeout=60.0)
        Error = 0
        if str(reaction.emoji) == str(SearchIcon):
            print("[Check] Option: Search")
            Stage2 = discord.Embed(
                title = "Please Enter The Name Of The Artist:",
                colour=discord.Colour.green())
            Stage2.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=Stage2)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                artist = await client.wait_for("message", check=check, timeout=60.0)
                print("[Check] Artist Entered: "+str(artist.content))
                Stage2 = discord.Embed(
                    title = "Please Enter The Name Of The Song:",
                    colour=discord.Colour.green())
                Stage2.set_author(name="Stage 2: Enter Details")
                await artist.delete()
                await Temp.edit(embed=Stage2)
                def check(m):
                    return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
                try:
                    song = await client.wait_for("message", check=check, timeout=60.0)
                    print("[Check] Song Entered: "+str(song.content))
                    Stage3 = discord.Embed(
                        title = "Checking Song...",
                        colour=discord.Colour.green())
                    Stage3.set_author(name="Stage 3: Search & Check Song")
                    Stage3.add_field(name="Searching For Song:", value=(str(song.content)+" - "+str(artist.content)))
                    await song.delete()
                    await Temp.edit(embed=Stage3)
                    Lyrics.CheckLyrics(str(song.content), str(artist.content))
                    print("[Check] Check Song Initiated")
                except Exception as e:
                    TimedOut = Errors.TimedOut('Check')
                    await Temp.edit(embed=TimedOut)
                    Error = 1
            except:
                TimedOut = Errors.TimedOut('Check')
                await Temp.edit(embed=TimedOut)
                Error = 1
        elif str(reaction.emoji) == str(SpotifyIcon):
            print("[Check] Option: Spotify")
            Stage2 = discord.Embed(
                title = "Please Enter The Spotify Link:",
                colour=discord.Colour.green())
            Stage2.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=Stage2)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                link = await client.wait_for("message", check=check, timeout=60.0)
                print("[Check] Link Entered: "+str(link.content))
                Stage3 = discord.Embed(
                    title = "Checking Song...",
                    colour=discord.Colour.green())
                Stage3.set_author(name="Stage 3: Search & Check Song")
                Stage3.add_field(name="Link Entered:", value=str(link.content))
                await link.delete()
                await Temp.edit(embed=Stage3)
                Lyrics.CheckLyrics(str(link.content), "")
                print("[Check] Check Song Initiated")
            except:
                TimedOut = Errors.TimedOut('Check')
                await Temp.edit(embed=TimedOut)
                Error = 1
        elif str(reaction.emoji) == str(DeezerIcon):
            print("[Check] Option: Deezer")
            Stage2 = discord.Embed(
                title = "Please Enter The Deezer Link:",
                colour=discord.Colour.green())
            Stage2.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=Stage2)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                link = await client.wait_for("message", check=check, timeout=60.0)
                print("[Check] Link Entered: "+str(link.content))
                Stage3 = discord.Embed(
                    title = "Checking Song...",
                    colour=discord.Colour.green())
                Stage3.set_author(name="Stage 3: Search & Check Song")
                Stage3.add_field(name="Link Entered:", value=str(link.content))
                await link.delete()
                await Temp.edit(embed=Stage3)
                Lyrics.CheckLyrics(str(link.content), "")
                print("[Check] Check Song Initiated")
            except:
                TimedOut = Errors.TimedOut('Check')
                await Temp.edit(embed=TimedOut)
                Error = 1
        elif str(reaction.emoji) == str(MusicIcon):
            print("[Check] Option: MP3 File")
            Stage2 = discord.Embed(
                title = "Please Send The MP3 File Below:",
                colour=discord.Colour.green())
            Stage2.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=Stage2)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                file = await client.wait_for("message", check=check, timeout=60.0)
                File = file.attachments[0]
                filename = File.filename
                downloaded_obj = requests.get(File.url)
                with open(str(filename), "wb") as File:
                    File.write(downloaded_obj.content)
                File.close()
                print("[Check] File Entered: "+str(filename))
                audio = EasyID3(str(filename))
                os.remove(str(filename))
                Stage3 = discord.Embed(
                    title = "Checking Song...",
                    colour=discord.Colour.green())
                Stage3.set_author(name="Stage 3: Search & Check Song")
                Stage3.add_field(name="Song Entered:", value=str(audio['title'][0])+" - "+str(audio['artist'][0]))
                await file.delete()
                await Temp.edit(embed=Stage3)
                Lyrics.CheckLyrics(str(audio['title'][0]), str(audio['artist'][0]))
                print("[Check] Check Song Initiated")
            except:
                TimedOut = Errors.TimedOut('Check')
                await Temp.edit(embed=TimedOut)
                Error = 1
        if Error == 0:
            try:
                print("[Check] Search Results: "+str(Lyrics.CheckResults))
                Clean = True
                BadLines = []
                for key, value in Lyrics.CheckResults.items():
                    if not("Clean" in value or "Song Not Found" in value):
                        Clean = False
                        if not("Explicit Content Found" in value):
                            for line in value:
                                if str(line[-1]) == "," or str(line[-1]) == ";" or str(line[:-1]) == ":":
                                    line = line[:-1]
                                elif str(line[-3]) == "," or str(line[-3]) == ";" or str(line[:-3]) == ":":
                                    line = line[:-3]+line[-2:]
                                if not(str(line) in BadLines):
                                    BadLines.append(str(line))
                            Lyrics.CheckResults[key] = ["Explicit Content Found"]
                BadLines = "\n".join(BadLines)
                Tick = client.get_emoji(738865801964027904)
                Caution = client.get_emoji(738865809878810664)
                Cross = client.get_emoji(738865828648189972)
                WebsiteResults = ""
                for key, value in Lyrics.CheckResults.items():
                    Lyrics.CheckResults[str(key)] = value[0]
                if not("Clean" in Lyrics.CheckResults.values()) and not("Explicit Content Found" in Lyrics.CheckResults.values()):
                    WebsiteResults = str(Caution)+" Song Not Found "+str(Caution)
                    Clean = None
                else:
                    for key, value in Lyrics.CheckResults.items():
                        if str(value) == "Clean":
                            WebsiteResults = WebsiteResults+"\n**"+str(key)+":** "+str(Tick)+" Clean "+str(Tick)
                        elif str(value) == "Explicit Content Found":
                            WebsiteResults = WebsiteResults+"\n**"+str(key)+":** "+str(Cross)+" Explict Content Found "+str(Cross)
                    WebsiteResults = WebsiteResults[1:]
                if Clean == False:
                    embed = discord.Embed(
                        title = "Explicit Content Found!",
                        colour=discord.Colour.green())
                    embed.add_field(name="Song Found:", value=str(Lyrics.SongName)+"\n"+str(Lyrics.Artist), inline=True)
                    embed.add_field(name="Links:", value="[Spotify]("+str(Lyrics.SpotifyUrl)+")\n[Deezer]("+str(Lyrics.DeezerUrl)+")", inline=True)
                    embed.add_field(name="Results:", value=WebsiteResults, inline=False)
                    embed.add_field(name="Explicit Lines:", value=BadLines, inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                    await Temp.edit(embed=embed)
                    print("[Check] Result: Explicit")
                elif Clean == None:
                    embed = discord.Embed(
                        title = "Song Not Found!",
                        colour=discord.Colour.green())
                    embed.add_field(name="Result:", value=WebsiteResults, inline=False)
                    embed.add_field(name="Explicit Lines:", value="N/A", inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                    await Temp.edit(embed=embed)
                    print("[Check] Result: Song Not Found")
                else:
                    embed = discord.Embed(
                        title = "Song Clean!",
                        colour=discord.Colour.green())
                    embed.add_field(name="Song Found:", value=str(Lyrics.SongName)+"\n"+str(Lyrics.Artist), inline=True)
                    embed.add_field(name="Links:", value="[Spotify]("+str(Lyrics.SpotifyUrl)+")\n[Deezer]("+str(Lyrics.DeezerUrl)+")", inline=True)
                    embed.add_field(name="Results:", value=WebsiteResults, inline=False)
                    embed.add_field(name="Explicit Lines:", value="None", inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                    await Temp.edit(embed=embed)
                    print("[Check] Result: Clean")
            except:
                UnexpectedError = Errors.Unexpected('Check')
                await Temp.edit(embed=UnexpectedError)
    except:
        await Temp.delete()
        await ctx.message.delete()

#DISCORD CONNECTION

print("--------------------CONNECTING TO DISCORD--------------------")
client.run(secrets['discord'])
