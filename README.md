# Musicstry Lyric Checker

Musicstry was an experimental tool developed during the 2020 lockdown just after studying for my GCSE's, and forms the first example of a significant completed project. It aims to scan multiple lyric sources given an input, and check whether those lyrics contain an explicit lyric. The program could then return a boolean true/false veridct to the user, along with any line numbers containing explicit lyrics so that the user could double check for false positives.

The program was interfaced through the use of a Discord bot, allowing my friends at an online radio station to use it themselves to make sure that the songs they wanted to play were appropiate for the air. This is the reason that initially inspired the project as well.

## About The Implementation

Musicstry.py was the orignial implementation. This was my first time working with an API, particularily the Spotify Web API, which would become a critical part of my A-Level project over the next couple of years. However, at this time, I only minimal programming knowledge, with only basic knowledge of functional programming in Python.

In year 12, I decided to revist the project during the introduction to object-oriented programming with classes in Python. I used classes to help encapsulate and resuse some of the longer functions inside the original version. This proved to be good practice for my A-Level project.

## Running The Code

To run your own instance of the code, you will need accounts with the following 4 companies:

- [Genius API](https://docs.genius.com/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- APISeeds (Depreciated)
- [Discord Developers](https://discord.com/developers)
