import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, Select, View
import scratchattach as sa
from scratchattach import MultiEventHandler
import pprint
import os
import asyncio
from pyppeteer import launch
from datetime import datetime
from itertools import cycle
import requests
import duckdb
import sys
import io
from openai import OpenAI
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

bot = commands.Bot(command_prefix="s ", intents=discord.Intents.all())
bot_statuses = cycle(["Scratch", "Scratchattach", "ESDB", "Need help ? Do /help :)", "PP by Chagarou", "Follow Fluffygamer_ on scratch !", "Subscribe to Fluffyscratch on youtube !"])

db = duckdb.connect('FluffyBot_private/fluffybot.duckdb')
db.execute("""CREATE TABLE IF NOT EXISTS fluffybot (
           serverid INTEGER PRIMARY KEY,
           language TEXT DEFAULT 'en',
           ai BOOLEAN DEFAULT FALSE,
           embeds BOOLEAN DEFAULT FALSE
)
""")

colour1 = discord.Color(0xF6AB3C) # Scratch orange
colour2 = discord.Color(0xffbe00) # Scratch gold ?
colour3 = discord.Color(0x4e97fe) # Old scratch blue

client = OpenAI(base_url="https://api.penguinai.tech/v1", api_key="sk-1234")

betaembed = discord.Embed(title="Sorry, this command is still in beta !", color=discord.Color.red())

contributors = ["EletrixTime", "TimMcCool"]
devs = []

@tasks.loop(seconds=10)
async def status():
    await bot.change_presence(activity=discord.Game(next(bot_statuses)))

async def dc2scratch(username):
    # Use 'with' to ensure files are properly closed after use
    with open("FluffyBot_private/dcusers.txt") as f1, open("FluffyBot_private/scusers.txt") as f2:
        # Read lines once and store them in variables, stripping newlines or extra whitespace
        dc_users = [line.strip() for line in f1.readlines()]
        sc_users = [line.strip() for line in f2.readlines()]

        # Check if the username exists in the dc_users list
        if username in dc_users:
            index = dc_users.index(username)
            return sc_users[index]  # return the corresponding scuser, no need to strip again
        else:
            return None

async def replace_last_screenshot(url, screenshot_path='screenshot.png'):
    # Check if the screenshot file already exists
    if os.path.exists(screenshot_path):
        # Delete the last screenshot
        os.remove(screenshot_path)
        print(f"Deleted the previous screenshot: {screenshot_path}")
    
    # Launch headless browser using Pyppeteer
    browser = await launch(headless=True)
    page = await browser.newPage()
    
    # Navigate to the URL
    await page.goto(url)
    
    # Take a new screenshot and save it with the same filename
    await page.screenshot({'path': screenshot_path})
    print(f"New screenshot saved as: {screenshot_path}")
    
    # Close the browser
    await browser.close()

def get_server_data(server_id, column_name):
    """
    Retrieves specific data from the 'fluffybot' table in the 'fluffybot.duckdb' database.

    :param server_id: The server ID to look for.
    :param column_name: The column name whose value is requested.
    :return: The value of the requested column for the given server ID, or None if not found.
    """
    try:
        # Parameterized query to fetch the desired column value
        query = f"SELECT {column_name} FROM fluffybot WHERE serverid = ?"
        result = db.execute(query, [server_id]).fetchone()

        # Return the result if found, otherwise None
        return result[0] if result else None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def remove_line_by_index(file_path, index_to_remove):
    # Ouvrir le fichier en mode lecture
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Supprimer la ligne à l'indice spécifique
    if 0 <= index_to_remove < len(lines):
        del lines[index_to_remove]

    # Réécrire le fichier sans la ligne supprimée
    with open(file_path, 'w') as file:
        file.writelines(lines)

def update_pings():
    with open("FluffyBot_private/users2ping.txt") as file:
        whatever = False
        temp = ...
        for item in file.readlines():
            if item == "\n" or item == "":
                    break
            if whatever == True:
                temp = temp, sa.get_user(item.strip()).message_events()
            else:
                whatever = True
                temp = sa.get_user(item.strip()).message_events()
        if len(file.readlines()) - 1  == 1:
            multievents = False
        else:
            multievents = True
        file.close()
    if multievents == True:
        combined = MultiEventHandler(temp)
        print(temp)
        print(combined)
        @combined.event(function=combined) # defines the event for all eventhandlers that were combined
        def on_ready():
            print("Message trackers are up to date !")
        @combined.request(function=combined) # defines the request for all request handlers that were combined
        def your_request():
            ...
        combined.start()
    else:
        events = temp
        @events.event()
        def on_count_change(old_count, new_count): #Called when the user's message count changes.
            print("message count changed from", old_count, "to", new_count)

        @events.event() #Called when the event listener is ready
        def on_ready():
            print("Event listener ready!")

        events.start()

@bot.event
async def on_ready():
    print("FluffyBot is ready !")
    status.start()
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except:
        print("Nah, I don't want to sync my commands today.")

@bot.event
async def on_guild_join(guild):
    db.execute("""
    INSERT INTO fluffybot (serverid) VALUES (?)
    """, [guild.id])

@bot.tree.command(name="modstatus", description="Tells if a project is either FE or NFE.")
async def modstatus(interact : discord.Interaction, project : str):
    id = ''.join(filter(str.isdigit, project))
    project = sa.get_project(id)
    
    embeded_msg = discord.Embed(title="This project is...")
    
    if project.moderation_status() == "notsafe":
        embeded_msg.description = "<:Nope:1333795409403052032>Not Safe (NFE) !<:Nope:1333795409403052032>"
        embeded_msg.color = discord.Color.red()
    else:
        embeded_msg.description = "<:Verified:1333795453250175058>Safe (FE) !<:Verified:1333795453250175058>"
        embeded_msg.color = discord.Color.green()
    
    embeded_msg.set_footer(text=f"Project ID : {id}")
    await interact.response.send_message(embed=embeded_msg)

@bot.tree.command(name="help", description="Need help ? No problem ! All commands and their usage are here.")
async def help(interact : discord.Interaction):
    await interact.response.send_message(
    embed=discord.Embed(
        title="<:giga404:1330551323610976339>Help",
        description=(
            "🎉 EVENT COMMANDS 🗓️ :\n"
            "<:2025:1333042237876998224> **/2025** ║ Returns the current new year projects on trending !\n"
            "\n═══════════════════════════\n\n"
            "<:New1:1333793269636661288><:New2:1333793304822808677> <:search:1333037655902130247> **/about** ║ Gives interesting facts and stats about this bot !\n"
            "🔗 **/bind** ║ Allows you to bind your scratch account to your discord account, through a simple authentication process.\n"
            "<:newscratcher:1330550984971259954> **/check_username** ║ Tells you if a username is available or not, so you can claim it if you want to!\n"
            "📧 **/embed** ║ Gives the embed version of a project, useful for websites.\n"
            "🔔 **/followedby** ║ Checks if a user is followed by another user!\n"
            "📃 **/forums** ║ Gets all topics in a forum category, with their stats. Language topics not supported yet because of discord limitations <a:sadcat:1330550126745227335>\n"
            "🩺 **/health** ║ Gets 'health data' about Scratch such as version, uptime, and complex data. Made for very advanced tech users.\n"
            "✅ **/modstatus** ║ Says if a project is rated either For Everyone (FE) or Not For Everyone (NFE).\n"
            "🆕 **/newestprojects** ║ Gets newly shared projects.\n"
            "<:ocular:1333041343668158515> **/bettersearch**  Allows searching projects just like in scratch, but better. For example, projects with high ids do show up, not like on scratch. Powered by ESDB.\n"
            "📈 **/ontrend** ║ Checks if a project is on trending in a certain language (must be precised with 2 letters, such as en for english or fr for french) with a custom limit of how many projects the bot will look at.\n"
            "💻 **/project** ║ Gives a lot of useful information about a specific project.\n"
            "🎲 **/randomprojects** ║ Returns a pre-defined number of clickable random project titles. Powered by ESDB.\n"
            "📋 **/scratchactivity** ║ Find a user's past activity on scratch. Because of API limitations, sometimes you will see '.' as where an action took place. WARNING : TOO HIGH LIMIT = ERROR\n"
            "<:ScratchTeam:1330549427580178472> **/scratchteam** ║ Gets all scratch team members !\n"
            "<:tts:1344271467876974602> **/scratchtts** ║ Allows you to use text to speech... Using scratch's text to speech extension !\n"
            "<:ScratchCat:1330547949721223238> **/s_profile** ║ Allows you to look at someone's profile easily, with high precision.\n"
            "🗂️ **/studio** ║ Allows you to preview a studio.\n"
            "🏷️ **/topic** ║ Previews a forum topic, not that useful right now.\n"
            "🌟 **/trendscore** ║ Gives a trending score for a specific project, mainly to compare how trendy 2 projects are, can also be used to approximately predict if a project may go on trending.\n"
            "🌐 **/webstats** ║ Gets statistics about Scratch, such as total projects count.\n"
            "<:youtube:1340017536409927711> **/yttoscratch** ║ Converts any youtube video link into a forum video link. Better for sharing youtube videos on Scratch.\n"
            "\n\nNeed assistance, have a suggestion or found a bug? Join our [🔧 support server](https://discord.gg/dgymF2Ye4k)!"
            "\nBot profile picture by [<:chagarou:1340009091929608232>Chagarou](https://youtube.com/@Chagarou-MC), all rights reserved to them and the FluffyBot developement team."
        ),
        color=colour1,
    )
)

@bot.tree.command(name="embed", description="Gives an embeded version of the specified project, mainly for websites.")
async def embed(interact : discord.Interaction, project : str):
    id = ''.join(filter(str.isdigit, project))
    project = sa.get_project(id)
    
    link = project.embed_url
    embeded_msg = discord.Embed(title="This project is now embedded ! <:embed:1343565862077988904>", description=f"🔗 Link : {link}", color=colour1)
    await interact.response.send_message(embed=embeded_msg)

@bot.tree.command(name="webstats", description="Returns statistics about scratch's website.")
async def webstats(interact : discord.Interaction):
    embeded_message = discord.Embed(title=":bar_chart: Statistics about Scratch :bar_chart:")
    embeded_message.description = (
    f"**On scratch, there are :**\n\n"
    f"- {sa.total_site_stats().get('PROJECT_COUNT')} projects 💻\n"
    f"- {sa.total_site_stats().get('USER_COUNT')} users <:together:1330551758166036500>\n"
    f"- {sa.total_site_stats().get('STUDIO_COUNT')} studios 🗂️\n\n"
    f"**There are {sa.total_site_stats().get('COMMENT_COUNT')} comments 💬 :**\n\n"
    f"- {sa.total_site_stats().get('PROFILE_COMMENT_COUNT')} are profile comments <:together:1330551758166036500>\n"
    f"- {sa.total_site_stats().get('PROJECT_COMMENT_COUNT')} are project comments 💻\n"
    f"- {sa.total_site_stats().get('STUDIO_COMMENT_COUNT')} are studio comments 🗂️"
)
    
    embeded_message.color = colour1
    await interact.response.send_message(embed=embeded_message)

@bot.tree.command(name="studio", description="Reads informations about a studio.")
async def studio(interact : discord.Interaction, studio : str):
    id = ''.join(filter(str.isdigit, studio))
    studio = sa.get_studio(id)
    
    if studio.open_to_all:
        access = "Everyone"
    else:
        access = "Only curators"
    
    msg = discord.Embed(title=studio.title)
    msg.set_image(url=studio.image_url)
    msg.set_thumbnail(url=studio.host().icon_url)
    msg.description=(
        f"Owned by **{studio.host()}**, with id {studio.host_id}\n"
        f"**{access}** can add projects.\n\n"
        "**This studio has :**\n"
        f"- {studio.project_count} projects\n"
        f"- {studio.follower_count} followers\n"
        f"- {studio.manager_count} managers\n\n"
        "**Description :**\n"
        f"{studio.description}"
    )
    msg.set_footer(text=f"Studio id : {studio.id}, link : https://scratch.mit.edu/studios/{studio.id}")
    msg.color = colour1
    await interact.response.send_message(embed=msg)

@bot.tree.command(name="s_profile", description="Take a look at a scratcher's profile !")
async def s_profile(interact : discord.Interaction, user : str):
    await interact.response.defer()
    embeded_message = discord.Embed(title=user)

    try:
        usr = sa.get_user(user)
        # Rank finder
        if usr.is_new_scratcher():
            rank = "<:newscratcher:1330550984971259954> New scratcher"
        elif usr.scratchteam:
            rank = "<:ScratchTeam:1330549427580178472> Scratch team member"
        elif usr.follower_count() > 10000:
            rank = "<:forumcool:1341109220119941140> Legend scratcher (>10 000 followers)"
        elif usr.name in contributors:
            rank = "<:coolcat:1330548833209417821> Contributor"
        elif usr.name in devs:
            rank = "<:code:1333794362315767870> FluffyBot dev"
        elif usr.name == "Fluffygamer_":
            rank = "<:Verified:1333795453250175058> FluffyBot owner"
        else:
            rank = "<:ScratchCat:1330547949721223238> Scratcher"
            
        embeded_message.description = (
    f"**{rank}**\n\n"
    f"*Joined scratch on {usr.join_date} - Lives in {usr.country}* \n"
    f"**{user}** has **{usr.message_count()}** message(s). \n\n"
    f"**<:ocular:1333041343668158515>Ocular :** \n"
    f"Color : {usr.ocular_status().get('color')} Status : {usr.ocular_status().get('status')}* \n\n"
    f"**About {user}** : \n"
    f"{usr.about_me} \n\n"
    f"**What is {user} working on** : \n"
    f"{usr.wiwo}\n\n"
    f"**{user}** is followed by **{usr.follower_count()}** scratchers, "
    f"and is following **{usr.following_count()}** scratchers.\n"
    f"They also loved **{usr.loves_count()} projects** and favourited "
    f"**{usr.favorites_count()} projects** in total.\n\n"
    f"{usr.featured_data()['label']} : [{usr.featured_data()['project']['title']}](https://scratch.mit.edu/projects/{usr.featured_data()['project']['id']})"
)
        
        embeded_message.set_thumbnail(url=usr.icon_url)
        embeded_message.set_footer(text=f"{user}'s ID : {usr.id}")
        embeded_message.color = colour1
        embeded_message.set_image(url=usr.featured_data()['project']['thumbnail_url'])
        await interact.followup.send(embed=embeded_message)
    except:
        await interact.followup.send(embed=discord.Embed(title="Error :", description="An error occured. Does this user exist ?<:giga404:1330551323610976339>", color=discord.Color.red()))

@bot.tree.command(name="check_username", description="Checks if a scratch username is already claimed or not !")
async def check_username(interact : discord.Interaction, username : str):
    msg = discord.Embed(title="This username is...")
    if sa.check_username(username) == "valid username":
        msg.description = "Avaliable ! :partying_face: \n [Claim it](<https://scratch.mit.edu/join>) <:happycat:1330550203756970127>"
        msg.color = discord.Color.green()
    else:
        msg.description = f"Taken ! :smiling_face_with_tear:\n Link : https://scratch.mit.edu/users/{username} <a:sadcat:1330550126745227335>"
        msg.color = discord.Color.red()
    await interact.response.send_message(embed=msg)

@bot.tree.command(name="newestprojects", description="Get all the newest published projects.")
async def newestprojects(interact : discord.Interaction):
    await interact.response.send_message(embed=discord.Embed(title="<:newscratcher:1330550984971259954>Newest scratch projects :", description=pprint.pformat(sa.newest_projects()), color=colour1))

@bot.tree.command(name="yttoscratch", description="Converts a youtube video link into a scratch forums link.")
async def yttoscratch(interact : discord.Interaction, link : str):
    await interact.response.send_message(embed=discord.Embed(title="Conversion finished ! Link :", description=sa.youtube_link_to_scratch(link), color=colour1))

@bot.tree.command(name="health", description="Gets health data about scratch.")
async def scratchstatus(interact : discord.Interaction):
    # The original description string
    original_description = pprint.pformat(sa.get_health())

    # Remove '{', '}', and make text between single quotes bold
    modified_description = re.sub(r"[{},]", "", original_description)  # Remove '{' and '}'
    modified_description = re.sub(r"'([^']+)'", r'**\1**', modified_description)  # Make text between single quotes bold

    await interact.response.send_message(
    embed=discord.Embed(
        title="❤️‍🩹 Scratch's health status :",
        description=f"{modified_description}\n\n## Tip : press control + F (or command + F on mac) and search the health data you're looking for.",
        color=colour1
    )
)

@bot.tree.command(name="followedby", description="Checks if a user is followed by another user !")
async def followedby(interact : discord.Interaction, username : str, followed_by : str):
    if sa.get_user(username).is_followed_by(followed_by) == True:
        await interact.response.send_message(embed=discord.Embed(title=username, description=f"Is followed by {followed_by} !", color=discord.Color.green()))
    else:
        await interact.response.send_message(embed=discord.Embed(title=username, description=f"Is not followed by {followed_by} !", color=discord.Color.red()))

@bot.tree.command(name="bind", description="Binds your scratch account to your discord account.")
async def bind(interact : discord.Interaction, username : str):
    await interact.response.defer()
    target = str(interact.user)
    found = False
    user = sa.get_user(username)
    
    # Verifies if the user already has a binded account.
    with open("FluffyBot_private/dcusers.txt") as file:
        for item in file.readlines():
            if item.strip() == target:
                found = True
                break
        file.close()
    
    # If user already has a binded account, tell it to them. Else, bind user.
    if found == True:
        binded = await dc2scratch(interact.user.name)
        await interact.followup.send(embed=discord.Embed(title="<:Nope:1333795409403052032>A scratch account is already linked to your discord account !<:Nope:1333795409403052032>", description=f"Your account is linked to **{binded}**.\n FluffyBot can't handle replacements yet.", color=discord.Color.red()))
    else:
        verificator = user.verify_identity()
        if verificator.check() == True:
            with open("FluffyBot_private/dcusers.txt", "a+") as file:
                file.write(f"{str(interact.user)}\n")
                file.close()
            with open("FluffyBot_private/scusers.txt", "a+") as file:
                file.write(f"{str(username)}\n")
                file.close()
            await interact.followup.send(embed=discord.Embed(title="<:Verified:1333795453250175058>Success !<:Verified:1333795453250175058>", description=f"Your discord account is now linked to your scratch account, {username} !", color=discord.Color.green()))
        else:
            await interact.followup.send(embed=discord.Embed(title="<:wait:1333795784357056552>Wait !<:wait:1333795784357056552>", description=f"To be sure this scratch account is really yours, please comment **'{verificator.code}'** on this project : {verificator.projecturl}. Then, run this command again.", color=colour1))

@bot.tree.command(name="toggle_ping", description="Enable or disable discord ping when recieving a new message. Requires binding.")
async def toggle_ping(interact : discord.Interaction):
    if interact.user.name == "fluffygamer.":
        target = str(interact.user)
        found = False
        i = -1
        with open("FluffyBot_private/dcusers.txt") as file:
            for item in file.readlines():
                i = i + 1
                if item.strip() == target:
                    found = True
                    break
            file.close()
        print(i)
        if found == True:
            with open("FluffyBot_private/scusers.txt") as file:
                s_user = file.readlines()[i]
                file.close()
            print(s_user)
            target = s_user
            found = False
            i = 0
            with open("FluffyBot_private/users2ping.txt") as file:
                for item in file.readlines():
                    i = i + 1
                    if item.strip() == target:
                        found = True
                        break
            if found == True:
                remove_line_by_index("users2ping.txt", i - 1)
                update_pings()
                await interact.response.send_message(embed=discord.Embed(title="Success !", description="Pinging when recieving a scratch message is now disabled for your account !", color=discord.Color.green()))
            else:
                with open("FluffyBot_private/users2ping.txt", "a+") as file:
                    file.write(f"{s_user}\n")
                    update_pings()
                    await interact.response.send_message(embed=discord.Embed(title="Success !", description="Pinging when recieving a scratch message is now enabled for your account !", color=discord.Color.green()))
        else:
            await interact.response.send_message(embed=discord.Embed(title="Error :", description="You need to bind your scratch account to use this command. To bind your scratch account, use /bind !", color=discord.Color.red()))
    else:
        await interact.response.send_message(embed=betaembed)

@bot.tree.command(name="2025", description="Take a look at the best new year projects easily !")
async def event(interact : discord.Interaction):
    message = ""
    projects = sa.search_projects(query="new year", mode="trending", language="en", limit=10, offset=0)
    for item in projects:
        message = f"{message}\n\n **[{item.title}](<https://scratch.mit.edu/projects/{item.id}>)** by [{item.author().username}](scratch.mit.edu/users/{item.author().username})"
    await interact.response.send_message(embed=discord.Embed(title="<:2025:1333042237876998224>Top 10 trending new year projects<:2025:1333042237876998224> :", description=message, color=colour1))

@bot.tree.command(name="project", description="Gets a lot of informations about a project.")
async def project(interact : discord.Interaction, project : str):
    id = ''.join(filter(str.isdigit, project))
    project = sa.get_project(id)
    
    msg = discord.Embed(title=f"{project.title} :")
    
    # Fields are used for project statistics
    msg.add_field(name="Views :", value=f"{project.views} :eye:")
    msg.add_field(name="Loves :", value=f"{project.loves} :heart:")
    msg.add_field(name="Faves :", value=f"{project.favorites} :star:")
    msg.add_field(name="Loves per view :", value=f"{round(project.loves / project.views, 2)} :heart: / :eye:")
    msg.add_field(name="Faves per view :", value=f"{round(project.favorites / project.views, 2)} :star: / :eye:")
    msg.add_field(name="Loves per view (%) :", value=f"{round((project.loves / project.views) * 100)} :heart: / 100 :eye:")
    msg.add_field(name="Faves per view (%) :", value=f"{round((project.favorites / project.views) * 100)} :star: / 100 :eye:")
    
    msg.color = colour1
    msg.description = (
        f"Made by {project.author_name}, at {project.share_date} (Last modified at {project.last_modified})\n"
        f"<:Turbowarp:1330552274774396979>Turbowarp link : https://turbowarp.org/{id}\n\n"
        f"**Description :**\n{project.instructions}\n\n"
        f"**Notes and Credits :**\n{project.notes}\n\n"
        "<:scratchstats:1330550531864662018> Statistics :\n"
    )
    msg.set_image(url=project.thumbnail_url)
    
    await interact.response.send_message(embed=msg)

@bot.tree.command(name="remixtree", description="Gets a project's remix tree.")
async def remixtree(interact : discord.Interaction, project : str):
    if interact.user.name == "fluffygamer.":
        id = ''.join(filter(str.isdigit, project))
        asyncio.get_event_loop().run_until_complete(replace_last_screenshot(f"scratch.mit.edu/projects/{id}/remixtree"))
        await interact.response.send_message(file=discord.File('screenshot.png'))
    else:
        await interact.response.send_message(embed=betaembed)

@bot.tree.command(name="trendscore", description="Gets a project's trending potential, represented as a score number.")
async def trendscore(interact : discord.Interaction, project : str):
    id = ''.join(filter(str.isdigit, project))
    proj = sa.get_project(id)
    diff = datetime.now() - datetime.strptime(proj.share_date, "%Y-%m-%dT%H:%M:%S.%fZ") # converts weird API date to python understandable date.
    await interact.response.send_message(embed=discord.Embed(title=f"<:popular:1330550904813916272>'{proj.title}' has a trending score of {round(proj.views / (diff.days * 24 + diff.seconds / 3600), 3)} !<:popular:1330550904813916272>", color=discord.Colour.gold()))

@bot.tree.command(name="ontrend", description="Checks if a project is on trending in a specific language.")
async def ontrend(interact : discord.Interaction, project : str, language : str, limit : int):
    i = 0
    found = False
    id = ''.join(filter(str.isdigit, project))
    for item in sa.explore_projects(language=language, limit=limit, mode="trending"):
        i = i + 1
        if item.id == int(id):
            found = True
            break
    if found:
        await interact.response.send_message(embed=discord.Embed(title="Project found !", description=f"This project is on trending, at the **{i}th** position !", colour=discord.Color.green()))
    else:
        await interact.response.send_message(embed=discord.Embed(title="Project not found !", description="This project is not on trending !", color=discord.Colour.red()))

@bot.tree.command(name="tips", description="Gives you tips and tricks for scratch !")
async def tips(interact : discord.Interaction):
    msg = discord.Embed()
    msg.title = "Here are some helpful tips and tricks for scratch !"
    msg.color = colour1
    msg.description = (
    "**Cool emojis compatible with scratch:**\n\n"
    "☠️ ◼️ ◻️ ⚪ ⚫ 🔲 🔳 🔴 🔵 🔶 🔷 🔸 🔹 🟠 🟡 🟢 🔘 🟣 🟤 🔵 🟦 🟩 🟧 🟨 🟩\n"
    "🖤 🤖 📞 ⌛ ⏰ ⏱ 🕰 🔋 🔌 🖤 🛠 🛡 📱 📝 🔨 📖 🍵 ⚽ 🏀 ⚾ 🏐 🏆 🎮 🎯 🚗 🏎\n"
    "💣 🔑 🔒 🔓 🎁 🏠 🏡 🏢 🔑 🔒 🔒 🔌 🏠 🏡 🔷 🌐 💬 ✉ 🧩 🌟 🕹️ 🎮 🖋️ 🎨\n"
    "🎧 🎤 📷 📹 🎬 🏞 🖼 🖊️ 🎞 🎟 🎪 🎭 🎬 🕹️ 🎮 ⌨ 🖱 🔍 📝 🏁 🏆 🏅 🏆\n"
    "🏅 🏆 🏁 🏟 ⛹️‍♂️ 🏋️‍♀️ 💆‍♀️ 🚴‍♀️ 🏊‍♂️ 🤾‍♀️ 🤽‍♀️ 🧘‍♀️ 🎾 🏸 🏓 🏒\n"
    "🎳 🏏 🎯 ⚽ 🏀 🏐 🏓 🏒 🏆 🏅 🏆 ⛳ 🎯 🏆 🏅 🏅 🔗 📎 🖇 🏷️ 🎀 🎁 🧧\n\n"
    "**Scratchmojis :**\n"
    "Cats :\n\n"
    "<:cat:1330548816843374655> <:separator:1333808735101124668> `_:)_`\n"
    "<:awwcat:1330548798841163840> <:separator:1333808735101124668> `_:D_`\n"
    "<:coolcat:1330548833209417821> <:separator:1333808735101124668> `_B)_`\n"
    "<:tongueoutcat:1330549148155514981> <:separator:1333808735101124668> `_:P_`\n"
    "<:winkcat:1330549190169727071> <:separator:1333808735101124668> `_;P_`\n"
    "<:lolcat:1330548983873142854> <:separator:1333808735101124668> `_:'P_`\n"
    "<:upsidedowncat:1330549166207664209> <:separator:1333808735101124668> `_P:_`\n"
    "<:huhcat:1330548916223217747> <:separator:1333808735101124668> `_:3_`\n"
    "<:loveitcat:1330549053741731942> <:separator:1333808735101124668> `_<3_`\n"
    "<:favitcat:1330548853317042196> <:separator:1333808735101124668> `_**_`\n"
    "<:rainbowcat:1330549122855600262> <:separator:1333808735101124668> `_:))_`\n"
    "<:pizzacat:1330549104249667655> <:separator:1333808735101124668> `_:D<_`\n\n"
    "Other :"
)

    msg.add_field(name="<:meow:1330549076223070269>", value="`_meow_`")
    msg.add_field(name="<:Gobo:1330552595390926948>", value="`_gobo_`")
    msg.add_field(name="<:10mil:1330548335471493241>", value="`_10mil_`")
    msg.add_field(name="<:waffle:1335195624127336451>", value="`_waffle_`")
    msg.add_field(name="<:taco:1330548746156638208>", value="`_taco_`")
    msg.add_field(name="<:sushi:1330548721355722817>", value="`_sushi_`")
    msg.add_field(name="<:apple:1330548350663131247>", value="`_apple_`")
    msg.add_field(name="<:broccoli:1330548400214511718>", value="`_broccoli_`")
    msg.add_field(name="<:pizza:1330548624215642183>", value="`_pizza_`")
    msg.add_field(name="<:candycorn:1330548437753794640>", value="`_candycorn_`")
    msg.add_field(name="<:map:1330548598508879922>", value="`_map_`")
    msg.add_field(name="<:camera:1330548417684045854>", value="`_camera_`")
    msg.add_field(name="<:suitcase:1330548697359974512>", value="`_suitcase_`")
    msg.add_field(name="<:compass:1330548457357967360>", value="`_compass_`")
    msg.add_field(name="<:binoculars:1330548366064484422>", value="`_binoculars_`")
    msg.add_field(name="<:cupcake:1330548475359920141>", value="`_cupcake_`")
    msg.add_field(name="<:pride:1330548644859871253>", value="`_pride_`")
    msg.add_field(name="<:blm:1330548384007852032>", value="`_blm_`")

    await interact.response.send_message(embed=msg)

@bot.tree.command(name="randomprojects", description="Shows a number of random scratch projects, powered by ESDB.")
async def randomprojects(interact : discord.Interaction, number :  int):
    response = requests.get(f"https://explore.eletrix.fr/api/projects/random?limit={number}")
    if response.status_code == 200:
        message = ""
        for item in response.json():
            message = f"{message} [**{item['title']}**](https://scratch.mit.edu/projects/{item['id']}) :\n\n"
        msg = discord.Embed()
        if number == 1:
            msg.title = "Here is 1 random project !"
        else:
            msg.title = f"Here are {number} random projects !"
        msg.description = message
        msg.color = colour1
        await interact.response.send_message(embed=msg)
    else:
        await interact.response.send_message(embed=discord.Embed(title=f"Whoops, looks like we've got an error {response.status_code} !<:giga404:1330551323610976339>", color=discord.Color.red()))

@bot.tree.command(name="bettersearch", description="Allows you to search projects without bugs such as <900 million ids. Powered by ESDB.")
async def bettersearch(interact : discord.Interaction, query : str):
    response = requests.get(f"https://explore.eletrix.fr/api/projects/search?search={query}")
    if response.status_code == 200:
        message = ""
        for item in response.json():
            message = f"{message} [**{item['title']}**](https://scratch.mit.edu/projects/{item['id']}) :\n\n"
        msg = discord.Embed()
        msg.title = f"<:search:1333037655902130247>Results for '{query}' :"
        msg.description = message
        msg.color = colour1
        await interact.response.send_message(embed=msg)
    else:
        await interact.response.send_message(embed=discord.Embed(title=f"Whoops, looks like we've got an error {response.status_code} !<:giga404:1330551323610976339>", color=discord.Color.red()))

@bot.tree.command(name="scratchactivity", description="Shows the scratch activity of a user")
async def activity(interact : discord.Interaction, user : str, limit : str):

    await interact.response.defer()

    msg = discord.Embed(title="This user 's past scratch activity :", color=colour1)
    result = ""
    where = ""

    for item in sa.get_user(user).activity(limit=limit):
        result = (
            f"{result}\n"
            f"`{user}` made action {item.type} at "
        )
        if type(item.target()) == sa.User:
            where = f"[{item.target().username}](https://scratch.mit.edu/users/{item.target().username})"
        if type(item.target()) == sa.Project:
            where = f"[{item.target().id}](https://scratch.mit.edu/projects/{item.target().id})"
        if type(item.target()) == sa.Studio:
            where = f"[{item.target().id}](https://scratch.mit.edu/studios/{item.target().id})"
        if type(item.target()) == sa.Comment:
            where = "Comment (I ain't writing 100 lines to support comments links because of scratchattach limitations, sorry)"
        result = f"{result}{where}."

    msg.description = result
    await interact.followup.send(embed=msg)

@bot.tree.command(name="mutualfollowers", description="Finds mutual followers between 2 users.")
async def mutualfollowers(interact: discord.Interaction, user_1: str, user_2: str):
    await interact.response.defer()
    msg = discord.Embed()
    count = 0
    desc = ""
    followers1 = sa.get_user(user_1).follower_names(limit=int(sa.get_user(user_1).follower_count()))
    followers2 = sa.get_user(user_2).follower_names(limit=int(sa.get_user(user_2).follower_count()))

    for item in followers1:
        if item in followers2:
            count = count + 1
            desc = f"{desc}\n{item}"

    if count == 0:
        await interact.followup.send(embed=discord.Embed(title=f"{user_1} and {user_2} have no mutual followers!", color=colour1))
    else:
        msg.title = f"<:together:1330551758166036500>{user_1} and {user_2} have {count} mutual followers<:together:1330551758166036500> :"
        msg.description = desc
        msg.color = colour1
        await interact.followup.send(embed=msg)

@bot.tree.command(name="recommend", description="Gives you recommended scratchers, projects or studios customised for you.")
@app_commands.choices(type=[
    app_commands.Choice(name="User", value="user"),
    app_commands.Choice(name="Project", value="project"),
    app_commands.Choice(name="Studio", value="studio")
])
async def recommend(interact : discord.Interaction, type : str):
    if interact.user.name == "fluffygamer.":
        scratch = dc2scratch(interact.user.name)
        if not scratch == None:
            sa.get_user(scratch)
        else:
            interact.response.send_message(embed=discord.Embed(title="Sorry, you need to /bind your account so we can recommend you things !", color=discord.Color.red()))
    else:
        await interact.response.send_message(embed=betaembed)

@bot.tree.command(name="scratchgpt", description="EXPERIMENTAL - Chat with a powerful AI to get scratch related help !")
async def scratchgpt(interact : discord.Interaction, prompt : str):
    await interact.response.defer()

    if get_server_data(interact.guild_id, "ai"):
        url = "https://api.penguinai.tech/v1/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4-turbo",
            "messages": [
                {"role": "scratcher", "content": f"Answer this knowing you're a scratch assistant and number one scratch discord bot called FluffyBot and like scratching, coding and helping people : {prompt}"}
            ]
        }
        response = requests.post(url=url, headers=headers, json=data)
        if response.status_code == 200:
            # Assuming the response content is in JSON format, use .json() to parse it
            data = response.json()  # This will already be a dictionary

            # Extract the content
            content = data['choices'][0]['message']['content']

            # Respond with the answer
            await interact.followup.send(embed=discord.Embed(description=content, color=colour1))
        else:
            await interact.response.send_message(embed=discord.Embed(color=discord.Color.red(), title="Sorry, the API we use appears to be down :/"))
    else:
        if interact.user.guild_permissions.administrator:
            await interact.followup.send(embed=discord.Embed(color=discord.Color.red(), title=":x: Sorry, AI is not allowed on this server. Since you're a server admin, you can change this using /settings."))
        else:
            await interact.followup.send(embed=discord.Embed(color=discord.Color.red(), title=":x: Sorry, AI is not allowed on this server."))

ai_state = tuple
embed_state = tuple

# Global dictionary to store button states
button_states = {}

# Slash command for settings
@bot.tree.command(name="settings", description="Configure FluffyBot settings for this server")
async def settings(interaction: discord.Interaction):
    if interaction.user.name == "fluffygamer.":
        # Button current color state
        ai_state = discord.ButtonStyle.green if get_server_data(interaction.guild_id, "ai") else discord.ButtonStyle.red
        embed_state = discord.ButtonStyle.green if get_server_data(interaction.guild_id, "embeds") else discord.ButtonStyle.red

        # Create the embed (without content for now)
        embed = discord.Embed(title="Settings", description="Please select your preferences.", color=discord.Color.blue())

        # Create the buttons with initial states (green for AI and red for Embeds)
        ai_button = Button(label="AI", style=ai_state, custom_id="ai_button")
        embeds_button = Button(label="Embeds", style=embed_state, custom_id="embeds_button")

        # Define the dropdown (Select menu)
        language_select = Select(
            placeholder="Select your language here",
            options=[
                discord.SelectOption(label="English", value="en"),
                discord.SelectOption(label="Français", value="fr"),
            ]
        )

        # Define the view (a container for buttons and dropdown)
        view = View()
        view.add_item(ai_button)
        view.add_item(embeds_button)
        view.add_item(language_select)

        # Save initial button states to the global dictionary
        button_states["ai_button"] = ai_state
        button_states["embeds_button"] = embed_state

        # Send the embed with the UI elements
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=betaembed)

# Button interaction handlers
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        button_id = interaction.data['custom_id']

        # Make sure the button_id exists in button_states
        if button_id not in button_states:
            # If it's not in button_states, initialize with a default value
            button_states[button_id] = discord.ButtonStyle.red  # Default color

        current_style = button_states[button_id]

        # Toggle the button's color (green <-> red)
        new_style = discord.ButtonStyle.green if current_style == discord.ButtonStyle.red else discord.ButtonStyle.red

        # Update the state in button_states
        button_states[button_id] = new_style

        # Rebuild the button with the new style
        if button_id == "ai_button":
            new_button = Button(label="AI", style=new_style, custom_id="ai_button")
        elif button_id == "embeds_button":
            new_button = Button(label="Embeds", style=new_style, custom_id="embeds_button")

        # Rebuild the view with the updated button
        ai_button = Button(label="AI", style=button_states["ai_button"], custom_id="ai_button")
        embeds_button = Button(label="Embeds", style=button_states["embeds_button"], custom_id="embeds_button")
        language_select = Select(
            placeholder="Select your language here",
            options=[
                discord.SelectOption(label="English", value="en"),
                discord.SelectOption(label="Français", value="fr"),
            ]
        )

        view = View()
        view.add_item(ai_button)
        view.add_item(embeds_button)
        view.add_item(language_select)

        # Edit the original message to reflect the updated button colors
        await interaction.response.edit_message(view=view)

        # Acknowledge the button press
        await interaction.followup.send(f"The {button_id} color changed to {'green' if new_style == discord.ButtonStyle.green else 'red'}!", ephemeral=True)

@bot.tree.command(name="about", description="Everything you need to know about FluffyBot !")
async def about(interact : discord.Interaction):
    from collections import Counter

    # Dictionary to hold language counts
    language_counts = Counter()

    # Loop through all the guilds (servers) the bot is in
    for guild in bot.guilds:
        # Increment the language count for this guild's locale
        language_counts[guild.preferred_locale] += 1

    # Displays top 2 most common languages
    top_languages = language_counts.most_common(2)

    # Display the top languages
    langs = f"\n**Top Languages :**\n"
    for i, (lang, count) in enumerate(top_languages, 1):
        langs = (f"{langs}\n**{i}.** {lang} with {count} servers")
    

    unique_members = set()  # Set to hold unique user IDs

    # Loop through all the guilds (servers) the bot is in
    for guild in bot.guilds:
        # Add the IDs of all members to the set
        unique_members.update(member.id for member in guild.members)
    
    # The size of the set is the count of unique members
    total_unique_members = len(unique_members)

    msg = discord.Embed(title="🤔 About FluffyBot <:BestBotEver:1333794479932575746> :")
    msg.description = (
        "<:together:1330551758166036500> **Contributors :**\n\n"
        "- <:fluffy:1340009005581598820>**Fluffy** <:separator:1333808735101124668> Basically the bot founder and owner, that coded FluffyBot.\n"
        "- <:chagarou:1340009091929608232>**Chagarou** <:separator:1333808735101124668> The amazing artist that made FluffyBot's profile picture for completely free.\n"
        "- <:timmccool:1340009073990701238>**TimMcCool** <:separator:1333808735101124668> Maker of scratchattach, the python library this bot is mainly based on.\n"
        "- <:eletrixtime:1340009103019348020>**ElectrixTime** <:separator:1333808735101124668> Maker of ESDB, a really cool projects database that powers 2 really cool FluffyBot services.\n"
        "- 🫵**You** <:separator:1333808735101124668> FluffyBot user, motivating me to continue updating this bot !\n"
        "\n📍 **Where is FluffyBot ?** 🌎\n\n"
        f"📈 FluffyBot is in {len(bot.guilds)} servers, and used by {total_unique_members} unique scratchers worldwide. <:together:1330551758166036500>\n"
        f"{langs}"
        "\n\n🔗 **Links :**\n\n"
        "- [➕ Add FluffyBot](https://discord.com/oauth2/authorize?client_id=1300009645078876170&permissions=274877990912&integration_type=0&scope=bot)\n"
        "- [🔧 Support server](https://discord.gg/dgymF2Ye4k)\n"
        "⬆️ Help FluffyBot by upvoting it there ⬆️ :\n"
        "- [Discordbotlist.com](https://discordbotlist.com/bots/fluffybot)\n"
        "- [Discordlist.gg](https://discordlist.gg/bot/1300009645078876170)"
    )
    msg.color = colour1

    await interact.response.send_message(embed=msg)

@bot.tree.command(name="scratchteam", description="Gets all scratch team members !")
async def scratchteam(interact : discord.Interaction):
    msg = discord.Embed(title="<:ScratchTeam:1330549427580178472> These are all the members of the scratch team :", color=colour1)
    for item in sa.scratch_team_members():
        msg.description = f"{msg.description}\n**[{item['userName']}](https://scratch.mit.edu/users/{item['userName']})** <:separator:1333808735101124668> {item['name']}"
    await interact.response.send_message(embed=msg)

@bot.tree.command(name="scratchtts", description="Use scratch's Text to Speech in discord !")
@app_commands.choices(voice=[
    app_commands.Choice(name="Alto", value="alto"),
    app_commands.Choice(name="Tenor", value="tenor"),
    app_commands.Choice(name="Squeak", value="squeak"),
    app_commands.Choice(name="Giant", value="giant"),
    app_commands.Choice(name="Kitten", value="kitten")
])
@app_commands.choices(language=[
    app_commands.Choice(name="English (US)", value="en-US"),
    app_commands.Choice(name="French", value="fr")
])
async def scratchtts(interact : discord.Interaction, text : str, voice : str, language : str):
    await interact.response.defer()

    audio_data, playback_rate = sa.text2speech(text=text, voice_name=voice, language=language)

    # Create a file-like object from the audio data (the response.content from text2speech)
    audio_file = discord.File(io.BytesIO(audio_data), filename="output.mp3")

    # Send the message with the file
    await interact.followup.send(
        embed=discord.Embed(title="Done! Here is the output ⬆️", color=colour1),
        file=audio_file
    )

@bot.tree.command(name="forums", description="Check for topics in any forums category !")
@app_commands.choices(category=[
    app_commands.Choice(name="Announcements", value=5),
    app_commands.Choice(name="New Scratchers", value=6),
    app_commands.Choice(name="Help with Scripts", value=7),
    app_commands.Choice(name="Show and Tell", value=8),
    app_commands.Choice(name="Project Ideas", value=9),
    app_commands.Choice(name="Collaboration", value=10),
    app_commands.Choice(name="Requests", value=11),
    app_commands.Choice(name="Project Save & Level Codes", value=60),
    app_commands.Choice(name="Questions about scratch", value=4),
    app_commands.Choice(name="Suggestions", value=1),
    app_commands.Choice(name="Bugs and Glitches", value=3),
    app_commands.Choice(name="Advanced Topics", value=31),
    app_commands.Choice(name="Connecting to the Physical World", value=32),
    app_commands.Choice(name="Developing Scratch Extensions", value=48),
    app_commands.Choice(name="Open Source Projects", value=49),
    app_commands.Choice(name="Things I'm Making and Creating", value=29),
    app_commands.Choice(name="Things I'm Reading and Playing", value=30),
])
async def forums(interact : discord.Interaction, category : int):
    msg = discord.Embed(title="Topics in this category :", color=colour1)
    desc = ""
    for item in sa.get_topic_list(category_id=category, page=1):
        desc = (
            f"{desc}"
            f"\n\n**[{item.title}](https://scratch.mit.edu/discuss/topic/{item.id})** - {item.reply_count} replies - {item.view_count} views (last update : {item.last_updated})"
        )
    msg.description = desc
    await interact.response.send_message(embed=msg)

@bot.tree.command(name="topic", description="Gives useful infos about a forum topic.")
async def topic(interact : discord.Interaction, topic : str):
    id = ''.join(filter(str.isdigit, topic))
    stopic = sa.get_topic(id)
    msg = discord.Embed(title=stopic.title, color=colour1)
    msg.description = (
        f"Link : https://scratch.mit.edu/discuss/topic/{stopic.id}\n"
        f"Category : {stopic.category_name}\n"
        f" Last updated : {stopic.last_updated}\n"
        f"Author : {stopic.first_post().author_name}\n"
        "First post :\n"
        f"```{stopic.first_post().content}```"
    )
    msg.set_thumbnail(url=stopic.first_post().author().icon_url)
    await interact.response.send_message(embed=msg)

@bot.tree.command(name="s_download", description="Downloads the specified project")
async def s_download(interact : discord.Interaction, project : str):
    id = ''.join(filter(str.isdigit, project))
    proj = sa.get_project(id)

@bot.command()
async def ping(ctx):
    msg = discord.Embed(title="🏓 Pong !", description="Latency in ms :")
    msg.add_field(name=f"{bot.user.name}'s Latency (ms): ", value=f"{round(bot.latency * 1000)}ms.", inline=False)
    msg.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)
    msg.color = discord.Color.dark_orange()
    await ctx.send(embed=msg)

with open("FluffyBot_private/token.txt") as f:
    bot.run(f.readlines()[0])
    f.close()