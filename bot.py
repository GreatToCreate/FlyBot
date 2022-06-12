import os
import httpx
from discord.ext import commands
from thefuzz import process

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
BASE_URL = os.getenv("BASE_URL")

bot = commands.Bot(command_prefix="!")

CHOICE_MAPPING = {
    "Hold on to your stomach": 8213737,
    "Around The Block": 8213732,
    "Snake": 8310467,
    "You Have Headlights, Right?": 8237753,
    "Speed is Only Half the Battle": 8237657,
    "Thread The Needle": 8310656,
    "A Gentle Start": 8223418,
    "You Might Wanna Hold Back a Bit": 8237749,
    "Crest Loop": 8310286,
    "Limiter Mastery": 8237754,
    "Death Valley": 8237751,
    "Hide and Seek": 8393581,
    "Ups and Downs": 8393529,
    "Around the station": 8236361,
    "Long Road": 8542057,
    "Mountain Spiral": 8558031
}


@bot.command(name="course", help="Get the leaders for a particular course")
async def send_course_leaderboard(ctx, *args):
    """
    Gets the top 20 times for a particular course
    :param ctx: default parameter that is injected by bot and handles message response
    :param args: will be a list of string arguments (whatever the user typed past !course
    :return:
    """
    # Fuzzy search on course to resolve proper course id
    str_search = " ".join(args)
    course_name, _ = process.extractOne(str_search, CHOICE_MAPPING.keys())

    r = httpx.get(f"{BASE_URL}/leaderboards/{course_name}")
    data = r.json()

    out_str = f"Results for course: {course_name}\n"
    for i, entry in enumerate(data):
        out_str += f"{i + 1}. {entry['steam_id']} - {entry['time'] / 1000}s\n"

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
    out_str = "Course - Steam ID - Time\n"

    for entry in data:
        out_str += f"{entry['course']} - {entry['steam_id']} - {entry['time'] / 1000}s\n"

    await ctx.send(out_str)


@bot.command(name="top", help="Get the overall leaders in Fly Dangerous")
async def send_top_players(ctx):
    """
    Gets the computed top overall rankings for players in Fly Dangerous
    :param ctx: default parameter that is injected by bot and handles message response
    :return:
    """
    out_str = "Username: Points\n"

    # Get top 10 entries from endpoint
    r = httpx.get(f"{BASE_URL}/leaders/")
    data = r.json()[:10]

    for i, entry in enumerate(data):
        out_str += f"{i + 1}. {entry['steam_username']}: {entry['points']}\n"

    await ctx.send(out_str)


@bot.command(name="fdgh", help="Get the overall leaders in Fly Dangerous")
async def send_github_links(ctx):
    """
    Returns the various github links relating to Fly Dangerous projects
    :param ctx: default parameter that is injected by bot and handles message response
    :return:
    """
    await ctx.send("https://github.com/jukibom/FlyDangerous")


@bot.command(name="calc", help="Explain the calculation methodology for leaders")
async def send_calc_explanation(ctx):
    """
    Sends the explanation for how top players is calculated
    :param ctx: default parameter that is injected by bot and handles message response
    :return:
    """

    await ctx.send("NOTE: Calculation is done by sum(points) where points is 200-leaderboard position or count(" \
                   "leaderboard_entries) - position for courses having fewer than 200 entries")


bot.run(TOKEN)
