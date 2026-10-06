"""
Link embed functions for the bot.
"""

import interactions
from datetime import datetime

import scratchattach as scratch

from config import contributors, devs, scratch_orange
from utils import limiter

def user_embed(username: str):
    embeded_message = interactions.Embed(title=username)

    try:
        user = scratch.get_user(username)

        # Rank finder
        if user.is_new_scratcher():
            rank = "<:newscratcher:1330550984971259954> New scratcher"
        elif user.scratchteam:
            rank = "<:ScratchTeam:1330549427580178472> Scratch team member"
        elif user.follower_count() > 10000:
            rank = "<:forumcool:1341109220119941140> Legend scratcher (>10 000 followers)"
        elif user.name in contributors:
            rank = "<:coolcat:1330548833209417821> Contributor"
        elif user.name in devs:
            rank = "<:code:1333794362315767870> ScratchOn dev"
        elif user.name == "Fluffygamer_":
            rank = "<:Verified:1333795453250175058> ScratchOn owner"
        else:
            rank = "<:ScratchCat:1330547949721223238> Scratcher"
    
        with open("private/scusers.txt") as f:
            lines = [line.rstrip("\n") for line in f]
            if user.name in lines:
                idx = lines.index(user.name)
                bound = f"{open('private/dcusers.txt').readlines()[idx].rstrip('\n')} on Discord\n\n"
            else:
                bound = ""
    
            join_date = datetime.fromisoformat(
                user.join_date.replace("Z", "+00:00")
            ).strftime("%B %d, %Y at %H:%M:%S UTC")
    
        embeded_message.description = (
            f"**{rank}**\n\n"
            f"{bound}"
            f"*Joined scratch on {join_date} - Lives in {user.country}* \n"
            f"**{username}** has **{user.message_count()}** message(s). \n\n"
            f"**<:ocular:1333041343668158515>Ocular :** \n"
            f"Color : {user.ocular_status().get('color')} Status : {user.ocular_status().get('status')}* \n\n"
            f"**About {username}** : \n"
            f"{user.about_me} \n\n"
            f"**What is {username} working on** : \n"
            f"{user.wiwo}\n\n"
            f"**{username}** is followed by **{user.follower_count()}** scratchers, "
            f"and is following **{user.following_count()}** scratchers.\n"
            f"They also loved **{user.loves_count()} projects** and favourited "
            f"**{user.favorites_count()} projects** in total.\n\n"
            f"{user.featured_data()['label']} : [{user.featured_data()['project']['title']}]"
            f"(https://scratch.mit.edu/projects/{user.featured_data()['project']['id']})"
        )
    
        embeded_message.set_thumbnail(url=user.icon_url)
        embeded_message.set_footer(text=f"{username}'s ID : {user.id}")
        embeded_message.color = scratch_orange
        embeded_message.set_image(
            url=user.featured_data()["project"]["thumbnail_url"]
        )
        return embeded_message
    
    except scratch.utils.exceptions.UserNotFound:
        return interactions.Embed(
            title="Error :",
                description="This user doesn't exist !<:giga404:1330551323610976339>",
                color=0xFF0000,
            )

def project_embed(project : str | int):
    id = "".join(filter(str.isdigit, project))
    project_obj = scratch.get_project(id)
    
    msg = interactions.Embed(title=f"{project_obj.title} :")
    
    msg.add_field(name="Views :", value=f"{project_obj.views} :eye:")
    msg.add_field(name="Loves :", value=f"{project_obj.loves} :heart:")
    msg.add_field(name="Faves :", value=f"{project_obj.favorites} :star:")
    msg.add_field(
        name="Loves per view :",
        value=f"{round(project_obj.loves / project_obj.views, 2)} :heart: / :eye:",
    )
    msg.add_field(
        name="Faves per view :",
        value=f"{round(project_obj.favorites / project_obj.views, 2)} :star: / :eye:",
    )
    msg.add_field(
        name="Loves per view (%) :",
        value=f"{round((project_obj.loves / project_obj.views) * 100)} :heart: / 100 :eye:",
    )
    msg.add_field(
        name="Faves per view (%) :",
        value=f"{round((project_obj.favorites / project_obj.views) * 100)} :star: / 100 :eye:",
    )
    
    msg.color = scratch_orange
    desc = limiter(text=project_obj.instructions, limit=500)
    msg.description = (
        f"Made by {project_obj.author_name}, at {project_obj.share_date} "
        f"(Last modified at {project_obj.last_modified})\n"
        f"<:Turbowarp:1330552274774396979>Turbowarp link : https://turbowarp.org/{id}\n\n"
        f"**Description :**\n{desc}\n\n"
        f"**Notes and Credits :**\n{project_obj.notes}\n\n"
        "<:scratchstats:1330550531864662018> Statistics :\n"
    )
    msg.set_image(url=project_obj.thumbnail_url)

    return msg

def studio_embed(studio : str | int):
    id = "".join(filter(str.isdigit, studio))
    studio_obj = scratch.get_studio(id)
    
    access = "Everyone" if studio_obj.open_to_all else "Only curators"
    
    msg = interactions.Embed(title=studio_obj.title)
    msg.set_image(url=studio_obj.image_url)
    msg.set_thumbnail(url=studio_obj.host().icon_url)
    desc = limiter(text=studio_obj.description, limit=500)
    
    msg.description = (
        f"Owned by **{studio_obj.host()}**, with id {studio_obj.host_id}\n"
        f"**{access}** can add projects.\n\n"
        "**This studio has :**\n"
        f"- {studio_obj.project_count} projects\n"
        f"- {studio_obj.follower_count} followers\n"
        f"- {studio_obj.manager_count} managers\n\n"
        f"**Description :**\n{desc}"
    )
    msg.set_footer(
        text=(
            f"Studio id : {studio_obj.id}, "
            f"link : https://scratch.mit.edu/studios/{studio_obj.id}"
        )
    )
    msg.color = scratch_orange
    return msg