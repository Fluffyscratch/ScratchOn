"""
Project-related slash commands.
"""

import os
import interactions
from datetime import datetime

import scratchattach as scratch

from config import scratch_orange
from utils import limiter


class ProjectCommands(interactions.Extension):
    """Project-related slash commands."""

    @interactions.slash_command(
        name="modstatus",
        description="Tells if a project is either FE or NFE.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def modstatus(self, ctx: interactions.SlashContext, project: str):
        id = "".join(filter(str.isdigit, project))
        project_obj = scratch.get_project(id)

        status = project_obj.moderation_status()
        embeded_msg = interactions.Embed(title="This project is...")

        if status == "notsafe":
            embeded_msg.description = (
                "<:Nope:1333795409403052032>Not Safe (NFE) !<:Nope:1333795409403052032>"
            )
            embeded_msg.color = 0xFF0000
        elif status == "safe":
            embeded_msg.description = (
                "<:Verified:1333795453250175058>Safe (FE) !<:Verified:1333795453250175058>"
            )
            embeded_msg.color = 0x57F287
        else:
            embeded_msg.description = (
                "<:forumneutral:1341109236679053312>Not Reviewed (counts as FE) !"
                "<:forumneutral:1341109236679053312>"
            )
            embeded_msg.color = 0x99AAB5  # light grey

        embeded_msg.set_footer(text=f"Project ID : {id}")
        await ctx.send(embed=embeded_msg)

    @interactions.slash_command(
        name="embed",
        description="Gives an embeded version of the specified project, mainly for websites.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def embed(self, ctx: interactions.SlashContext, project: str):
        id = "".join(filter(str.isdigit, project))
        project_obj = scratch.get_project(id)

        link = project_obj.embed_url
        embeded_msg = interactions.Embed(
            title="This project is now embedded ! <:embed:1343565862077988904>",
            description=f"🔗 Link : {link}",
            color=scratch_orange,
        )
        await ctx.send(embed=embeded_msg)

    @interactions.slash_command(
        name="project",
        description="Gets a lot of informations about a project.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def project(self, ctx: interactions.SlashContext, project: str):
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
        await ctx.send(embed=msg)

    @interactions.slash_command(
        name="trendscore",
        description="Gets a project's trending potential, represented as a score number.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def trendscore(self, ctx: interactions.SlashContext, project: str):
        id = "".join(filter(str.isdigit, project))
        proj = scratch.get_project(id)
        diff = datetime.now() - datetime.strptime(
            proj.share_date, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        score = round(proj.views / (diff.days * 24 + diff.seconds / 3600), 3)

        await ctx.send(
            embed=interactions.Embed(
                title=(
                    f"<:popular:1330550904813916272>'{proj.title}' has a trending score of {score} !"
                    "<:popular:1330550904813916272>"
                ),
                color=0xF1C40F,  # gold
            )
        )

    @interactions.slash_command(
        name="ontrend",
        description="Checks if a project is on trending in a specific language.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="language",
        description="Two-letter language code (e.g. en, fr)",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="limit",
        description="How many trending projects to check",
        opt_type=interactions.OptionType.INTEGER,
        required=True,
    )
    async def ontrend(
        self,
        ctx: interactions.SlashContext,
        project: str,
        language: str,
        limit: int,
    ):
        i = 0
        found = False
        id = "".join(filter(str.isdigit, project))

        for item in scratch.explore_projects(
            language=language, limit=limit, mode="trending"
        ):
            i += 1
            if item.id == int(id):
                found = True
                break

        if found:
            await ctx.send(
                embed=interactions.Embed(
                    title="Project found !",
                    description=f"This project is on trending, at the **{i}th** position !",
                    color=0x57F287,
                )
            )
        else:
            await ctx.send(
                embed=interactions.Embed(
                    title="Project not found !",
                    description="This project is not on trending !",
                    color=0xFF0000,
                )
            )

    @interactions.slash_command(
        name="newestprojects",
        description="Get all the newest published projects.",
    )
    async def newestprojects(self, ctx: interactions.SlashContext):
        import pprint

        await ctx.send(
            embed=interactions.Embed(
                title="<:newscratcher:1330550984971259954>Newest scratch projects :",
                description=pprint.pformat(scratch.newest_projects()),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="s_download",
        description="Downloads the specified project",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def s_download(self, ctx: interactions.SlashContext, project: str):
        id = "".join(filter(str.isdigit, project))
        await ctx.defer()
        proj = scratch.get_project(id)
        proj.download(filename="project.sb3", dir="private")

        await ctx.send(
            file=interactions.File(
                file="private/project.sb3",
                file_name=f"{proj.title}.sb3",
            )
        )

        os.remove(path="private/project.sb3")


def setup(bot: interactions.Client):
    ProjectCommands(bot)
