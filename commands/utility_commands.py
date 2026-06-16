"""
Utility slash commands (help, about, stats, tips, etc.).
"""

import io
import pprint
import re
from collections import Counter

import interactions
import scratchattach as scratch

from config import scratch_orange


class UtilityCommands(interactions.Extension):
    """Utility slash commands."""

    @interactions.slash_command(
        name="help",
        description="Need help ? No problem ! All commands and their usage are here.",
    )
    async def help(self, ctx: interactions.SlashContext) -> None:
        await ctx.send(
            embed=interactions.Embed(
                title="<:giga404:1330551323610976339>Help",
                description=(
                    "EVENT COMMANDS :\n\n"
                    "<:SantaCat:1444277069826494557> **/christmas** - Returns the current christmas projects on trending !\n"
                    "\n---\n\n"
                    "<:search:1333037655902130247> **/about** - Gives interesting facts and stats about this bot !\n"
                    " **/bind** - Allows you to bind your scratch account to your discord account.\n"
                    "<:newscratcher:1330550984971259954> **/check_username** - Tells you if a username is available or not.\n"
                    " **/embed** - Gives the embed version of a project, useful for websites.\n"
                    " **/followedby** - Checks if a user is followed by another user!\n"
                    " **/forums** - Gets all topics in a forum category.\n"
                    " **/health** - Gets health data about Scratch.\n"
                    " **/modstatus** - Says if a project is rated FE or NFE.\n"
                    " **/newestprojects** - Gets newly shared projects.\n"
                    " **/ontrend** - Checks if a project is on trending.\n"
                    " **/project** - Gives useful information about a specific project.\n"
                    " **/randomprojects** - Returns random project titles.\n"
                    " **/scratchactivity** - Find a user's past activity on scratch.\n"
                    "<:catblock:1330552768171216897> **/scratchblocks** - Generates scratch-like blocks.\n"
                    "<:ScratchTeam:1330549427580178472> **/scratchteam** - Gets all scratch team members !\n"
                    "<:tts:1344271467876974602> **/scratchtts** - Use scratch's Text to Speech in discord !\n"
                    "<:ScratchCat:1330547949721223238> **/s_profile** - Look at someone's profile.\n"
                    " **/studio** - Preview a studio.\n"
                    " **/topic** - Preview a forum topic.\n"
                    " **/trendscore** - Gives a trending score for a project.\n"
                    " **/webstats** - Gets statistics about Scratch.\n"
                    "<:youtube:1340017536409927711> **/yttoscratch** - Converts a youtube video link into a forum link.\n"
                    "\nNeed assistance, have a suggestion or found a bug? "
                    "Join our [support server](https://discord.gg/dgymF2Ye4k)!"
                ),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="about",
        description="Everything you need to know about ScratchOn !",
    )
    async def about(self, ctx: interactions.SlashContext) -> None:
        language_counts = Counter()
        for guild in self.bot.guilds:
            language_counts[str(guild.preferred_locale)] += 1

        top_languages = language_counts.most_common(2)
        langs = "\n".join(
            f"{i}. {lang} with {count} servers"
            for i, (lang, count) in enumerate(top_languages, 1)
        )

        unique_members = set()
        for guild in self.bot.guilds:
            unique_members.update(member.id for member in guild.members)

        bot_name = self.bot.user.username

        embed = interactions.Embed(
            title="About ScratchOn <:BestBot:1388503205373280337> :"
        )
        embed.description = (
            "<:together:1330551758166036500> **Contributors :**\n\n"
            "- <:fluffy:1340009005581598820>** Fluffy** - Bot founder and owner.\n"
            "- <:timmccool:1340009073990701238>** TimMcCool** - Maker of scratchattach.\n"
            "- <:kRxZy_kRxZy:1455522693758849156>** kRxZy_kRxZy** - ScratchOn Developer.\n"
            "- <:AJustEpic:1368235230749528276>** A Just Epic** - Artist behind the PFP.\n"
            f"- You - {bot_name} user, motivating me to continue !\n"
            f"\n**Where is {bot_name} ?**\n\n"
            f"{bot_name} is in **{len(self.bot.guilds)}** servers, "
            f"and used by **{len(unique_members)}** unique scratchers worldwide.\n"
            f"**Top Languages :**\n{langs}\n\n"
            "**Links :**\n\n"
            f"- [Add {bot_name}](https://discord.com/oauth2/authorize?client_id=1300009645078876170&permissions=274877990912&integration_type=0&scope=bot)\n"
            "- [Support server](https://discord.gg/dgymF2Ye4k)\n\n"
            f"**Help {bot_name} by upvoting it :**\n"
            "- [Top.gg](https://top.gg/bot/1300009645078876170)\n"
            "- [Discordbotlist.com](https://discordbotlist.com/bots/ScratchOn)\n"
            "- [Discordlist.gg](https://discordlist.gg/bot/1300009645078876170)\n"
            "Contribute: https://github.com/Fluffyscratch/ScratchOn"
        )
        embed.color = scratch_orange
        await ctx.send(embed=embed)

    @interactions.slash_command(
        name="webstats",
        description="Returns statistics about scratch's website.",
    )
    async def webstats(self, ctx: interactions.SlashContext) -> None:
        stats = scratch.total_site_stats()

        embed = interactions.Embed(title="Statistics about Scratch :bar_chart:")
        embed.description = (
            f"**On scratch, there are :**\n\n"
            f"- {stats.get('PROJECT_COUNT')} projects\n"
            f"- {stats.get('USER_COUNT')} users\n"
            f"- {stats.get('STUDIO_COUNT')} studios\n\n"
            f"**There are {stats.get('COMMENT_COUNT')} comments :**\n\n"
            f"- {stats.get('PROFILE_COMMENT_COUNT')} are profile comments\n"
            f"- {stats.get('PROJECT_COMMENT_COUNT')} are project comments\n"
            f"- {stats.get('STUDIO_COMMENT_COUNT')} are studio comments"
        )
        embed.color = scratch_orange
        await ctx.send(embed=embed)

    @interactions.slash_command(
        name="health",
        description="Gets health data about scratch.",
    )
    async def scratchstatus(self, ctx: interactions.SlashContext) -> None:
        raw = pprint.pformat(scratch.get_health())
        formatted = re.sub(r"[{},]", "", raw)
        formatted = re.sub(r"'([^']+)'", r"**\1**", formatted)

        await ctx.send(
            embed=interactions.Embed(
                title="Scratch's health status :",
                description=(
                    f"{formatted}\n\n"
                    "## Tip : press control + F and search the health data you're looking for."
                ),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="yttoscratch",
        description="Converts a youtube video link into a scratch forums link.",
    )
    @interactions.slash_option(
        name="link",
        description="YouTube video URL",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    async def yttoscratch(self, ctx: interactions.SlashContext, link: str) -> None:
        await ctx.send(
            embed=interactions.Embed(
                title="Conversion finished ! Link :",
                description=scratch.youtube_link_to_scratch(link),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="tips",
        description="Gives you tips and tricks for scratch !",
    )
    async def tips(self, ctx: interactions.SlashContext) -> None:
        embed = interactions.Embed(
            title="Here are some helpful tips and tricks for scratch !",
            color=scratch_orange,
            description=(
                "**Cool emojis compatible with scratch:**\n\n"
                "Black and white squares/circles: black and white squares\n\n"
                "**Scratchmojis :**\n"
                "Cats :\n"
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
            ),
        )

        other_items = [
            ("<:meow:1330549076223070269>", "`_meow_`"),
            ("<:Gobo:1330552595390926948>", "`_gobo_`"),
            ("<:10mil:1330548335471493241>", "`_10mil_`"),
            ("<:waffle:1335195624127336451>", "`_waffle_`"),
            ("<:taco:1330548746156638208>", "`_taco_`"),
            ("<:sushi:1330548721355722817>", "`_sushi_`"),
            ("<:apple:1330548350663131247>", "`_apple_`"),
            ("<:broccoli:1330548400214511718>", "`_broccoli_`"),
            ("<:pizza:1330548624215642183>", "`_pizza_`"),
            ("<:candycorn:1330548437753794640>", "`_candycorn_`"),
            ("<:map:1330548598508879922>", "`_map_`"),
            ("<:camera:1330548417684045854>", "`_camera_`"),
            ("<:suitcase:1330548697359974512>", "`_suitcase_`"),
            ("<:compass:1330548457357967360>", "`_compass_`"),
            ("<:binoculars:1330548366064484422>", "`_binoculars_`"),
            ("<:cupcake:1330548475359920141>", "`_cupcake_`"),
            ("<:pride:1330548644859871253>", "`_pride_`"),
            ("<:blm:1330548384007852032>", "`_blm_`"),
        ]
        for emoji, code in other_items:
            embed.add_field(name=emoji, value=code)

        await ctx.send(embed=embed)

    @interactions.slash_command(
        name="scratchtts",
        description="Use scratch's Text to Speech in discord !",
    )
    @interactions.slash_option(
        name="text",
        description="Text to convert to speech",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="voice",
        description="TTS voice to use",
        opt_type=interactions.OptionType.STRING,
        required=True,
        choices=[
            interactions.SlashCommandChoice(name="Alto", value="alto"),
            interactions.SlashCommandChoice(name="Tenor", value="tenor"),
            interactions.SlashCommandChoice(name="Squeak", value="squeak"),
            interactions.SlashCommandChoice(name="Giant", value="giant"),
            interactions.SlashCommandChoice(name="Kitten", value="kitten"),
        ],
    )
    @interactions.slash_option(
        name="language",
        description="Language for TTS",
        opt_type=interactions.OptionType.STRING,
        required=True,
        choices=[
            interactions.SlashCommandChoice(name="English (US)", value="en-US"),
            interactions.SlashCommandChoice(name="French", value="fr"),
        ],
    )
    async def scratchtts(
        self,
        ctx: interactions.SlashContext,
        text: str,
        voice: str,
        language: str,
    ) -> None:
        await ctx.defer()

        audio_data, playback_rate = scratch.text2speech(
            text=text, voice_name=voice, language=language
        )

        audio_file = interactions.File(
            file=io.BytesIO(audio_data),
            file_name="output.mp3",
        )

        await ctx.send(
            embed=interactions.Embed(
                title="Done! Here is the output", color=scratch_orange
            ),
            file=audio_file,
        )

    @interactions.slash_command(
        name="scratchblocks",
        description="Allow you to render scratchblocks easily !",
    )
    @interactions.slash_option(
        name="code",
        description="Scratchblocks code to render",
        opt_type=interactions.OptionType.STRING,
        required=True,
    )
    @interactions.slash_option(
        name="style",
        description="Rendering style (default: Scratch 3.0)",
        opt_type=interactions.OptionType.STRING,
        required=False,
        choices=[
            interactions.SlashCommandChoice(name="Scratch 3.0", value="scratch3"),
            interactions.SlashCommandChoice(
                name="Scratch 3.0 (high-contrast)", value="scratch3-high-contrast"
            ),
            interactions.SlashCommandChoice(name="Scratch 2.0", value="scratch2"),
        ],
    )
    async def scratchblocks(
        self,
        ctx: interactions.SlashContext,
        code: str,
        style: str = "scratch3",
    ) -> None:
        from services import render_blocks_image

        await ctx.defer()
        filename = await render_blocks_image(code=code, style=style)
        await ctx.send(file=interactions.File(file=filename))


def setup(bot: interactions.Client) -> None:
    UtilityCommands(bot)
