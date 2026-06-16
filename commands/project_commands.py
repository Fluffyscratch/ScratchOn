"""
Project-related slash commands.
"""

import os
from datetime import datetime

import interactions
import scratchattach as scratch

from config import scratch_orange
from utils import limiter


def _extract_project_id(raw: str) -> str:
    """Return only the digits from *raw* (works for IDs and URLs)."""
    return "".join(filter(str.isdigit, raw))


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
    async def modstatus(self, ctx: interactions.SlashContext, project: str) -> None:
        project_id = _extract_project_id(project)
        project_obj = scratch.get_project(project_id)

        status = project_obj.moderation_status()
        embed = interactions.Embed(title="This project is...")

        if status == "notsafe":
            embed.description = (
                "<:Nope:1333795409403052032>Not Safe (NFE) !<:Nope:1333795409403052032>"
            )
            embed.color = 0xFF0000
        elif status == "safe":
            embed.description = "<:Verified:1333795453250175058>Safe (FE) !<:Verified:1333795453250175058>"
            embed.color = 0x57F287
        else:
            embed.description = (
                "<:forumneutral:1341109236679053312>Not Reviewed (counts as FE) !"
                "<:forumneutral:1341109236679053312>"
            )
            embed.color = 0x99AAB5

        embed.set_footer(text=f"Project ID : {project_id}")
        await ctx.send(embed=embed)

    @interactions.slash_command(
        name="embed",
        description="Gives an embedded version of the specified project, mainly for websites.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def embed(self, ctx: interactions.SlashContext, project: str) -> None:
        project_id = _extract_project_id(project)
        project_obj = scratch.get_project(project_id)

        await ctx.send(
            embed=interactions.Embed(
                title="This project is now embedded ! <:embed:1343565862077988904>",
                description=f"Link : {project_obj.embed_url}",
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="project",
        description="Gets a lot of information about a project.",
    )
    @interactions.slash_option(
        name="project",
        description="Project ID or URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def project(self, ctx: interactions.SlashContext, project: str) -> None:
        project_id = _extract_project_id(project)
        proj = scratch.get_project(project_id)

        views = proj.views or 1  # prevent division by zero

        embed = interactions.Embed(title=f"{proj.title} :")
        embed.add_field(name="Views :", value=f"{proj.views} :eye:")
        embed.add_field(name="Loves :", value=f"{proj.loves} :heart:")
        embed.add_field(name="Faves :", value=f"{proj.favorites} :star:")
        embed.add_field(
            name="Loves per view :",
            value=f"{round(proj.loves / views, 2)} :heart: / :eye:",
        )
        embed.add_field(
            name="Faves per view :",
            value=f"{round(proj.favorites / views, 2)} :star: / :eye:",
        )
        embed.add_field(
            name="Loves per view (%) :",
            value=f"{round((proj.loves / views) * 100)} :heart: / 100 :eye:",
        )
        embed.add_field(
            name="Faves per view (%) :",
            value=f"{round((proj.favorites / views) * 100)} :star: / 100 :eye:",
        )

        embed.color = scratch_orange
        desc = limiter(text=proj.instructions, limit=500)
        embed.description = (
            f"Made by {proj.author_name}, at {proj.share_date} "
            f"(Last modified at {proj.last_modified})\n"
            f"<:Turbowarp:1330552274774396979>Turbowarp link : https://turbowarp.org/{project_id}\n\n"
            f"**Description :**\n{desc}\n\n"
            f"**Notes and Credits :**\n{proj.notes}\n\n"
            "<:scratchstats:1330550531864662018> Statistics :\n"
        )
        embed.set_image(url=proj.thumbnail_url)
        await ctx.send(embed=embed)

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
    async def trendscore(self, ctx: interactions.SlashContext, project: str) -> None:
        project_id = _extract_project_id(project)
        proj = scratch.get_project(project_id)
        diff = datetime.now() - datetime.strptime(
            proj.share_date, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        hours = diff.days * 24 + diff.seconds / 3600
        score = round(proj.views / hours, 3) if hours else 0

        await ctx.send(
            embed=interactions.Embed(
                title=(
                    f"<:popular:1330550904813916272>'{proj.title}' has a trending score of {score} !"
                    "<:popular:1330550904813916272>"
                ),
                color=0xF1C40F,
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
    ) -> None:
        project_id = _extract_project_id(project)
        position = 0

        for item in scratch.explore_projects(
            language=language, limit=limit, mode="trending"
        ):
            position += 1
            if item.id == int(project_id):
                await ctx.send(
                    embed=interactions.Embed(
                        title="Project found !",
                        description=f"This project is on trending, at the **{position}th** position !",
                        color=0x57F287,
                    )
                )
                return

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
    async def newestprojects(self, ctx: interactions.SlashContext) -> None:
        projects = scratch.newest_projects()
        description = "\n".join(
            f"- [{p.title}](https://scratch.mit.edu/projects/{p.id})" for p in projects
        )
        await ctx.send(
            embed=interactions.Embed(
                title="<:newscratcher:1330550984971259954>Newest scratch projects :",
                description=description,
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
    async def s_download(self, ctx: interactions.SlashContext, project: str) -> None:
        project_id = _extract_project_id(project)
        await ctx.defer()
        proj = scratch.get_project(project_id)
        proj.download(filename="project.sb3", dir="private")

        await ctx.send(
            file=interactions.File(
                file="private/project.sb3",
                file_name=f"{proj.title}.sb3",
            )
        )

        os.remove("private/project.sb3")


def setup(bot: interactions.Client) -> None:
    ProjectCommands(bot)
