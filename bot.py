import discord
from discord.ext import commands
import re
import json

img_regex = re.compile(r".+\.(png|jpeg|gif|jpg)$")
url_regex = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
)

bot = commands.Bot(command_prefix="$", case_insensitive=True)


class MediaType:
    Link = "links"
    Photo = "photos"


def set_channel(ctx, channel_type: MediaType, channel_id: discord.TextChannel):
    server_id = str(ctx.message.guild.id)
    with open("channel_ids.json", "r") as channel_file:
        channel_ids = json.load(channel_file)
    if server_id in channel_ids:
        channel_ids[server_id][str(channel_type)] = channel_id.id
    else:
        channel_ids[server_id] = {str(channel_type): channel_id.id}
    with open("channel_ids.json", "w") as channel_file:
        json.dump(channel_ids, channel_file)


@bot.command(aliases=["set_links", "sl"])
async def set_link(ctx, channel_id: discord.TextChannel):
    """set the link channel name (admin only)"""
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send(f"🚧 Admins only 🚧")
        return
    set_channel(ctx, MediaType.Link, channel_id)
    await ctx.send(
        f"{ctx.author.mention} The links channel has been set to <#{channel_id.id}>"
    )


@bot.command(aliases=["set_photos", "sp"])
async def set_photo(ctx, channel_id: discord.TextChannel):
    """set the photo channel name (admin only)"""
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send(f"🚧 Admins only 🚧")
        return
    set_channel(ctx, MediaType.Photo, channel_id)
    await ctx.send(
        f"{ctx.author.mention} The photos channel has been set to <#{channel_id.id}>"
    )


@bot.listen("on_ready")
async def on_ready():
    print("Logged on as {0}!".format(bot.user))
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="you")
    )


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: `{error}`")


async def get_media(media_type: MediaType, message, channel_ids, guild_id):
    if media_type in channel_ids[guild_id]:
        channel = bot.get_channel(channel_ids[guild_id][media_type])
        await channel.send(message)


@bot.listen("on_message")
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    with open("channel_ids.json", "r") as channel_file:
        channel_ids = json.load(channel_file)
    guild_id = str(message.guild.id)
    if guild_id not in channel_ids:
        return
    for attachment in message.attachments:
        if img_regex.match(attachment.url):
            await get_media(MediaType.Photo, attachment.url, channel_ids, guild_id)
    if img_regex.match(message.content):
        await get_media(MediaType.Photo, message.content, channel_ids, guild_id)
    elif url_regex.match(message.content):
        await get_media(MediaType.Link, message.content, channel_ids, guild_id)


with open("token.txt", "r") as f:
    token = f.read()
bot.run(token)
