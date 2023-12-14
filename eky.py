from __future__ import unicode_literals

from spotipy.oauth2 import SpotifyClientCredentials
from forex_python.converter import CurrencyRates
from datetime import datetime, date
from PIL import Image, ImageEnhance
from discord.ext import commands
from discord import SyncWebhook
from colorama import Fore
from math import trunc

import requests
import asyncio
import discord
import spotipy
import random
import typing
import pydub
import json
import re
import io
import re


#! Declaring variables


ascii_quality = 100
ascii_qualities = {"medium": 100, "high": 200, "low": 50}

WEBHOOK_URL = 
webhook = SyncWebhook.from_url(WEBHOOK_URL)
server_id = 
log_channel_name = "bot-logs"
media_channel_name = "image-gen"
mail_hannel_name = "mail"
mail_send_time = "20:00"
media_types = ["png", "jpeg", "gif", "jpg", "mp4", "mov"]

intents = discord.Intents().all()
bot = discord.Bot(command_prefix='.', intents=intents)


#! Declaring dictionary


command_dict = {
    "flip":     [":coin:", "Coin flip.", ""],
    "ping":     [":ping_pong:", "Pings internet connection.", ""],
    "owoify":   [":flag_jp:", "Makes everyting much kawaii~", ""],
    "echo":     [":speaker:", "Repeats the input text.", "text = string"],
    "roll":     [":four_leaf_clover:", "Rolls the dice.", "min = integer, max = integer"],
    "help":     [":grey_question:", "Displays a list of available commands", ""],
    "shazam":   [":microphone:", "Searches for similar songs", ""],

    "eng":      [":flag_gb:", "Random English words.", "amount = (max 150)"],
    "hun":      [":flag_hu:", "Random Hungarian words.", "amount = (max 150)"],
    "chi":      [":flag_cn:", "Random Chinese characters.", "amount = (max 2000)"],

    "cl":    [":wastebasket:", "Clears text messages.", "amount = integer"],
    "bake":     [":frame_photo:", "Bakes an image.", "amount = (-10, +10), back = (max 30)"],
    "ascii":    [":frame_photo:", "Image to ASCII art", "back = (max 30)"],
    "low":      [":point_down::skin-tone-1:", "Makes an image low quality.", "amount = (-10, +10), back = (max 30)"],
    "urban":    [":book:", "Generates random definition.", "amount = (max 10)"],
    "wiki":     [":globe_with_meridians:", "Generates random wiki article.", "amount = (max 10)"],
    "sos":      [":sos:", "Tags everyone", ""],
    "gym":      [":muscle::skin-tone-1:", "Gym day dolog", ""]
}

reddit_pages = [
    "discordmemes",
    "arabfunny",
    "shitposting",
    "cursedmemes",
    "cursedimages"
]


#! Api keys


async def main():
    with open('.txt') as f:
        file = f.readlines()
    global DISCORD_BOT_TOKEN
    DISCORD_BOT_TOKEN = file[1].strip()
asyncio.run(main())


#! Help command


@bot.slash_command(guild_id=server_id, name="help", description=command_dict["help"][1])
async def help(ctx):
    command_definitions = sorted(command_dict.items(), key=lambda x: (len(x[1][1])+len(x[1][2]))/2)

    em = discord.Embed(
        title=":grey_question:Help",
        description="\n",
        color=discord.Color.blurple())

    em.set_thumbnail(
        url=ctx.bot.user.avatar.url)

    for command, description in command_definitions:
        if len(description[2]) == 0:
            command_syntax = description[1]
        else:
            command_syntax = f"{description[1]}\n`{description[2]}`"

        em.add_field(
            name=command,
            value=f"{description[0]} {command_syntax}\n",
            inline=False
        )

    await ctx.response.send_message(embed=em, ephemeral=True)
    return


#! Random wiki page gen


def randomarticle():
    response = requests.get("https://en.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=1")
    return response.json()

def randomword():
    response = requests.get("https://api.urbandictionary.com/v0/random")
    return response.json()

@bot.slash_command(guild_id=server_id, name="wiki", description=command_dict["wiki"][1])
async def wiki(ctx, amount: int = 1):
    amount = min(amount, 10)
    
    if amount <= 0:
        await ctx.response.send_message("`amount` must be positive", ephemeral=True)
        return

    def get_random_wikipedia_article():
        data = randomarticle()
        article = data["query"]["random"][0]["title"].replace(" ", "_")
        return f"https://en.wikipedia.org/wiki/{article}"
    
    await ctx.response.defer()
    await ctx.followup.send(get_random_wikipedia_article())

    for _ in range(1, amount):
        await ctx.channel.send(get_random_wikipedia_article())

    return


#! Random urban dictionary definition gen


@bot.slash_command(guild_id=server_id, name="urban", description=command_dict["urban"][1])
async def urban(ctx, amount: int = 1):
    amount = min(amount, 10)

    if amount <= 0:
        await ctx.response.send_message("`amount` must be positive", ephemeral=True)
        return

    def create_word_embed(data):
        firstdef = data["list"][0]
        author = firstdef["author"]
        definition = firstdef["definition"].replace('[', '**').replace(']', '**')
        word = firstdef["word"]

        word_embed = discord.Embed(title=word, description=f"*{author}*", color=discord.Color.dark_blue())
        word_embed.add_field(name='', value=definition)

        return word_embed

    await ctx.response.defer()

    data = randomword()
    json_data = json.dumps(data)  # Convert dictionary to JSON string
    parsed_data = json.loads(json_data)  # Parse the JSON string
    await ctx.followup.send(embed=create_word_embed(parsed_data))

    for _ in range(1, amount):
        data = randomword()
        json_data = json.dumps(data)  # Convert dictionary to JSON string
        parsed_data = json.loads(json_data)  # Parse the JSON string
        await ctx.channel.send(embed=create_word_embed(parsed_data))


#! Shazam


def get_similar_songs(track, artist, link):
    spotify_client_id = 
    spotify_client_secret = 

    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    if link:
        match = re.search(r'track/([a-zA-Z0-9]+)', link)
        if match:
            track_id = match.group(1)
        else:
            return []

    else:
        query = f"{track} artist:{artist}" if track and artist else track or artist
        results = sp.search(q=query, type='track', limit=10)

        if results['tracks']['items']:
            track_id = max(results['tracks']['items'], key=lambda t: t['popularity'])['id']
        else:
            return []

    audio_features = sp.audio_features(track_id)
    if audio_features:
        audio_features = audio_features[0]
    else:
        return []

    recommendations = sp.recommendations(seed_tracks=[track_id], limit=10)

    similar_track_ids = [track['id'] for track in recommendations['tracks']]

    track_urls = ' '.join(['https://open.spotify.com/track/' + track_id for track_id in similar_track_ids])

    return track_urls

@bot.slash_command(guild_id=server_id, name="shazam", description=command_dict["shazam"][1])
async def mc(ctx, link: typing.Optional[str] = None, track: typing.Optional[str] = None, artist: typing.Optional[str] = None):
    if not (track or artist or link):
        await ctx.response.send_message("Please specify a parameter.", ephemeral=True)
        return

    response = get_similar_songs(track, artist, link)

    if not response:
        await ctx.response.send_message("No similar songs found.", ephemeral=True)
        return

    track_links = response.split() 
    num_links = 5

    await ctx.response.send_message("Here are the similar songs:", ephemeral=True)

    await ctx.followup.send('\n'.join(track_links[:num_links]), ephemeral=True)
    await ctx.followup.send('\n'.join(track_links[num_links:num_links * 2]), ephemeral=True)
    return



#! Asciify


ASCII_CHARS = ["@", "8", "&", "W", "#", "S", "%", "?", "*", "+", ";", ":", ",", ".", " "]

def resize_image(image, quality):
    width, height = image.size
    ratio = height / width
    new_height = int(quality * ratio * 0.5)
    return image.resize((quality, new_height))

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image, threshold=20):
    pixels = image.getdata()
    min_pixel = min(pixels)
    max_pixel = max(pixels)
    characters = "".join([ASCII_CHARS[int((pixel - min_pixel) * (len(ASCII_CHARS) - 1) / (max_pixel - min_pixel))] if pixel >= threshold else " " for pixel in pixels])
    return characters

async def asciify(image_url, quality):
    image = Image.open(requests.get(image_url, stream=True).raw)
    new_image_data = pixels_to_ascii(grayify(resize_image(image, quality)))
    ascii_image = "\n".join([new_image_data[index:(index+quality)] for index in range(0, len(new_image_data), quality)])
    return ascii_image

@bot.slash_command(guild_id=server_id, name="ascii", description=command_dict["ascii"][1])
async def ascii(ctx, back: typing.Optional[int] = 4, resolution: typing.Optional[str] = "medium"):
    if back <= 0:
        await ctx.response.send_message("`back` must be positive", ephemeral=True)
        return

    if resolution not in ascii_qualities:
        await ctx.response.send_message("Invalid `resolution`. (`low`/`medium`/`high`)", ephemeral=True)
        return

    quality = ascii_qualities[resolution]

    images = []
    ascii_text_list = []

    async for message in ctx.channel.history(limit=back):
        if message.author == bot.user:
            continue
        for attachment in message.attachments:
            url = attachment.url
            if url.endswith(('png', 'jpeg', 'jpg')):
                images.append(url)

    if not images:
        await ctx.response.send_message(f"No image found in the past `{back}` messages", ephemeral=True)
        return

    ascii_text_list = []
    for image_url in images:
        ascii_text = await asciify(image_url, quality)
        ascii_text_list.append(ascii_text)

    all_ascii_text = "\n\n".join(ascii_text_list)

    ascii_file = io.StringIO(all_ascii_text)
    await ctx.response.defer()
    await ctx.followup.send(content="Here is the `ASCII` art as a text file:", file=discord.File(ascii_file, filename="ascii.txt"))
    return


#! Word gen


def get_random_words(file_path, amount, max_amount):
    with open(file_path, encoding='utf-8') as f:
        words = f.read().splitlines()

    if amount > max_amount:
        amount = max_amount

    if amount <= 0:
        raise ValueError("`amount` must be positive")

    random_words = [random.choice(words).lower() for _ in range(amount)]
    return random_words

@bot.slash_command(guild_id=server_id, name="hun", description=command_dict["hun"][1])
async def random_hungarian_word(ctx, amount: typing.Optional[int] = 5):
    try:
        random_words = get_random_words("/home/p/discord/src/hungarian_dictionary.txt", amount, 150)
    except ValueError as e:
        await ctx.response.send_message(str(e), ephemeral=True)
        return

    await ctx.response.defer()
    await ctx.followup.send("\n".join(random_words))

@bot.slash_command(guild_id=server_id, name="eng", description=command_dict["eng"][1])
async def random_english_word(ctx, amount: typing.Optional[int] = 5):
    try:
        random_words = get_random_words("/home/p/discord/src/english_dictionary.txt", amount, 150)
    except ValueError as e:
        await ctx.response.send_message(str(e), ephemeral=True)
        return

    await ctx.response.defer()
    await ctx.followup.send("\n".join(random_words))

@bot.slash_command(guild_id=server_id, name="chi", description=command_dict["chi"][1])
async def random_chinese_character(ctx, amount: typing.Optional[int] = 5):
    if amount > 2000:
        amount = 2000

    if amount <= 0:
        await ctx.response.send_message(f"`amount` must be positive", ephemeral=True)
        return

    start = 0x4E00
    end = 0x9FFF
    string = ""

    for _ in range(amount):
        x = random.randint(start, end)
        character = chr(x)
        string += character

    await ctx.response.defer()
    await ctx.followup.send(string)


#! Ping command


@bot.slash_command(guild_id=server_id, name="ping", description=command_dict["ping"][1])
async def ping(ctx):
    ping = round(bot.latency * 1000)

    await ctx.response.send_message(f"pong! Connection speed is `{ping}`ms\n", ephemeral=True)


#! echo


@bot.slash_command(guild_id = server_id, name = "echo", description = command_dict["echo"][1])
async def echo(ctx, text: str):
    text_segments = [text[i:i+2000] for i in range(0, len(text), 2000)]

    await ctx.response.defer()

    for segment in text_segments:
        await ctx.followup.send(segment)


#! Roll command


@bot.slash_command(guild_id = server_id, name = "roll", description = command_dict["roll"][1])
async def roll(ctx, min: typing.Optional[int] = 1, max: typing.Optional[int] = 6):
    if min < 0 or max < 0:
        await ctx.response.send_message("`min` and `max` must be positive", ephemeral=True)
        return
    
    number = random.randint(min, max)
    await ctx.response.defer()

    user = await bot.fetch_user(ctx.user.id)
    await ctx.followup.send(f"{user} rolled a **{number}**")



#! Flip command


@bot.slash_command(name = "flip", description=command_dict["flip"][1], guild=discord.Object(id=server_id))
async def flip(ctx):
    outcome = random.choice(["Heads", "Tails"])
    await ctx.response.defer()

    user = await bot.fetch_user(ctx.user.id)
    await ctx.followup.send(f"{user} flipped **{outcome}**")



#! Gym command


@bot.slash_command(name = "gym", description=command_dict["gym"][1], guild=discord.Object(id=server_id))
async def flip(ctx):
    outcome = random.randint(0, 100)
    await ctx.response.defer()

    message = ""
    if outcome <= 5:
        message = "**THEY DON'T KNOW ME SON. MÉSZ MINT A GECI** \nhttps://tenor.com/view/ronnie-coleman-bodybuilder-posing-bicep-gif-20430812"
    if 6 < outcome <= 80:
        message = "Mész. pont. ki leszel baszva"
    if 81 < outcome <= 99:
        message = "Pihi nap / *bunozes*"
    if outcome == 100:
        message = "**LÁB NAP. NINCS KIFOGAS** \nhttps://tenor.com/view/leg-press-workout-heavy-weights-tough-focused-gif-13985833"
    


    user = await bot.fetch_user(ctx.user.id)
    await ctx.followup.send(f"{message}")



#! SOS command


@bot.slash_command(name = "sos", description=command_dict["sos"][1], guild=discord.Object(id=server_id))
async def sos(ctx):
    
    await ctx.response.defer()

    user = await bot.fetch_user(ctx.user.id)
    server = ctx.guild
    members = [member for member in server.members if not member.bot]

    mentions = [f"<@{member.id}>" for member in members]


    mention_message = " ".join(mentions)

    await ctx.followup.send(f":sos: \n {mention_message}")


#! Owoify command


vowels = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
smileys = [' ;w; ', ' ^w^ ', ' >w< ', ' OwO ', ' :3 ', ' UwU ']

def text_to_owo(text):
    text = text.replace('L', 'W').replace('l', 'w')
    text = text.replace('R', 'W').replace('r', 'w')

    for v in vowels:
        text = text.replace(f'n{v}', f'ny{v}')
        text = text.replace(f'N{v}', f'N{"Y" if v.isupper() else "y"}{v}')

    words = re.split(r'(\s+)', text)
    num_smileys = max(1, len(words) // 12)  # Number of smileys based on text length

    smiley_indices = [i for i in range(1, len(words), 12)]
    smiley_indices = random.sample(smiley_indices, min(num_smileys, len(smiley_indices)))
    smiley_indices.sort(reverse=True)

    for index in smiley_indices:
        words.insert(index, random.choice(smileys))

    words.append(random.choice(smileys))  # Add one random smiley at the end of the text

    return ''.join(words)

@bot.slash_command(name="owoify", description=command_dict["owoify"][1], guild=discord.Object(id=server_id))
async def owo(ctx, text: str):
    sentence = text_to_owo(text)

    await ctx.response.defer()
    await ctx.followup.send(sentence)
    return


#! Bake command


@bot.slash_command(guild_id=server_id, name="bake", description=command_dict["bake"][1])
async def bake(ctx, amount: typing.Optional[int] = 2, back: typing.Optional[int] = 4):
    if not (-10 <= amount <= 10):
        await ctx.response.send_message("Invalid `amount`.   (-10 - 10)", ephemeral=True)
        return
    
    if back <= 0:
        await ctx.response.send_message("`back` must be positive", ephemeral=True)
        return

    baked_images = []
    async for message in ctx.channel.history(limit=back):
        for attachment in message.attachments:
            if attachment.url.endswith(('png', 'jpeg', 'jpg')):
                response = requests.get(attachment.url)
                image = Image.open(io.BytesIO(response.content))
                for enhancer_type in [ImageEnhance.Contrast, ImageEnhance.Color, ImageEnhance.Sharpness]:
                    enhancer = enhancer_type(image)
                    image = enhancer.enhance(amount)

                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                baked_images.append(buffer)
                buffer.seek(0)

    if not baked_images:
        await ctx.response.send_message(f"No images found to bake in the previous `{amount}` messages.", ephemeral=True)
        return

    await ctx.response.send_message("Baked images:")
    for image_buffer in baked_images:
        image_buffer.seek(0)
        try:
            await ctx.send(file=discord.File(image_buffer, filename='image.png'))
        except discord.errors.HTTPException:
            await ctx.send("Error baking photo. Please try again.")
        finally:
            image_buffer.close()


#! Low command


async def low_quality(amount: int, back: int, url: str) -> bytes:
    response = requests.get(url)
    file_bytes = response.content

    if url.endswith('.mp3'):
        audio = pydub.AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        modified_audio = audio.set_frame_rate(int(audio.frame_rate / amount))
        buffer = io.BytesIO()
        modified_audio.export(buffer, format="mp3")
    else:
        image = Image.open(io.BytesIO(file_bytes))
        target_size = (image.width // amount, image.height // amount)  # Calculate target size for compression
        resized_image = image.resize(target_size, Image.ANTIALIAS)  # Resize the image to a smaller size
        restored_image = resized_image.resize(image.size, Image.LANCZOS)  # Rescale the image to the original size
        buffer = io.BytesIO()
        restored_image.save(buffer, format='PNG')

    buffer.seek(0)
    return buffer.getvalue()

@bot.slash_command(guild_id=server_id, name="low", description=command_dict["low"][1])
async def low(ctx, amount: typing.Optional[int] = 2, back: typing.Optional[int] = 4):
    if back > 30:
        back = 30

    if amount <= 0 or back <= 0:
        await ctx.response.send_message("`amount` and `back` must be positive", ephemeral=True)
        return

    files = []
    async for message in ctx.channel.history(limit=back):
        for attachment in message.attachments:
            url = attachment.url
            if url.endswith(('png', 'jpeg', 'jpg', 'mp3')):
                files.append(url)
    if not files:
        await ctx.response.send_message(f"No images or MP3 files found in the last `{back}` messages.", ephemeral=True)
        return

    await ctx.response.defer()
    await ctx.followup.send("Here are the low-quality images/audios:")
    for url in files:
        try:
            file_bytes = await low_quality(amount, back, url)
            if url.endswith('.mp3'):
                await ctx.channel.send(file=discord.File(io.BytesIO(file_bytes), filename='audio.mp3'))
                return
            else:
                await ctx.channel.send(file=discord.File(io.BytesIO(file_bytes), filename='image.png'))
                return
        except Exception as e:
            await ctx.response.send_message(f"Failed to process file: `{url}`", ephemeral=True)
            return


#! Clear 


@bot.slash_command(guild_id=server_id, name="cl", description=command_dict["cl"][1])
async def clear(ctx, amount: typing.Optional[int] = None, all: typing.Optional[bool] = False):
    if "clear user" not in [i.name.lower() for i in ctx.author.roles]:
        await ctx.response.send_message("You need to have the *clear user* role to use this command", ephemeral=True)
        return

    if amount is None and all is False:
        await ctx.response.send_message("Please specify a parameter.", ephemeral=True)
        return

    if amount is None and not all:
        await ctx.response.defer()
        await ctx.channel.purge(limit=None)
    else:
        if amount is not None and amount <= 0:
            await ctx.response.send_message("`amount` must be positive", ephemeral=True)
            return
        if all:
            if amount is not None and amount > 0:
                await ctx.response.defer()
                await ctx.channel.purge(limit=amount + 1)
            else:
                await ctx.response.defer()
                await ctx.channel.purge(limit=None)
        else:
            amount_int = int(amount)
            await ctx.response.defer()
            await ctx.channel.purge(limit=amount_int + 1)


#? Startup


@bot.event
async def on_ready():
    print(f"{Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}]{Fore.GREEN} {bot.user.name} online!")


    watching = discord.Streaming(type=2, url="https://www.youtube.com/watch?v=n8ItgETgpB8", name=f" in {len(bot.guilds)} servers!")
    await bot.change_presence(status=discord.Status.online, activity=watching)

bot.run(DISCORD_BOT_TOKEN)
