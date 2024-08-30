import azapi

API = azapi.AZlyrics('google', accuracy=0.5)

API.artist = 'Tylor Swft'
API.title = 'Bad Blods'

API.getLyrics(save=False, ext='lrc')
SplitLyrics = str(API.lyrics).split("\n")
while "" in SplitLyrics:
    SplitLyrics.remove("")

print(SplitLyrics)
print(API.title, API.artist)
