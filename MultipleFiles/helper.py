import discord
from discord.ext import commands
import datetime
import random

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_random_color():
    return discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

def is_owner(ctx):
    return ctx.author.id == ctx.bot.owner_id

def format_number(num):
    return "{:,}".format(num)

def get_embed(title, description, color=discord.Color.blue()):
    return discord.Embed(title=title, description=description, color=color)