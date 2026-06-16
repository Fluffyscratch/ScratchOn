"""
Search and discovery slash commands.
"""

import random
from itertools import islice

import interactions
import requests

import scratchattach as scratch

from config import scratch_orange


class SearchCommands(interactions.Extension):
    """Search and discovery slash commands."""

    @interactions.slash_command(
        name="randomprojects",
        description="Shows a number of random scratch projects.",
    )
    @interactions.slash_option(
        name="number",
        description="How many random projects to return",
        opt_type=interactions.OptionType.INTEGER,
        required=True,
    )
    async def randomprojects(self, ctx: interactions.SlashContext, number: int):
        await ctx.defer()

        message = ""
        max_project_id = scratch.total_site_stats().get("PROJECT_COUNT")
        for i in range(number):
            while True:
                try:
                    project = scratch.get_project(random.randint(1, max_project_id))
                except scratch.utils.exceptions.ProjectNotFound:
                    continue
                break
            message = (
                f"{message} [**{project.title}**]"
                f"(https://scratch.mit.edu/projects/{project.id})\n\n"
            )

        msg = interactions.Embed()
        msg.title = "Here is 1 random project !" if number == 1 else f"Here are {number} random projects !"
        msg.description = message
        msg.color = scratch_orange
        await ctx.send(embed=msg)

    @interactions.slash_command(
        name="christmas",
        description="Take a look at the best christmas projects easily !",
    )
    async def christmas(self, ctx: interactions.SlashContext):
        await ctx.defer()

        message = ""
        projects = scratch.search_projects(
            query="christmas", mode="popular", language="en", limit=10, offset=0
        )
        for item in projects:
            message = (
                f"{message}\n\n **[{item.title}](<https://scratch.mit.edu/projects/{item.id}>)**\n"
                f"-# by [{item.author().username}](https://scratch.mit.edu/users/{item.author().username})"
            )
        await ctx.send(
            embed=interactions.Embed(
                title="<:SantaCat:1444277069826494557>Top 10 popular christmas projects<:SantaCat:1444277069826494557> :",
                description=message,
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="recommend",
        description="Get personalized recommendations for projects, studios, or users based on a profile!",
    )
    @interactions.slash_option(
        name="username",
        description="Scratch username to base recommendations on",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="recommendation_type",
        description="What to recommend",
        opt_type=interactions.OptionType.STRING,
        required=True,
        choices=[
            interactions.SlashCommandChoice(name="Projects", value="projects"),
            interactions.SlashCommandChoice(name="Users", value="users"),
            interactions.SlashCommandChoice(name="Studios", value="studios"),
        ],
    )
    async def recommend(
        self,
        ctx: interactions.SlashContext,
        username: str,
        recommendation_type: str,
    ):
        await ctx.defer()

        try:
            user = scratch.get_user(username)
        except scratch.utils.exceptions.UserNotFound:
            await ctx.send(
                embed=interactions.Embed(
                    title="Error:",
                    description="This user doesn't exist! <:giga404:1330551323610976339>",
                    color=0xFF0000,
                )
            )
            return

        msg = interactions.Embed(color=scratch_orange)

        if recommendation_type == "projects":
            loved_projects = list(islice(user.loved_projects(limit=10), 10))

            if not loved_projects:
                msg.title = f"No recommendations found for {username}"
                msg.description = "This user hasn't loved any projects yet!"
                await ctx.send(embed=msg)
                return

            recommendations = []
            seen_ids = set()

            for project in loved_projects[:3]:
                try:
                    author = project.author()
                    for proj in list(author.projects(limit=5)):
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
            following = list(islice(user.following_names(limit=20), 20))

            if not following:
                msg.title = f"No recommendations found for {username}"
                msg.description = "This user isn't following anyone yet!"
                await ctx.send(embed=msg)
                return

            recommendations = []
            seen_users = set(following + [username])

            for followed_username in following[:5]:
                try:
                    followed_user = scratch.get_user(followed_username)
                    for potential_rec in list(followed_user.following_names(limit=10)):
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
            curating = list(islice(user.studios_curating(limit=20), 20))

            if not curating:
                msg.title = f"No recommendations found for {username}"
                msg.description = "This user isn't curating any studios yet!"
                await ctx.send(embed=msg)
                return

            recommendations = []
            seen_ids = set(s.id for s in curating)

            for studio in curating[:5]:
                try:
                    for curator_name in list(studio.curator_names(limit=10))[:3]:
                        try:
                            curator = scratch.get_user(curator_name)
                            for potential_studio in list(curator.studios_curating(limit=5)):
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

        await ctx.send(embed=msg)


def setup(bot: interactions.Client):
    SearchCommands(bot)
