"""
Search and discovery slash commands.
"""

import random
from itertools import islice

import interactions
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
    async def randomprojects(self, ctx: interactions.SlashContext, number: int) -> None:
        await ctx.defer()

        max_project_id = scratch.total_site_stats().get("PROJECT_COUNT", 1)
        project_links: list[str] = []

        for _ in range(number):
            while True:
                try:
                    proj = scratch.get_project(random.randint(1, max_project_id))
                    project_links.append(
                        f"[**{proj.title}**](https://scratch.mit.edu/projects/{proj.id})"
                    )
                    break
                except scratch.utils.exceptions.ProjectNotFound:
                    continue

        title = (
            "Here is 1 random project !"
            if number == 1
            else f"Here are {number} random projects !"
        )
        await ctx.send(
            embed=interactions.Embed(
                title=title,
                description="\n\n".join(project_links),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="christmas",
        description="Take a look at the best christmas projects easily !",
    )
    async def christmas(self, ctx: interactions.SlashContext) -> None:
        await ctx.defer()

        projects = scratch.search_projects(
            query="christmas", mode="popular", language="en", limit=10, offset=0
        )
        lines = [
            f"**[{p.title}](<https://scratch.mit.edu/projects/{p.id}>)**\n"
            f"-# by [{p.author().username}](https://scratch.mit.edu/users/{p.author().username})"
            for p in projects
        ]

        await ctx.send(
            embed=interactions.Embed(
                title="<:SantaCat:1444277069826494557>Top 10 popular christmas projects<:SantaCat:1444277069826494557> :",
                description="\n\n".join(lines),
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
    ) -> None:
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

        embed = interactions.Embed(color=scratch_orange)

        if recommendation_type == "projects":
            embed = self._recommend_projects(user, username)
        elif recommendation_type == "users":
            embed = self._recommend_users(user, username)
        elif recommendation_type == "studios":
            embed = self._recommend_studios(user, username)

        await ctx.send(embed=embed)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _recommend_projects(self, user, username: str) -> interactions.Embed:
        loved = list(islice(user.loved_projects(limit=10), 10))
        if not loved:
            return interactions.Embed(
                title=f"No recommendations found for {username}",
                description="This user hasn't loved any projects yet!",
                color=scratch_orange,
            )

        recommendations = []
        seen_ids: set[int] = set()

        for project in loved[:3]:
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

        if not recommendations:
            return interactions.Embed(
                title=f"No recommendations found for {username}",
                description="Could not find similar projects at this time.",
                color=scratch_orange,
            )

        lines = [
            f"**[{p.title}](<https://scratch.mit.edu/projects/{p.id}>)**\n"
            f"-# by [{p.author_name}](https://scratch.mit.edu/users/{p.author_name}) "
            f"• {p.loves} loves • {p.favorites} faves"
            for p in recommendations[:5]
        ]
        return interactions.Embed(
            title=f"Project recommendations for {username}",
            description="Based on projects you loved, you might enjoy:\n"
            + "\n".join(lines),
            color=scratch_orange,
        )

    def _recommend_users(self, user, username: str) -> interactions.Embed:
        following = list(islice(user.following_names(limit=20), 20))
        if not following:
            return interactions.Embed(
                title=f"No recommendations found for {username}",
                description="This user isn't following anyone yet!",
                color=scratch_orange,
            )

        recommendations = []
        seen_users = set(following + [username])

        for followed_name in following[:5]:
            try:
                followed_user = scratch.get_user(followed_name)
                for potential in list(followed_user.following_names(limit=10)):
                    if potential not in seen_users:
                        try:
                            rec_user = scratch.get_user(potential)
                            recommendations.append(rec_user)
                            seen_users.add(potential)
                            if len(recommendations) >= 5:
                                break
                        except Exception:
                            continue
            except Exception:
                continue
            if len(recommendations) >= 5:
                break

        if not recommendations:
            return interactions.Embed(
                title=f"No recommendations found for {username}",
                description="Could not find similar users at this time.",
                color=scratch_orange,
            )

        lines = [
            f"**[{u.username}](https://scratch.mit.edu/users/{u.username})**\n"
            f"-# {u.follower_count()} followers • {u.following_count()} following"
            for u in recommendations[:5]
        ]
        return interactions.Embed(
            title=f"User recommendations for {username}",
            description="Based on who you follow, you might like:\n" + "\n".join(lines),
            color=scratch_orange,
        )

    def _recommend_studios(self, user, username: str) -> interactions.Embed:
        curating = list(islice(user.studios_curating(limit=20), 20))
        if not curating:
            return interactions.Embed(
                title=f"No recommendations found for {username}",
                description="This user isn't curating any studios yet!",
                color=scratch_orange,
            )

        recommendations = []
        seen_ids: set[int] = set(s.id for s in curating)

        for studio in curating[:5]:
            try:
                for curator_name in list(studio.curator_names(limit=10))[:3]:
                    try:
                        curator = scratch.get_user(curator_name)
                        for potential in list(curator.studios_curating(limit=5)):
                            if potential.id not in seen_ids:
                                recommendations.append(potential)
                                seen_ids.add(potential.id)
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

        if not recommendations:
            return interactions.Embed(
                title=f"No recommendations found for {username}",
                description="Could not find similar studios at this time.",
                color=scratch_orange,
            )

        lines = [
            f"**[{s.title}](<https://scratch.mit.edu/studios/{s.id}>)**\n"
            f"-# {s.project_count} projects • {s.follower_count} followers"
            for s in recommendations[:5]
        ]
        return interactions.Embed(
            title=f"Studio recommendations for {username}",
            description="Based on studios you're in, you might like:\n"
            + "\n".join(lines),
            color=scratch_orange,
        )


def setup(bot: interactions.Client) -> None:
    SearchCommands(bot)
