"""
User-related slash commands.
"""

import interactions
from datetime import datetime

import scratchattach as scratch

from config import scratch_orange, green, red, contributors, devs, pending_verifiers
from utils import dc2scratch, user_embed


class UserCommands(interactions.Extension):
    """User-related slash commands."""

    @interactions.slash_command(
        name="s_profile",
        description="Take a look at a scratcher's profile!",
    )
    @interactions.slash_option(
        name="user",
        description="Scratch username to look up",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def s_profile(self, ctx: interactions.SlashContext, user: str):
        await ctx.defer()
        await ctx.send(embed=user_embed(user))

    @interactions.slash_command(
        name="check_username",
        description="Checks if a scratch username is already claimed or not!",
    )
    @interactions.slash_option(
        name="username",
        description="Username to check",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def check_username(self, ctx: interactions.SlashContext, username: str):
        check = scratch.check_username(username)
        msg = interactions.Embed(title=f"Username \"{username}\" is...")
        if check == "bad username":
            msg.title = "Invalid username!"
            msg.description = "This username is not appropriate! <:Nope:1333795409403052032> \n [Check the rules](https://scratch.mit.edu/community_guidelines) :arrow_left:"
            msg.color = red
        elif check == "valid username":
            msg.description = "Available! :partying_face: \n [Claim it](https://scratch.mit.edu/join) <:happycat:1330550173335982160>"
            msg.color = green
        else:
            msg.description = f"Taken! :smiling_face_with_tear:\n Link: https://scratch.mit.edu/users/{username} <a:sadcat:1330550126745227335>"
            msg.color = red
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

        # Check if user is already bound
        with open("private/dcusers.txt") as file:
            for item in file.readlines():
                if item.strip() == target:
                    found = True
                    break

        if found:
            bound = await dc2scratch(ctx.author.username)
            await ctx.send(
                embed=interactions.Embed(
                    title="❌ A scratch account is already linked to your discord account!",
                    description=f"Your account is linked to **{bound}**.\nScratchOn can't handle replacements yet.",
                    color=red,
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

        # If the user already started verification, check now
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
                    color=green,
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
                    description=f"Is followed by {followed_by}!",
                    color=green,
                )
            )
        else:
            await ctx.send(
                embed=interactions.Embed(
                    title=username,
                    description=f"Is not followed by {followed_by}!",
                    color=red,
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
        limit_reached = False

        followers1 = scratch.get_user(user_1).follower_names(
            limit=min(1000, int(scratch.get_user(user_1).follower_count()))
        )
        followers2 = scratch.get_user(user_2).follower_names(
            limit=min(1000, int(scratch.get_user(user_2).follower_count()))
        )

        for item in followers1:
            if item in followers2:
                count += 1
                if not limit_reached:
                    desc = f"{desc}\n{item}"
            if count == 200:
                desc = f"{desc}\n**And more...**"
                limit_reached = True

        if count == 0:
            await ctx.send(
                embed=interactions.Embed(
                    title=f"{user_1} and {user_2} have no mutual followers!",
                    color=scratch_orange,
                )
            )
        else:
            if len(followers1) == 1000 or len(followers2) == 1000:
                msg.title = (
                    f"<:together:1330551758166036500>"
                    f"{user_1} and {user_2} have over {count} mutual followers"
                    f"<:together:1330551758166036500> :"
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
        opt_type=interactions.OptionType.INTEGER,
        required=True,
        max_value=50,
    )
    async def activity(self, ctx: interactions.SlashContext, user: str, limit: int):
        await ctx.defer()
        user = "".join(filter(str.isdigit, user))

        msg = interactions.Embed(
            title=f"{user}'s past scratch activity:", color=scratch_orange
        )
        result = ""

        for item in scratch.get_user(user).activity(limit=limit):

            # Handle where the user did this action
            target = item.target()
            if type(target) == scratch.User:
                where = f"[{target.username}](https://scratch.mit.edu/users/{target.username})"
            elif type(target) == scratch.Project:
                where = f"[{scratch.get_project(target.id).title}](https://scratch.mit.edu/projects/{target.id})"
            elif type(target) == scratch.Studio:
                where = f"[{scratch.get_studio(target.id).title}](https://scratch.mit.edu/studios/{target.id})"
            elif type(target) == scratch.Comment:
                where = "Comment¹"
            else:
                where = "Unknown"

            # Handle the type of action
            if item.type == "becomecurator":
                action = "became a curator of"
            elif item.type == "was promoted to manager of":
                action = "became a manager of"
            elif item.type == "followstudio ":
                action = "followed the studio"
            elif item.type == "followuser":
                action = "is following"
            elif item.type == "loveproject":
                action = "loved"
            elif item.type == "favoriteproject":
                action = "favorited"
            else:
                action = item.type

            result = f"{result}\n`{user}` {action} {where}"

        if "Comment¹" in result:
            result = f"{result}\n\n¹ This is just \"Comment\" because it would be too much work to fetch the comment's URL with the way the API is built."

        msg.description = result
        await ctx.send(embed=msg)

    @interactions.slash_command(
        name="scratchteam",
        description="Gets all scratch team members!",
    )
    async def scratchteam(self, ctx: interactions.SlashContext):
        msg = interactions.Embed(
            title="<:ScratchTeam:1330549427580178472> The Scratch Team is composed of:",
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

    @interactions.slash_command(
        name="compare",
        description="Compares two Scratch users' stats.",
    )
    @interactions.slash_option(
        name="user1",
        description="First Scratch username",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="user2",
        description="Second Scratch username",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def compare(self, ctx: interactions.SlashContext, user1: str, user2: str):
        await ctx.defer()

        try:
            sc_user1 = scratch.get_user(user1)
            sc_user2 = scratch.get_user(user2)

        except scratch.utils.exceptions.UserNotFound:
            await ctx.send(
                embed=interactions.Embed(
                    title="Error",
                    description="One or both of the specified users do not exist on Scratch.",
                    color=red,
                )
            )

        project_count1 = sc_user1.project_count()
        love_count1 = 0
        favorite_count1 = 0

        project_count2 = sc_user2.project_count()
        love_count2 = 0
        favorite_count2 = 0

        for project in sc_user1.projects(limit=project_count1):
            love_count1 += project.loves
            favorite_count1 += project.favorites

        for project in sc_user2.projects(limit=project_count2):
            love_count2 += project.loves
            favorite_count2 += project.favorites

        embed = interactions.Embed(title=f"{user1} and {user2}", color=scratch_orange)
        embed.add_field(
            name=user1,
            value=(
                f"{project_count1} projects\n"
                f"{sc_user1.follower_count()} <:Followers:1524005976485924874>\n"
                f"{sc_user1.following_count()} <:Followings:1524093134060130405>\n"
                f"{love_count1} <:Heart:1524004399104655440>\n"
                f"{favorite_count1} <:Star:1524004383778406562>"
            ),
            inline=True,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name=user2,
            value=(
                f"{project_count2} projects\n"
                f"{sc_user2.follower_count()} <:Followers:1524005976485924874>\n"
                f"{sc_user2.following_count()} <:Followings:1524093134060130405>\n"
                f"{love_count2} <:Heart:1524004399104655440>\n"
                f"{favorite_count2} <:Star:1524004383778406562>"
            ),
            inline=True,
        )

        await ctx.send(embed=embed)


def setup(bot: interactions.Client):
    UserCommands(bot)
