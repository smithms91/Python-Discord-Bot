import discord
from discord.ext import commands
from views import GambleView
import openai
import os
import requests, json
from dotenv import load_dotenv
import youtube_dl
import YouTube




intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

bot = commands.Bot(command_prefix="$", intents=intents)

from pymongo import MongoClient
client = MongoClient(os.getenv('MONGO_DB_KEY'))
db = client.discord_bot
user_collection = db.users

# Commands start here:

@bot.command()
async def command_list(ctx):
    x = await ctx.author.create_dm()
    reg_embed = discord.Embed(title="Command List", description="$hello -> Say hello!\n\n $gpt <Message> -> Interact with ChatGPT. Ask a question, do math, or write a story!\n\n $dalle <description> -> Interact with AI Image Generator Dalle. Enter a description of any image!\n\n $play -> Add yourself to the database and get 10000 free points to play with!")
    admin_embed = discord.Embed(title="Admin Command List", description="$clear <amount> -> Clears <amount> messages in the current channel.\n\n $kick <user> -> Kicks <user> from the server.\n\n $ban <user> -> Bans <user> from the server.")
    if ctx.author.guild_permissions.administrator:
        await x.send(embed=reg_embed)
        await x.send(embed=admin_embed)
    else:
        await x.send(embed=reg_embed)


@bot.command()
async def hello(ctx):
    await ctx.reply(f"Hi {ctx.author}!")


@bot.command()
async def meme(ctx):
    x = requests.get("https://meme-api.com/gimme")
    await ctx.send(f'{json.loads(x.text)["url"]}')


@bot.command()
async def apex(ctx, arg):
    print(arg)
    headers = {
        'TRN-Api-Key': 'fa882391-7789-4838-a44c-5823dee527ab',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip'
    }
    x = requests.get(f'https://public-api.tracker.gg/v2/apex/standard/profile/origin/{arg}', headers=headers)
    data = x.json()
    total_kills = data['data']['segments'][0]['stats']['kills']['displayValue']
    total_level = data['data']['segments'][0]['stats']['level']['displayValue']
    total_damage = data['data']['segments'][0]['stats']['damage']['displayValue']
    total_headshots = data['data']['segments'][0]['stats']['headshots']['displayValue']
    total_matches = data['data']['segments'][0]['stats']['matchesPlayed']['displayValue']

    embed=discord.Embed(title="Apex Lifetime Stats", description=f"Lifetime stats for {arg}: ", color=0xFF5733)
    embed.add_field(name='Level', value=f"{total_level}")
    embed.add_field(name='Total Kills', value=f"{total_kills}")
    embed.add_field(name='Headshots', value=f"{total_headshots}")
    embed.add_field(name='Total Damage', value=f"{total_damage}")
    embed.add_field(name='Total Matches', value=f"{total_matches}")
    await ctx.send(embed=embed)


@bot.command()
async def play(ctx):
    documents = user_collection.find_one({'username': str(ctx.author)})
        
    if documents:
        await ctx.send(f'You are already playing! You have {documents["points"]} points!')
    else:
        new_document = {
            'username': str(ctx.author),
            'points': 10000
        }
        user_collection.insert_one(new_document)
        await ctx.send(f'You have been added to the database, {ctx.author}. You have 10,000 points to begin!')


@bot.command()
async def gamble(ctx, amt):
    view = GambleView()
    await ctx.send("Pick a game", view=view, mention_author=True)
    

@bot.command()
async def gpt(ctx, *, arg):
    response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=arg,
            max_tokens=1024,
            temperature=0.5,
        )
    await ctx.send(response.choices[0].text)


@bot.command()
async def dalle(ctx, *, arg):
    response = openai.Image.create(
            prompt=arg,
            n=1,
            size="1024x1024",
        )
    image_url = response['data'][0]['url']
    await ctx.send(image_url)


@bot.command()
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command()
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")



@bot.command(name='play_song', help='To play song')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client
        YTDL = YouTube.YTDLSource
        async with ctx.typing():
            filename = await YTDL.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    

@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")



# Admin Commands

@bot.command()
@commands.has_permissions(administrator = True)
async def clear(ctx, amt: int):
    if ctx.author.guild_permissions.administrator:
        await ctx.channel.purge(limit=amt + 1)
    else:
        await ctx.send("You are not allowed to use that command.")





bot.run(os.getenv('TOKEN'))