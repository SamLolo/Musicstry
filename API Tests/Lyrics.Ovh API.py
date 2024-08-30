import requests

response = requests.get("https://api.lyrics.ovh/v1/Coldplay/Adventure of a Lifetime")

Lyrics = str(response.text).split('"')

SplitLyrics = str(Lyrics[3]).replace("\\r", "")
SplitLyrics = str(SplitLyrics).split("\\n")
while("" in SplitLyrics) : 
    SplitLyrics.remove("") 

print(SplitLyrics)

