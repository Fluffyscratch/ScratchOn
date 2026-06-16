"""
User-related slash commands.
"""

from datetime import datetime

import interactions
import scratchattach as scratch

from config import scratch_orange, contributors, devs, pending_verifiers
from utils import dc2scratch


class UserCommands(interactions.Extension):
    """User-related slash commands."""

    @interactions.slash_command(
        name="s_profile",
        description="Take a look at a scratcher's profile !",
    )
    @interactions.slash_option(
        name="user",
        description="Scratch username to look up",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def s_profile(self, ctx: interactions.SlashContext, user: str) -> None:
        await ctx.defer()
        embed = interactions.Embed(title=user)

        try:
            usr = scratch.get_user(user)

            # Determine rank
            if usr.is_new_scratcher():
                rank = "<:newscratcher:1330550984971259954> New scratcher"
            elif usr.scratchteam:
                rank = "<:ScratchTeam:1330549427580178472> Scratch team member"
            elif usr.follower_count() > 10000:
                rank = "<:forumcool:1341109220119941140> Legend scratcher (>10 000 followers)"
            elif usr.name in contributors:
                rank = "<:coolcat:1330548833209417821> Contributor"
            elif usr.name in devs:
                rank = "<:code:1333794362315767870> ScratchOn dev"
            elif usr.name == "Fluffygamer_":
                rank = "<:Verified:1333795453250175058> ScratchOn owner"
            else:
                rank = "<:ScratchCat:1330547949721223238> Scratcher"

            # Look up Discord binding
            with open("private/scusers.txt") as sc_file:
                sc_users = [line.strip() for line in sc_file]

            if usr.name in sc_users:
                idx = sc_users.index(usr.name)
                with open("private/dcusers.txt") as dc_file:
                    dc_lines = [line.strip() for line in dc_file]
                bound = (
                    dc_lines[idx]
                    if idx < len(dc_lines)
                    else "*No binded account found*"
                )
            else:
                bound = "*No binded account found*"

            join_date = datetime.fromisoformat(
                usr.join_date.replace("Z", "+00:00")
            ).strftime("%B %d, %Y at %H:%M:%S UTC")

            featured = usr.featured_data()
            embed.description = (
                f"**{rank}**\n\n"
                f"**Account binded to :** {bound}\n"
                f"*Joined scratch on {join_date} - Lives in {usr.country}*\n"
                f"**{user}** has **{usr.message_count()}** message(s).\n\n"
                f"**<:ocular:1333041343668158515>Ocular :**\n"
                f"Color : {usr.ocular_status().get('color')} "
                f"Status : {usr.ocular_status().get('status')}*\n\n"
                f"**About {user}** : \n"
                f"{usr.about_me}\n\n"
                f"**What is {user} working on** : \n"
                f"{usr.wiwo}\n\n"
                f"**{user}** is followed by **{usr.follower_count()}** scratchers, "
                f"and is following **{usr.following_count()}** scratchers.\n"
                f"They also loved **{usr.loves_count()} projects** and favourited "
                f"**{usr.favorites_count()} projects** in total.\n\n"
                f"{featured['label']} : "
                f"[{featured['project']['title']}]"
                f"(https://scratch.mit.edu/projects/{featured['project']['id']})"
            )

            embed.set_thumbnail(url=usr.icon_url)
            embed.set_footer(text=f"{user}'s ID : {usr.id}")
            embed.color = scratch_orange
            embed.set_image(url=featured["project"]["thumbnail_url"])
            await ctx.send(embed=embed)

        except scratch.utils.exceptions.UserNotFound:
            await ctx.send(
                embed=interactions.Embed(
                    title="Error :",
                    description="This user doesn't exist !<:giga404:1330551323610976339>",
                    color=0xFF0000,
                )
            )

    @interactions.slash_command(
        name="check_username",
        description="Checks if a scratch username is already claimed or not !",
    )
    @interactions.slash_option(
        name="username",
        description="Username to check",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def check_username(
        self, ctx: interactions.SlashContext, username: str
    ) -> None:
        embed = interactions.Embed(title="This username is...")
        if scratch.check_username(username) == "valid username":
            embed.description = (
                "Available ! :partying_face: \n"
                "[Claim it](<https://scratch.mit.edu/join>) "
                "<:happycat:1330550173335982160>"
            )
            embed.color = 0x57F287
        else:
            embed.description = (
                f"Taken ! :smiling_face_with_tear:\n"
                f"Link : https://scratch.mit.edu/users/{username} "
                f"<a:sadcat:1330550126745227335>"
            )
            embed.color = 0xFF0000
        await ctx.send(embed=embed)

    @interactions.slash_command(
        name="bind",
        description="Binds your scratch account to your discord account.",
    )
    @interactions.slash_option(
        name="username",
        description="Your Scratch username",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def bind(self, ctx: interactions.SlashContext, username: str) -> None:
        await ctx.defer()
        user_id = ctx.author.id
        target = str(ctx.author)

        # Check if user is already binded
        with open("private/dcusers.txt") as fh:
            already_bound = any(line.strip() == target for line in fh)

        if already_bound:
            bound_user = await dc2scratch(ctx.author.username)
            await ctx.send(
                embed=interactions.Embed(
                    title="A scratch account is already linked to your discord account!",
                    description=(
                        f"Your account is linked to **{bound_user}**.\n"
                        "ScratchOn can't handle replacements yet."
                    ),
                    color=0xFF0000,
                )
            )
            return

        user = scratch.get_user(username)

        # First step: issue a verification code
        if user_id not in pending_verifiers:
            v = user.verify_identity()
            pending_verifiers[user_id] = v
            await ctx.send(
                embed=interactions.Embed(
                    title="Wait!",
                    description=(
                        f"To verify ownership, please comment **'{v.code}'** on this project: "
                        f"{v.projecturl}\nThen, run this command again."
                    ),
                    color=scratch_orange,
                )
            )
            return

        # Second step: verify the code
        v = pending_verifiers[user_id]
        if v.check():
            with open("private/dcusers.txt", "a") as dc_file:
                dc_file.write(f"{ctx.author}\n")
            with open("private/scusers.txt", "a") as sc_file:
                sc_file.write(f"{username}\n")

            del pending_verifiers[user_id]

            await ctx.send(
                embed=interactions.Embed(
                    title="Success!",
                    description=(
                        f"Your Discord account is now linked to your Scratch account, "
                        f"**{username}**!"
                    ),
                    color=0x57F287,
                )
            )
        else:
            await ctx.send(
                embed=interactions.Embed(
                    title="Still waiting...",
                    description=(
                        f"Please comment **'{v.code}'** on this project: "
                        f"{v.projecturl}\nThen, run this command again."
                    ),
                    color=0xE67E22,
                )
            )

    @interactions.slash_command(
        name="followedby",
        description="Checks if a user is followed by another user !",
    )
    @interactions.slash_option(
        name="username",
        description="The Scratch user to check",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="followed_by",
        description="The user who may be following",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def followedby(
        self, ctx: interactions.SlashContext, username: str, followed_by: str
    ) -> None:
        if scratch.get_user(username).is_followed_by(followed_by):
            await ctx.send(
                embed=interactions.Embed(
                    title=username,
                    description=f"Is followed by {followed_by} !",
                    color=0x57F287,
                )
            )
        else:
            await ctx.send(
                embed=interactions.Embed(
                    title=username,
                    description=f"Is not followed by {followed_by} !",
                    color=0xFF0000,
                )
            )

    @interactions.slash_command(
        name="mutualfollowers",
        description="Finds mutual followers between 2 users.",
    )
    @interactions.slash_option(
        name="user_1",
        description="First Scratch user",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="user_2",
        description="Second Scratch user",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def mutualfollowers(
        self, ctx: interactions.SlashContext, user_1: str, user_2: str
    ) -> None:
        await ctx.defer()

        followers_1 = scratch.get_user(user_1).follower_names(
            limit=int(scratch.get_user(user_1).follower_count())
        )
        followers_2 = scratch.get_user(user_2).follower_names(
            limit=int(scratch.get_user(user_2).follower_count())
        )

        mutual = [name for name in followers_1 if name in followers_2]
        count = len(mutual)

        if count == 0:
            await ctx.send(
                embed=interactions.Embed(
                    title=f"{user_1} and {user_2} have no mutual followers!",
                    color=scratch_orange,
                )
            )
        else:
            await ctx.send(
                embed=interactions.Embed(
                    title=(
                        f"<:together:1330551758166036500>"
                        f"{user_1} and {user_2} have {count} mutual followers"
                        f"<:together:1330551758166036500> :"
                    ),
                    description="\n".join(mutual),
                    color=scratch_orange,
                )
            )

    @interactions.slash_command(
        name="scratchactivity",
        description="Shows the scratch activity of a user",
    )
    @interactions.slash_option(
        name="user",
        description="Scratch username",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="limit",
        description="Number of activities to show",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def activity(
        self, ctx: interactions.SlashContext, user: str, limit: str
    ) -> None:
        await ctx.defer()

        lines: list[str] = []
        for item in scratch.get_user(user).activity(limit=limit):
            target = item.target()

            if isinstance(target, scratch.User):
                where = f"[{target.username}](https://scratch.mit.edu/users/{target.username})"
            elif isinstance(target, scratch.Project):
                where = f"[{target.id}](https://scratch.mit.edu/projects/{target.id})"
            elif isinstance(target, scratch.Studio):
                where = f"[{target.id}](https://scratch.mit.edu/studios/{target.id})"
            elif isinstance(target, scratch.Comment):
                where = "Comment"
            else:
                where = "Unknown"

            lines.append(f"`{user}` made action {item.type} at {where}.")

        await ctx.send(
            embed=interactions.Embed(
                title="This user's past scratch activity :",
                description="\n".join(lines),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="scratchteam",
        description="Gets all scratch team members !",
    )
    async def scratchteam(self, ctx: interactions.SlashContext) -> None:
        members = "\n".join(
            f"- **[{m['userName']}](https://scratch.mit.edu/users/{m['userName']})** "
            f"<:separator:1333808735101124668> {m['name']}"
            for m in scratch.scratch_team_members()
        )
        await ctx.send(
            embed=interactions.Embed(
                title="<:ScratchTeam:1330549427580178472> The Scratch Team is composed of :",
                description=members,
                color=scratch_orange,
            )
        )


def setup(bot: interactions.Client) -> None:
    UserCommands(bot)
