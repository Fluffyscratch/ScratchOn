"""
Search and discovery slash commands (ESDB-powered and others).
"""

import random
from itertools import islice

import discord
from discord import app_commands
import requests

import scratchattach as scratch

from config import bot, scratch_orange


@bot.tree.command(
    name="randomprojects",
    description="Shows a number of random scratch projects.",
)
async def randomprojects(interact: discord.Interaction, number: int):
    await interact.response.defer()

    message = ""
    max_project_id = scratch.total_site_stats().get("PROJECT_COUNT")
    for i in range(number):
        while True:
            try:
                project = scratch.get_project(random.randint(1, max_project_id))
            except scratch.utils.exceptions.ProjectNotFound:
                continue
            break
        message = f"{message} [**{project.title}**](https://scratch.mit.edu/projects/{project.id})\n\n"

    msg = discord.Embed()
    if number == 1:
        msg.title = "Here is 1 random project !"
    else:
        msg.title = f"Here are {number} random projects !"
    msg.description = message
    msg.color = scratch_orange
    await interact.followup.send(embed=msg)


@bot.tree.command(
    name="christmas", description="Take a look at the best christmas projects easily !"
)
async def christmas(interact: discord.Interaction):
    await interact.response.defer()

    message = ""
    projects = scratch.search_projects(
        query="christmas", mode="popular", language="en", limit=10, offset=0
    )
    for item in projects:
        message = (
            f"{message}\n\n **[{item.title}](<https://scratch.mit.edu/projects/{item.id}>)**\n"
            f"-# by [{item.author().username}](https://scratch.mit.edu/users/{item.author().username})"
        )
    await interact.followup.send(
        embed=discord.Embed(
            title="<:SantaCat:1444277069826494557>Top 10 popular christmas projects<:SantaCat:1444277069826494557> :",
            description=message,
            color=scratch_orange,
        )
    )


@bot.tree.command(
    name="recommend",
    description="Get personalized recommendations for projects, studios, or users based on a profile!",
)
@app_commands.choices(
    recommendation_type=[
        app_commands.Choice(name="Projects", value="projects"),
        app_commands.Choice(name="Users", value="users"),
        app_commands.Choice(name="Studios", value="studios"),
    ]
)
async def recommend(
    interact: discord.Interaction, username: str, recommendation_type: str
):
    await interact.response.defer()

    try:
        user = scratch.get_user(username)
    except scratch.utils.exceptions.UserNotFound:
        await interact.followup.send(
            embed=discord.Embed(
                title="Error:",
                description="This user doesn't exist! <:giga404:1330551323610976339>",
                color=discord.Color.red(),
            )
        )
        return

    msg = discord.Embed(color=scratch_orange)

    if recommendation_type == "projects":
        # Get user's loved and favorited projects to find similar ones
        loved_projects = list(islice(user.loved_projects(limit=10), 10))
        
        if not loved_projects:
            msg.title = f"No recommendations found for {username}"
            msg.description = "This user hasn't loved any projects yet!"
            await interact.followup.send(embed=msg)
            return

        # Extract common tags/themes from loved projects
        recommendations = []
        seen_ids = set()
        
        # For each loved project, get its author's other popular projects
        for project in loved_projects[:3]:  # Limit to avoid too many API calls
            try:
                author = project.author()
                author_projects = list(author.projects(limit=5))
                for proj in author_projects:
                    if proj.id not in seen_ids and proj.id != project.id:
                        recommendations.append(proj)
                        seen_ids.add(proj.id)
                        if len(recommendations) >= 5:
                            break
            except Exception:
                continue
            
            if len(recommendations) >= 5:
                break
        
        if recommendations:
            msg.title = f"📚 Project recommendations for {username}"
            description = "Based on projects you loved, you might enjoy:\n"
            for proj in recommendations[:5]:
                description += (
                    f"\n**[{proj.title}](<https://scratch.mit.edu/projects/{proj.id}>)**\n"
                    f"-# by [{proj.author_name}](https://scratch.mit.edu/users/{proj.author_name}) "
                    f"• ❤️ {proj.loves} • ⭐ {proj.favorites}\n"
                )
            msg.description = description
        else:
            msg.title = f"No recommendations found for {username}"
            msg.description = "Could not find similar projects at this time."

    elif recommendation_type == "users":
        # Get users that the target user follows
        following = list(islice(user.following_names(limit=20), 20))
        
        if not following:
            msg.title = f"No recommendations found for {username}"
            msg.description = "This user isn't following anyone yet!"
            await interact.followup.send(embed=msg)
            return

        # Find users followed by the people this user follows
        recommendations = []
        seen_users = set(following + [username])
        
        for followed_username in following[:5]:  # Limit API calls
            try:
                followed_user = scratch.get_user(followed_username)
                their_following = list(followed_user.following_names(limit=10))
                
                for potential_rec in their_following:
                    if potential_rec not in seen_users:
                        try:
                            rec_user = scratch.get_user(potential_rec)
                            recommendations.append(rec_user)
                            seen_users.add(potential_rec)
                            if len(recommendations) >= 5:
                                break
                        except Exception:
                            continue
            except Exception:
                continue
                
            if len(recommendations) >= 5:
                break
        
        if recommendations:
            msg.title = f"👥 User recommendations for {username}"
            description = "Based on who you follow, you might like:\n"
            for rec_user in recommendations[:5]:
                description += (
                    f"\n**[{rec_user.username}](https://scratch.mit.edu/users/{rec_user.username})**\n"
                    f"-# {rec_user.follower_count()} followers • {rec_user.following_count()} following\n"
                )
            msg.description = description
        else:
            msg.title = f"No recommendations found for {username}"
            msg.description = "Could not find similar users at this time."

    elif recommendation_type == "studios":
        # Get studios the user is curating
        curating = list(islice(user.studios_curating(limit=20), 20))
        
        if not curating:
            msg.title = f"No recommendations found for {username}"
            msg.description = "This user isn't curating any studios yet!"
            await interact.followup.send(embed=msg)
            return

        # Get related studios from the ones they're already in
        recommendations = []
        seen_ids = set([studio.id for studio in curating])
        
        for studio in curating[:5]:  # Limit API calls
            try:
                # Get curators of this studio
                curators = list(studio.curator_names(limit=10))
                
                # Find other studios these curators are in
                for curator_name in curators[:3]:
                    try:
                        curator = scratch.get_user(curator_name)
                        curator_studios = list(curator.studios_curating(limit=5))
                        
                        for potential_studio in curator_studios:
                            if potential_studio.id not in seen_ids:
                                recommendations.append(potential_studio)
                                seen_ids.add(potential_studio.id)
                                if len(recommendations) >= 5:
                                    break
                    except Exception:
                        continue
                    
                    if len(recommendations) >= 5:
                        break
            except Exception:
                continue
            
            if len(recommendations) >= 5:
                break
        
        if recommendations:
            msg.title = f"🎨 Studio recommendations for {username}"
            description = "Based on studios you're in, you might like:\n"
            for studio in recommendations[:5]:
                description += (
                    f"\n**[{studio.title}](<https://scratch.mit.edu/studios/{studio.id}>)**\n"
                    f"-# {studio.project_count} projects • {studio.follower_count} followers\n"
                )
            msg.description = description
        else:
            msg.title = f"No recommendations found for {username}"
            msg.description = "Could not find similar studios at this time."

    await interact.followup.send(embed=msg)
