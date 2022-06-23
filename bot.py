import os
from typing import Optional

import httpx
from discord.ext import commands
from thefuzz import process

from constants import CHOICE_MAPPING
from utility.steam_helpers import get_steam_username

# Grabbing the specified discord bot token (setup here- https://discordpy.readthedocs.io/en/stable/discord.html)
TOKEN: str = os.getenv("DISCORD_TOKEN")

# Getting the specified URL where a FlyAPI instance is running
BASE_URL: str = os.getenv("BASE_URL")

bot: commands.Bot = commands.Bot(command_prefix="!")


@bot.command(name="course", help="Get the leaders for a particular course")
async def send_course_leaderboard(ctx, *args):
    """
    Gets the top 10 times for a particular course
    :param ctx: default parameter that is injected by bot and handles message response
    :param args: will be a list of string arguments (whatever the user typed past !course)
    :return:
    """
    # Fuzzy search on course to resolve proper course name. WIll always return a result from the mapping
    # Mapping exists as db course lookup is still in flux- may use id (possibly level hash) in the future
    str_search = " ".join(args)
    course_name, _ = process.extractOne(str_search, CHOICE_MAPPING.keys())

    # Getting the result set from the running FlyAPI instance and processing the results
    r = httpx.get(f"{BASE_URL}/leaderboards/{course_name}?limit=20")
    data = r.json()

    out_str = f"Results for course: {course_name}\n"
    for i, entry in enumerate(data):
        out_str += f"{i + 1}. {get_steam_username(entry['steam_id'])} - {entry['time'] / 1000}s\n"

    await ctx.send(out_str)


@bot.command(name="lb", help="Get the leaders for all courses")
async def send_course_leaderboards(ctx):
    """
    Gets the single best time for all tracked courses
    :param ctx: default parameter that is injected by bot and handles message response
    :return:
    """
    # Get the endpoint data (top 10?)
    r = httpx.get(f"{BASE_URL}/leaderboards/")

    data = r.json()
    out_str = "Course - User - Time\n"

    for entry in data:
        out_str += f"{entry['course']} - {get_steam_username(entry['steam_id'])} - {entry['time'] / 1000}s\n"

    await ctx.send(out_str)


@bot.command(name="top", help="Get the overall leaders in Fly Dangerous")
async def send_top_players(ctx, limit: Optional[int] = 20):
    """
    Gets the computed top overall rankings for players in Fly Dangerous
    :param limit: Optional int
    :param ctx: default parameter that is injected by bot and handles message response
    :return:
    """
    out_str = ""

    # Get top 20 entries from endpoint
    r = httpx.get(f"{BASE_URL}/leaders/?limit={limit}")
    data = r.json()

    for i, entry in enumerate(data):
        out_str += f"{i + 1}. {entry['steam_username']}: {entry['points']}\n"

    await ctx.send(out_str)


@bot.command(name="score", help="Get the score for a particular user")
async def send_user_score(ctx, steam_id):
    """

    :param ctx:
    :param user_id: int id of a steam user
    :return:
    """
    out_str = ""

    r = httpx.get(f"{BASE_URL}/leaders/?steam_id={steam_id}")
    data = r.json()

    if len(data) == 0:
        await ctx.send(f"No user found with steam id: {steam_id}")

    entry = data[0]
    out_str += f"{entry['steam_id']}: {entry['points']}\n"

    await ctx.send(out_str)


@bot.command(name="fdgh", help="Get the overall leaders in Fly Dangerous")
async def send_github_links(ctx):
    """
    Sends the various github links relating to Fly Dangerous projects
    :param ctx: default parameter that is injected by bot and handles message response
    :return:
    """

    await ctx.send("Main Game (Unity): <https://github.com/jukibom/FlyDangerous>\n"
                   "FlyAPI: <https://github.com/GreatToCreate/FlyAPI>\n"
                   "Discord Bot: <https://github.com/GreatToCreate/FlyBot>\n"
                   "Analytics Runner: <https://github.com/GreatToCreate/FlyAnalytics>\n")


@bot.command(name="calc", help="Explain the calculation methodology for leaders")
async def send_calc_explanation(ctx):
    """
    Sends the explanation for how top players is calculated
    :param ctx: default parameter that is injected by bot and handles message response
    :return:
    """

    await ctx.send("NOTE: Calculation is done by sum(points) where points is 200-leaderboard position or count(" \
                   "leaderboard_entries) - position for courses having fewer than 200 entries\n"
                   "This calculation is not final, and feedback about it is much appreciated in #suggestions")


bot.run(TOKEN)
