"""
User-related slash commands.
"""

import interactions
from datetime import datetime

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
    async def s_profile(self, ctx: interactions.SlashContext, user: str):
        await ctx.defer()
        embeded_message = interactions.Embed(title=user)

        try:
            usr = scratch.get_user(user)

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
                rank = "<:code:1333794362315767870> ScratchOn dev"
            elif usr.name == "Fluffygamer_":
                rank = "<:Verified:1333795453250175058> ScratchOn owner"
            else:
                rank = "<:ScratchCat:1330547949721223238> Scratcher"

            with open("private/scusers.txt") as f:
                lines = [line.rstrip("\n") for line in f]
                if usr.name in lines:
                    idx = lines.index(usr.name)
                    binded = open("private/dcusers.txt").readlines()[idx].rstrip("\n")
                else:
                    binded = "*No binded account found*"

            join_date = datetime.fromisoformat(
                usr.join_date.replace("Z", "+00:00")
            ).strftime("%B %d, %Y at %H:%M:%S UTC")

            embeded_message.description = (
                f"**{rank}**\n\n"
                f"**Account binded to :** {binded}\n"
                f"*Joined scratch on {join_date} - Lives in {usr.country}* \n"
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
                f"{usr.featured_data()['label']} : [{usr.featured_data()['project']['title']}]"
                f"(https://scratch.mit.edu/projects/{usr.featured_data()['project']['id']})"
            )

            embeded_message.set_thumbnail(url=usr.icon_url)
            embeded_message.set_footer(text=f"{user}'s ID : {usr.id}")
            embeded_message.color = scratch_orange
            embeded_message.set_image(url=usr.featured_data()["project"]["thumbnail_url"])
            await ctx.send(embed=embeded_message)

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
    async def check_username(self, ctx: interactions.SlashContext, username: str):
        msg = interactions.Embed(title="This username is...")
        if scratch.check_username(username) == "valid username":
            msg.description = "Avaliable ! :partying_face: \n [Claim it](<https://scratch.mit.edu/join>) <:happycat:1330550173335982160>"
            msg.color = 0x57F287  # green
        else:
            msg.description = f"Taken ! :smiling_face_with_tear:\n Link : https://scratch.mit.edu/users/{username} <a:sadcat:1330550126745227335>"
            msg.color = 0xFF0000  # red
        await ctx.send(embed=msg)

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
    async def bind(self, ctx: interactions.SlashContext, username: str):
        await ctx.defer()
        user_id = ctx.author.id
        target = str(ctx.author)
        found = False

        # Check if user is already binded
        with open("private/dcusers.txt") as file:
            for item in file.readlines():
                if item.strip() == target:
                    found = True
                    break

        if found:
            binded = await dc2scratch(ctx.author.username)
            await ctx.send(
                embed=interactions.Embed(
                    title="❌ A scratch account is already linked to your discord account!",
                    description=f"Your account is linked to **{binded}**.\nScratchOn can't handle replacements yet.",
                    color=0xFF0000,
                )
            )
            return

        user = scratch.get_user(username)

        # If the user hasn't started verification yet, issue a code
        if user_id not in pending_verifiers:
            v = user.verify_identity()
            pending_verifiers[user_id] = v
            await ctx.send(
                embed=interactions.Embed(
                    title="⏳ Wait!",
                    description=(
                        f"To verify ownership, please comment **'{v.code}'** on this project: {v.projecturl}\n"
                        "Then, run this command again."
                    ),
                    color=scratch_orange,
                )
            )
            return

        # User already started verification — check now
        v = pending_verifiers[user_id]
        if v.check():
            with open("private/dcusers.txt", "a") as file:
                file.write(f"{str(ctx.author)}\n")
            with open("private/scusers.txt", "a") as file:
                file.write(f"{str(username)}\n")

            del pending_verifiers[user_id]

            await ctx.send(
                embed=interactions.Embed(
                    title="✅ Success!",
                    description=f"Your Discord account is now linked to your Scratch account, **{username}**!",
                    color=0x57F287,
                )
            )
        else:
            await ctx.send(
                embed=interactions.Embed(
                    title="⏳ Still waiting...",
                    description=(
                        f"Please comment **'{v.code}'** on this project: {v.projecturl}\n"
                        "Then, run this command again."
                    ),
                    color=0xE67E22,  # orange
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
    ):
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
    ):
        await ctx.defer()
        msg = interactions.Embed()
        count = 0
        desc = ""

        followers1 = scratch.get_user(user_1).follower_names(
            limit=int(scratch.get_user(user_1).follower_count())
        )
        followers2 = scratch.get_user(user_2).follower_names(
            limit=int(scratch.get_user(user_2).follower_count())
        )

        for item in followers1:
            if item in followers2:
                count += 1
                desc = f"{desc}\n{item}"

        if count == 0:
            await ctx.send(
                embed=interactions.Embed(
                    title=f"{user_1} and {user_2} have no mutual followers!",
                    color=scratch_orange,
                )
            )
        else:
            msg.title = (
                f"<:together:1330551758166036500>"
                f"{user_1} and {user_2} have {count} mutual followers"
                f"<:together:1330551758166036500> :"
            )
            msg.description = desc
            msg.color = scratch_orange
            await ctx.send(embed=msg)

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
    async def activity(self, ctx: interactions.SlashContext, user: str, limit: str):
        await ctx.defer()

        msg = interactions.Embed(
            title="This user 's past scratch activity :", color=scratch_orange
        )
        result = ""

        for item in scratch.get_user(user).activity(limit=limit):
            result = f"{result}\n`{user}` made action {item.type} at "

            target = item.target()
            if type(target) == scratch.User:
                where = f"[{target.username}](https://scratch.mit.edu/users/{target.username})"
            elif type(target) == scratch.Project:
                where = f"[{target.id}](https://scratch.mit.edu/projects/{target.id})"
            elif type(target) == scratch.Studio:
                where = f"[{target.id}](https://scratch.mit.edu/studios/{target.id})"
            elif type(target) == scratch.Comment:
                where = "Comment (I ain't writing 100 lines to support comments links because of API limitations, sorry)"
            else:
                where = "Unknown"

            result = f"{result}{where}."

        msg.description = result
        await ctx.send(embed=msg)

    @interactions.slash_command(
        name="scratchteam",
        description="Gets all scratch team members !",
    )
    async def scratchteam(self, ctx: interactions.SlashContext):
        msg = interactions.Embed(
            title="<:ScratchTeam:1330549427580178472> The Scratch Team is composed of :",
            description="",
            color=scratch_orange,
        )
        for item in scratch.scratch_team_members():
            msg.description = (
                f"{msg.description}\n- **[{item['userName']}]"
                f"(https://scratch.mit.edu/users/{item['userName']})** "
                f"<:separator:1333808735101124668> {item['name']}"
            )
        await ctx.send(embed=msg)


def setup(bot: interactions.Client):
    UserCommands(bot)
