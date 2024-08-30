#IMPORTING MODULES

print("--------------------IMPORTING MODULES--------------------")

import discord
import os
import json
import requests
import lyricsgenius as genius
from mutagen.easyid3 import EasyID3
from discord.ext import commands

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

#CHECK SONG FUNCTION

def check_song(Song, Artist):

    #SET VARIABLES

    BadLines = {'info': {}}
    Banned_Words = ["ass", "bastard", "bellend", "bollocks", "bitch", "cock", "cunt", "dick", "fuck", "knob", "piss", "prick", "pussy", "shag", "shit", "tits", "twat", "wanker"]
    FalsePositives = ["massive", "glass", "grass", "glasses", "passed", "passing", "assisted", "assembly", "passion", "passions", "class", "pass", "massi", "assigned", "bass", "classy", "passport", "embarrassed"]

    if Song.startswith("https://open.spotify.com/track/"):

        #SPOTIFY - GET TRACK
        
        data = {'grant_type': 'client_credentials', 'redirect_uri': 'http://localhost/', 'client_id': "710b5d6211ee479bb370e289ed1cda3d", 'client_secret': secrets['spotify']}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        info = requests.post("https://accounts.spotify.com/api/token", data, headers)
        Data = info.json()
        Token = Data['access_token']
        ID = Song.split("https://open.spotify.com/track/")
        ID = ID[1]
        ID = ID.split("?si=")
        ID = ID[0]
        Data = requests.get('https://api.spotify.com/v1/tracks/'+str(ID), headers={ 'authorization': "Bearer "+Token })
        Data = Data.json()
        FoundArtist = Data['artists']
        FoundArtist = FoundArtist[0]
        Artist = FoundArtist['name']
        SongName = Data['name']
        SongName = SongName.replace(" - Radio Edit", "")
        Explicit = Data['explicit']
        SongURL = Data['external_urls']
        SpotifyURL = SongURL['spotify']
        print(SpotifyURL)
        print(Artist)
        print(SongName)
        BadLines['info'] = {'SongName': SongName, 'Artist': Artist, 'SpotifyURL': SpotifyURL}
        print(Explicit)
        if str(Explicit) == "True":
            BadLines['Spotify'] = ['Explicit Content Found']
        else:
            BadLines['Spotify'] = ['Clean']

        #DEEZER - GET LYRICS

        SongInfo = requests.get('https://api.deezer.com/search?q=artist:"'+Artist+'" track:"'+SongName+'"')
        SongInfo = SongInfo.json()
        Data = SongInfo['data']
        if Data != []:
            Data = Data[0]
            print()
            print()
            print(Data)
            ID = Data['id']
            FoundSong = Data['title']
            FoundSong = FoundSong.replace("’", "'")
            FoundSong = FoundSong.replace(" (Radio Edit)", "")
            FoundArtist = Data['artist']['name']
            DeezerURL = Data['link']
            print(DeezerURL)
            Info = BadLines['info']
            Info['DeezerURL'] = DeezerURL
            BadLines['info'] = Info
            print(FoundSong)
            print(FoundArtist)
            if str(SongName).lower() == str(FoundSong).lower() and str(Artist).lower() == str(FoundArtist).lower():
                if str(Data['explicit_lyrics']) == 'True' and int(Data['explicit_content_lyrics']) > 0:
                    BadLines['Deezer'] = ['Explicit Content Found']
                else:
                    BadLines['Deezer'] = ['Clean']
            else:
               BadLines['Deezer'] = ['Song Not Found'] 
        else:
            BadLines['Deezer'] = ['Song Not Found']

    elif Song.startswith("https://www.deezer.com/track/"):

        #DEEZER - GET TRACK
        
        ID = Song.split("https://www.deezer.com/track/")
        ID = ID[1]
        ID = ID.split("?utm")
        ID = ID[0]
        print(ID)
        Data = requests.get('https://api.deezer.com/track/'+str(ID))
        Data = Data.json()
        print(Data)
        SongName = Data['title']
        SongName = SongName.replace("’", "'")
        SongName = SongName.replace(" (Radio Edit)", "")
        Artist = Data['artist']['name']
        DeezerURL = Data['link']
        BadLines['info'] = {'SongName': SongName, 'Artist': Artist, 'DeezerURL': DeezerURL}
        if str(Data['explicit_lyrics']) == 'True' and int(Data['explicit_content_lyrics']) > 0:
            BadLines['Deezer'] = ['Explicit Content Found']
        else:
            BadLines['Deezer'] = ['Clean']

        #SPOTIFY - GET LYRICS

        data = {'grant_type': 'client_credentials', 'redirect_uri': 'http://localhost/', 'client_id': "710b5d6211ee479bb370e289ed1cda3d", 'client_secret': secrets['spotify']}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        info = requests.post("https://accounts.spotify.com/api/token", data, headers)
        Data = info.json()
        Token = Data['access_token']
        print(Token)
        SearchQuery = str(Artist)+" - "+str(SongName)
        print(SearchQuery)
        Data = requests.get('https://api.spotify.com/v1/search', headers={ 'authorization': "Bearer "+Token }, params={ 'q': SearchQuery, 'type': 'track', 'limit': "1" })
        Data = Data.json()
        Data = Data['tracks']
        Data = Data['items']
        if str(Data) != "[]":
            Data = Data[0]
            print(Data)
            FoundArtist = Data['artists']
            FoundArtist = FoundArtist[0]
            FoundArtist = FoundArtist['name']
            FoundSong = Data['name']
            FoundSong = FoundSong.replace(" - Radio Edit", "")
            Explicit = Data['explicit']
            SongURL = Data['external_urls']
            SpotifyURL = SongURL['spotify']
            print(SpotifyURL)
            Info = BadLines['info']
            Info['SpotifyURL'] = SpotifyURL
            BadLines['info'] = Info
            print(FoundArtist)
            print(FoundSong)
            print(Explicit)
            if str(FoundArtist).lower() == str(Artist).lower() and str(FoundSong).lower() == str(SongName).lower():
                if str(Explicit) == "True":
                    BadLines['Spotify'] = ['Explicit Content Found']
                else:
                    BadLines['Spotify'] = ['Clean']
            else:
                BadLines['Spotify'] = ['Song Not Found']
        else:
            BadLines['Spotify'] = ['Song Not Found']

    else:

        #DEEZER - SEARCH FOR TRACK

        SongInfo = requests.get('https://api.deezer.com/search?q=artist:"'+Artist+'" track:"'+Song+'"')
        SongInfo = SongInfo.json()
        Data = SongInfo['data']
        if Data != []:
            Data = Data[0]
            ID = Data['id']
            SongName = Data['title']
            SongName = SongName.replace("’", "'")
            SongName = SongName.replace(" (Radio Edit)", "")
            Artist = Data['artist']['name']
            DeezerURL = Data['link']
            BadLines['info'] = {'SongName': SongName, 'Artist': Artist, 'DeezerURL': DeezerURL}
            if str(Data['explicit_lyrics']) == 'True' and int(Data['explicit_content_lyrics']) > 0:
                BadLines['Deezer'] = ['Explicit Content Found']
            else:
                BadLines['Deezer'] = ['Clean']
            print(SongName)
            print(Artist)
        else:
            BadLines['Deezer'] = ['Song Not Found']
            SongName = Song.replace("%20", " ")
            Artist = Artist.replace("%20", " ")
            print(SongName)
            SongName.capitalize()
            print(Artist)
            ToCapitalise = Artist.split(" ")
            Capitalised = []
            for word in ToCapitalise:
                Capitalised.append(word.capitalize())
            Artist = Capitalised.join(" ")
            BadLines['info'] = {'SongName': SongName, 'Artist': Artist}

        print(BadLines)

        #SPOTIFY - GET LYRICS

        data = {'grant_type': 'client_credentials', 'redirect_uri': 'http://localhost/', 'client_id': "710b5d6211ee479bb370e289ed1cda3d", 'client_secret': secrets['spotify']}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        info = requests.post("https://accounts.spotify.com/api/token", data, headers)
        Data = info.json()
        Token = Data['access_token']
        print(Token)
        SearchQuery = str(Artist)+" - "+str(SongName)
        print(SearchQuery)
        Data = requests.get('https://api.spotify.com/v1/search', headers={ 'authorization': "Bearer "+Token }, params={ 'q': SearchQuery, 'type': 'track', 'limit': "1" })
        Data = Data.json()
        Data = Data['tracks']
        Data = Data['items']
        if str(Data) != "[]":
            Data = Data[0]
            print(Data)
            FoundArtist = Data['artists']
            FoundArtist = FoundArtist[0]
            FoundArtist = FoundArtist['name']
            FoundSong = Data['name']
            FoundSong = FoundSong.replace(" - Radio Edit", "")
            Explicit = Data['explicit']
            SongURL = Data['external_urls']
            SpotifyURL = SongURL['spotify']
            print(SpotifyURL)
            Info = BadLines['info']
            print(Info)
            Info['SpotifyURL'] = SpotifyURL
            print(Info)
            BadLines['info'] = Info
            print(FoundArtist)
            print(FoundSong)
            print(Explicit)
            if str(FoundArtist).lower() == str(Artist).lower() and str(FoundSong).lower() == str(SongName).lower():
                if str(Explicit) == "True":
                    BadLines['Spotify'] = ['Explicit Content Found']
                else:
                    BadLines['Spotify'] = ['Clean']
            else:
                BadLines['Spotify'] = ['Song Not Found']
        else:
            BadLines['Spotify'] = ['Song Not Found']

    #APISEEDS - GET LYRICS

    Lyrics1 = requests.get("https://orion.apiseeds.com/api/music/lyric/"+Artist+"/"+SongName+"?apikey="+secrets['apiseeds']).json()
    print(Lyrics1)
    BadLines['ApiSeeds Lyrics'] = []
    if not('error' in Lyrics1):
        Lyrics1 = str(Lyrics1['result']['track']['text'])
        Clean = 1
        SplitLyrics = Lyrics1.split("\n")
        for lyric in SplitLyrics:
            for word in Banned_Words:
                A = str(lyric.lower()).find(word)
                if A != -1:
                    Clean = 0
                    B = lyric.split(" ")
                    BadSentence = []
                    Bad = 0
                    for lyric in B:
                        BadWord = 0
                        for word in Banned_Words:
                            C = str(lyric.lower()).find(word)
                            if C != -1:
                                if not(str(lyric.lower()) in FalsePositives):
                                    Bad = 1
                                    BadWord = 1
                        if BadWord == 1:
                            BadSentence.append("**"+lyric+"**")
                        else:
                            BadSentence.append(lyric)
                    if Bad != 0:
                        BadSentence = " ".join(BadSentence)
                        if not(BadSentence in BadLines['ApiSeeds Lyrics']):
                            BadLines['ApiSeeds Lyrics'].append(BadSentence)
                    else:
                        Clean = 1
        if Clean == 1:
            BadLines['ApiSeeds Lyrics'] = ["Clean"]
    else:
        BadLines['ApiSeeds Lyrics'] = ["Song Not Found"]

    #GENUIS - GET LYRICS

    api=genius.Genius(secrets['genius'])
    song = api.search_song(str(SongName), str(Artist))
    Name = str(song)
    print(Name)
    Title = Name.split(":")
    print(Title)
    FoundSong = Title[0]
    FoundSong = FoundSong.replace("’", "'")
    if str(FoundSong).lower() == ('"'+str(SongName)+'" by '+str(Artist)).lower():
        Lyrics2 = str(song.lyrics)
        print(Lyrics2)
        Clean = 1
        Lyrics2 = Lyrics2.replace("\2005", " ")
        SplitLyrics = Lyrics2.split("\n")
        BadLines['Genius'] = []
        for lyric in SplitLyrics:
            for word in Banned_Words:
                A = str(lyric.lower()).find(word)
                if A != -1:
                    Clean = 0
                    B = lyric.split(" ")
                    BadSentence = []
                    Bad = 0
                    for lyric in B:
                        BadWord = 0
                        for word in Banned_Words:
                            C = str(lyric.lower()).find(word)
                            if C != -1:
                                if not(str(lyric.lower()) in FalsePositives):
                                    Bad = 1
                                    BadWord = 1
                        if BadWord == 1:
                            BadSentence.append("**"+lyric+"**")
                        else:
                            BadSentence.append(lyric)
                    if Bad != 0:
                        BadSentence = " ".join(BadSentence)
                        if not(BadSentence in BadLines['Genius']):
                            BadLines['Genius'].append(BadSentence)
                    else:
                        Clean = 1
        if Clean == 1:
            BadLines['Genius'] = ["Clean"]
    else:
        BadLines['Genius'] = ["Song Not Found"]

    #LOLOLYRICS - GET LYRICS

    Lyrics3 = requests.get("http://api.lololyrics.com/0.5/getLyric?artist="+str(Artist)+"&track="+str(SongName))
    if "200" in str(Lyrics3):
        Itterable = Lyrics3.iter_lines()
        Lyrics3 = []
        for item in Itterable:
            Lyrics3.append(str(item))
        Lyrics3.pop(0)
        Lyrics3.insert(0, ((str(Lyrics3[0]).split("<response>")[1])))
        Lyrics3.pop(1)
        Lyrics3.append(((str(Lyrics3[len(Lyrics3)-1]).split("</response>")[0])))
        Lyrics3.pop(len(Lyrics3)-2)
        Lyrics3 = "\n".join(Lyrics3)
        Lyrics3 = str(Lyrics3).replace("&#13", "")
        Lyrics3 = str(Lyrics3).replace("b'", "")
        Lyrics3 = str(Lyrics3).replace("'", "")
        Clean = 1
        SplitLyrics = Lyrics3.split("\n")
        BadLines['Lolo Lyrics'] = []
        for lyric in SplitLyrics:
            for word in Banned_Words:
                A = str(lyric.lower()).find(word)
                if A != -1:
                    Clean = 0
                    B = lyric.split(" ")
                    BadSentence = []
                    Bad = 0
                    for lyric in B:
                        BadWord = 0
                        for word in Banned_Words:
                            C = str(lyric.lower()).find(word)
                            if C != -1:
                                if not(str(lyric.lower()) in FalsePositives):
                                    Bad = 1
                                    BadWord = 1
                        if BadWord == 1:
                            BadSentence.append("**"+lyric+"**")
                        else:
                            BadSentence.append(lyric)
                    if Bad != 0:
                        BadSentence = " ".join(BadSentence)
                        if not(BadSentence in BadLines['Lolo Lyrics']):
                            BadLines['Lolo Lyrics'].append(BadSentence)
                    else:
                        Clean = 1
        if Clean == 1:
            BadLines['Lolo Lyrics'] = ["Clean"]
    else:
        BadLines['Lolo Lyrics'] = ["Song Not Found"]

    #CHART LYRICS - GET LYRICS

    Lyrics4 = requests.get("http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist="+Artist+"&song="+SongName, params={'host': 'api.chartlyrics.com'})
    print(Lyrics4.text)
    if "200" in str(Lyrics4):
        Itterable = Lyrics4.iter_lines()
        Lyrics4 = []
        for item in Itterable:
            Lyrics4.append(str(item))
        FoundSong = str(Lyrics4[5]).replace("b'  <LyricSong>", "")
        FoundSong = FoundSong.replace("</LyricSong>", "")
        FoundSong = FoundSong.replace("'", "")
        print(FoundSong)
        FoundArtist = str(Lyrics4[6]).replace("b'  <LyricArtist>", "")
        FoundArtist = FoundArtist.replace("</LyricArtist>", "")
        FoundArtist = FoundArtist.replace("'", "")
        print(FoundArtist)
        if str(FoundSong).lower() == str(SongName).lower() and str(FoundArtist).lower() == str(Artist).lower():
            Lyrics4.pop(-1)
            for i in range(11):
                Lyrics4.pop(0)
            print(Lyrics4)
            Lyrics4 = "\n".join(Lyrics4)
            Lyrics4 = Lyrics4.replace("b'  <Lyric>", "")
            Lyrics4 = Lyrics4.replace("</Lyric>'", "")
            Lyrics4 = Lyrics4.replace("\'", "'")
            Lyrics4 = Lyrics4.replace("b'", "")
            Lyrics4 = Lyrics4.replace('b"', "")
            Lyrics4 = Lyrics4.replace("'", "")
            Lyrics4 = Lyrics4.replace('"', "")
            print(Lyrics4)
            Clean = 1
            SplitLyrics = Lyrics4.split("\n")
            BadLines['Chart Lyrics'] = []
            for lyric in SplitLyrics:
                for word in Banned_Words:
                    A = str(lyric.lower()).find(word)
                    if A != -1:
                        Clean = 0
                        B = lyric.split(" ")
                        BadSentence = []
                        Bad = 0
                        for lyric in B:
                            BadWord = 0
                            for word in Banned_Words:
                                C = str(lyric.lower()).find(word)
                                if C != -1:
                                    if not(str(lyric.lower()) in FalsePositives):
                                        Bad = 1
                                        BadWord = 1
                            if BadWord == 1:
                                BadSentence.append("**"+lyric+"**")
                            else:
                                BadSentence.append(lyric)
                        if Bad != 0:
                            BadSentence = " ".join(BadSentence)
                            if not(BadSentence in BadLines['Chart Lyrics']):
                                BadLines['Chart Lyrics'].append(BadSentence)
                        else:
                            Clean = 1
            if Clean == 1:
                BadLines['Chart Lyrics'] = ["Clean"]
        else:
            BadLines['Chart Lyrics'] = ["Song Not Found"]
    else:
        BadLines['Chart Lyrics'] = ["Song Not Found"]
        
    #CAJUN LYRICS - GET LYRICS

    Lyrics5 = requests.get("http://api.cajunlyrics.com/LyricDirectSearch.php?artist="+Artist+"&title="+SongName)
    print(Lyrics5.text)
    if "200" in str(Lyrics5):
        if not("<Lyric>Not found</Lyric>" in str(Lyrics5.text)):
            ResultData = str(Lyrics5.text).replace("<", "\n")
            ResultData = ResultData.replace(">", "\n")
            ResultData = ResultData.split("\n")
            print(ResultData)
            FoundArtist = ResultData[18]
            FoundSong = ResultData[22]
            print(FoundArtist)
            print(FoundSong)
            if str(FoundSong).lower() == str(SongName).lower() and str(FoundArtist).lower() == str(Artist).lower():
                Lyrics5 = str(Lyrics5.text).split("<Lyric>")
                Lyrics5 = Lyrics5[1]
                Lyrics5 = Lyrics5.replace("Lyrics Provided by CajunLyrics.com</Lyric></GetLyricResult>", "")
                print(Lyrics5)
                Clean = 1
                SplitLyrics = Lyrics5.split("\n")
                BadLines['Cajun Lyrics'] = []
                for lyric in SplitLyrics:
                    for word in Banned_Words:
                        A = str(lyric.lower()).find(word)
                        if A != -1:
                            Clean = 0
                            B = lyric.split(" ")
                            BadSentence = []
                            Bad = 0
                            for lyric in B:
                                BadWord = 0
                                for word in Banned_Words:
                                    C = str(lyric.lower()).find(word)
                                    if C != -1:
                                        if not(str(lyric.lower()) in FalsePositives):
                                            Bad = 1
                                            BadWord = 1
                                if BadWord == 1:
                                    BadSentence.append("**"+lyric+"**")
                                else:
                                    BadSentence.append(lyric)
                            if Bad != 0:
                                BadSentence = " ".join(BadSentence)
                                if not(BadSentence in BadLines['Cajun Lyrics']):
                                    BadLines['Cajun Lyrics'].append(BadSentence)
                            else:
                                Clean = 1
                if Clean == 1:
                    BadLines['Cajun Lyrics'] = ["Clean"]
            else:
                BadLines['Cajun Lyrics'] = ["Song Not Found"]
        else:
            BadLines['Cajun Lyrics'] = ["Song Not Found"]
    else:
        BadLines['Cajun Lyrics'] = ["Song Not Found"]

    return BadLines

#SET ACTIVITY 

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="-check"))
    print("Connection Established")
    print("Bot Is Now Online & Ready")
    print()

#CHECK COMMAND

@client.command()
async def check(ctx):
    print("--------------------CHECK INITIALISED--------------------")
    print("[Check] Discord Id: "+str(ctx.author.id))
    SearchIcon = client.get_emoji(738865765360599140)
    SpotifyIcon = client.get_emoji(738865749824897077)
    DeezerIcon = client.get_emoji(738865785073696898)
    MusicIcon = client.get_emoji(738865773807665354)
    embed = discord.Embed(
        title = "Please Select What You'd Like To Scan",
        author = "Stage 1: Select Input",
        thumbnail = "https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png",
        colour = discord.Colour.green())
    embed.add_field(name=str(SearchIcon)+" Song Search", value="Enter plain text, and the bot will automatically search and find the closest song to what you enter to scan for explicit content.", inline=False)
    embed.add_field(name=str(SpotifyIcon)+" Spotify Link", value="Enter a spotify link, and the bot will return whether or not there is explicit content in that song.", inline=False)
    embed.add_field(name=str(DeezerIcon)+" Deezer Link", value="Enter a Deezer link, and the bot will scan that song for explicit langauge and return the result.")
    embed.add_field(name=str(MusicIcon)+" MP3 File", value="Upload a MP3 File, and the bot will scan the lyrics of that song for explicit content.", inline=False)
    Temp = await ctx.send(embed=embed)
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
            print("[Check] Search Selected")
            embed = discord.Embed(
                title = "Please Enter The Name Of The Artist:",
                colour=discord.Colour.green())
            embed.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=embed)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                artist = await client.wait_for("message", check=check, timeout=60.0)
                print("[Check] Artist Entered: "+str(artist.content))
                embed = discord.Embed(
                    title = "Please Enter The Name Of The Song:",
                    colour=discord.Colour.green())
                embed.set_author(name="Stage 2: Enter Details")
                await artist.delete()
                await Temp.edit(embed=embed)
                def check(m):
                    return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
                try:
                    song = await client.wait_for("message", check=check, timeout=60.0)
                    print("[Check] Song Entered: "+str(song.content))
                    embed = discord.Embed(
                        title = "Checking Song...",
                        colour=discord.Colour.green())
                    embed.add_field(name="Searching For Song:", value=(str(song.content)+" - "+str(artist.content)))
                    embed.set_author(name="Stage 3: Search & Check Song")
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                    await song.delete()
                    await Temp.edit(embed=embed)
                    Result = check_song(str(song.content), str(artist.content))
                    print("[Check] Check Song Function Initiated")
                except:
                    embed = discord.Embed(
                        title = "Check Timed Out",
                        description = "Please re-run the command to check another song.",
                        colour=discord.Colour.green())
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                    await Temp.edit(embed=embed)
                    Error = 1
                    print("[Check] Error: Timed Out")
            except:
                embed = discord.Embed(
                    title = "Check Timed Out",
                    description = "Please re-run the command to check another song.",
                    colour=discord.Colour.green())
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await Temp.edit(embed=embed)
                Error = 1
                print("[Check] Error: Timed Out")
        elif str(reaction.emoji) == str(SpotifyIcon):
            print("[Check] Spotify Link Selected")
            embed = discord.Embed(
                title = "Please Enter The Spotify Link:",
                colour=discord.Colour.green())
            embed.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=embed)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                link = await client.wait_for("message", check=check, timeout=60.0)
                print("[Check] Link Entered: "+str(link.content))
                embed = discord.Embed(
                    title = "Checking Song...",
                    colour=discord.Colour.green())
                embed.add_field(name="Link Entered:", value=str(link.content))
                embed.set_author(name="Stage 3: Search & Check Song")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await link.delete()
                await Temp.edit(embed=embed)
                Result = check_song(str(link.content), "None")
                print("[Check] Check Song Function Initiated")
            except:
                embed = discord.Embed(
                    title = "Check Timed Out",
                    description = "Please re-run the command to check another song.",
                    colour=discord.Colour.green())
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await Temp.edit(embed=embed)
                Error = 1
                print("[Check] Error: Timed Out")
        elif str(reaction.emoji) == str(DeezerIcon):
            print("[Check] Deezer Link Selected")
            embed = discord.Embed(
                title = "Please Enter The Deezer Link:",
                colour=discord.Colour.green())
            embed.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=embed)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                link = await client.wait_for("message", check=check, timeout=60.0)
                print("[Check] Link Entered: "+str(link.content))
                embed = discord.Embed(
                    title = "Checking Song...",
                    colour=discord.Colour.green())
                embed.add_field(name="Link Entered:", value=str(link.content))
                embed.set_author(name="Stage 3: Search & Check Song")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await link.delete()
                await Temp.edit(embed=embed)
                Result = check_song(str(link.content), "None")
                print("[Check] Check Song Function Initiated")
            except:
                embed = discord.Embed(
                    title = "Check Timed Out",
                    description = "Please re-run the command to check another song.",
                    colour=discord.Colour.green())
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await Temp.edit(embed=embed)
                Error = 1
                print("[Check] Error: Timed Out")
        elif str(reaction.emoji) == str(MusicIcon):
            print("MP3 File")
            embed = discord.Embed(
                title = "Please Send The MP3 File Below:",
                colour=discord.Colour.green())
            embed.set_author(name="Stage 2: Enter Details")
            await Temp.clear_reactions()
            await Temp.edit(embed=embed)
            def check(m):
                return m.author.id != 713084491500879974 and m.author.id == ctx.author.id
            try:
                file = await client.wait_for("message", check=check, timeout=60.0)
                print(file)
                File = file.attachments
                File = File[0]
                print(File)
                url = File.url
                filename = File.filename
                print(url)
                downloaded_obj = requests.get(url)
                with open(str(filename), "wb") as File:
                    File.write(downloaded_obj.content)
                File.close()
                print("[Check] File Entered: "+str(filename))
                audio = EasyID3(str(filename))
                title = audio['title']
                title = title[0]
                print(title)
                artists = audio['artist']
                artists = artists[0]
                print(artists)
                os.remove(str(filename))
                embed = discord.Embed(
                    title = "Checking Song...",
                    colour=discord.Colour.green())
                value = str(title)+" - "+str(artists)
                print(value)
                embed.add_field(name="Song Entered:", value=value)
                embed.set_author(name="Stage 3: Search & Check Song")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await file.delete()
                await Temp.edit(embed=embed)
                Result = check_song(str(title), str(artists))
                print("[Check] Check Song Function Initiated")
            except:
                embed = discord.Embed(
                    title = "Check Timed Out",
                    description = "Please re-run the command to check another song.",
                    colour=discord.Colour.green())
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await Temp.edit(embed=embed)
                Error = 1
                print("[Check] Error: Timed Out")
        if Error == 0:
            try:
                print("[Check] Search Results: "+str(Result))
                Clean = 1
                Info = Result['info']
                Result.pop('info')
                BadLines = []
                for key, value in Result.items():
                    if not("Clean" in value or "Song Not Found" in value):
                        Clean = 0
                        if not("Explicit Content Found" in value):
                            for line in value:
                                if str(line[-1]) == "," or str(line[-1]) == ";" or str(line[:-1]) == ":":
                                    line = line[:-1]
                                elif str(line[-3]) == "," or str(line[-3]) == ";" or str(line[:-3]) == ":":
                                    line = line[:-3]+line[-2:]
                                if not(str(line) in BadLines):
                                    BadLines.append(str(line))
                            Result[key] = ["Explicit Content Found"]
                BadLines = "\n".join(BadLines)
                Tick = client.get_emoji(738865801964027904)
                Caution = client.get_emoji(738865809878810664)
                Cross = client.get_emoji(738865828648189972)
                WebsiteResults = ""
                for key, value in Result.items():
                    print(str(value))
                    Result[str(key)] = value[0]
                print(Result)
                if not("Clean" in Result.values()) and not("Explicit Content Found" in Result.values()):
                    WebsiteResults = str(Caution)+" Song Not Found "+str(Caution)
                    Clean = 2
                else:
                    for key, value in Result.items():
                        print(str(key))
                        print(str(value))
                        if str(value) == "Clean":
                            print("Clean")
                            WebsiteResults = WebsiteResults+"\n**"+str(key)+":** "+str(Tick)+" Clean "+str(Tick)
                        elif str(value) == "Explicit Content Found":
                            print("Explicit")
                            WebsiteResults = WebsiteResults+"\n**"+str(key)+":** "+str(Cross)+" Explict Content Found "+str(Cross)
                    WebsiteResults = WebsiteResults[1:]
                if Clean == 0:
                    embed = discord.Embed(
                        title = "Explicit Content Found!",
                        colour=discord.Colour.green())
                    embed.add_field(name="Song Found:", value=str(Info['SongName'])+"\n"+str(Info['Artist']), inline=True)
                    embed.add_field(name="Links:", value="[Spotify]("+str(Info['SpotifyURL'])+")\n[Deezer]("+str(Info['DeezerURL'])+")", inline=True)
                    embed.add_field(name="Results:", value=WebsiteResults, inline=False)
                    embed.add_field(name="Explicit Lines:", value=BadLines, inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                    await Temp.edit(embed=embed)
                    print("[Check] Result: Explicit")
                elif Clean == 2:
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
                    embed.add_field(name="Song Found:", value=str(Info['SongName'])+"\n"+str(Info['Artist']), inline=True)
                    embed.add_field(name="Links:", value="[Spotify]("+str(Info['SpotifyURL'])+")\n[Deezer]("+str(Info['DeezerURL'])+")", inline=True)
                    embed.add_field(name="Results:", value=WebsiteResults, inline=False)
                    embed.add_field(name="Explicit Lines:", value="None", inline=False)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                    await Temp.edit(embed=embed)
                    print("[Check] Result: Clean")
            except:
                embed = discord.Embed(
                    title = "An Unexpected Error Occured!",
                    description = "Please re-run the command to check another song. \nIf this issue persists, please contact the bots owner, Lolo#6699 on Discord.",
                    colour=discord.Colour.green())
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/738862396445032538/739271143910801429/Musicstry_Logo.png")
                await Temp.edit(embed=embed)
                print("[Check] Error: Handling Output Of Check")
    except:
        await Temp.delete()
        await ctx.message.delete()

#LRYRICS COMMAND

@client.command()
async def lyrics(ctx):
    print("--------------------LYRICS INITIALISED--------------------")
    print("[Check] Discord Id: "+str(ctx.author.id))
    await ctx.send("Please enter the artist:")
    artist = await client.wait_for("message")
    while artist.author.id == 669586333676732464 or artist.channel.id != ctx.channel.id or artist.author.id != ctx.author.id:
        artist = await client.wait_for("message")
    print("[Check] Artist Entered: "+str(artist.content))
    await ctx.send("Please enter the name of the song:")
    song = await client.wait_for("message")
    while song.author.id == 669586333676732464 or song.channel.id != ctx.channel.id or song.author.id != ctx.author.id:
        song = await client.wait_for("message")
    print("[Check] Song Entered: "+str(song.content))
    await ctx.send("Getting Lyrics: "+str(song.content)+" - "+str(artist.content))
    api=genius.Genius(secrets['genius'])
    song = api.search_song(str(song.content), str(artist.content))
    Name = str(song)
    Title = Name.split(":")
    DMChannel = await ctx.author.create_dm()
    print("[Check] Song Found: "+str(Title[0]))
    await DMChannel.send("**Song Found: "+str(Title[0])+"**")
    Lyrics = str(song.lyrics)
    print(Lyrics)
    Lyrics = Lyrics.replace("\u2005", " ")
    SplitLyrics = Lyrics.split("\n")
    n = 0
    SplitIndex = 0
    for i in range(0, len(SplitLyrics)):
        n = n + len(SplitLyrics[i])
        if n > 1750:
            SplitIndex = i
            break
    print(SplitLyrics)
    First = ""
    if SplitIndex != 0:
        for i in range(0, SplitIndex):
            First = First+"\n"+SplitLyrics[0]
            SplitLyrics.pop(0)
        Second = "\n".join(SplitLyrics)
        await DMChannel.send(First)
        await DMChannel.send(Second)
    else:
        First = "\n".join(SplitLyrics)
        await DMChannel.send(First)

#SONGINFO COMMAND

@client.command()
async def songinfo(ctx):
    print(client.guilds)

#DISCORD CONNECTION

print("--------------------CONNECTING TO DISCORD--------------------")
client.run(secrets['discord'])
