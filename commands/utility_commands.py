"""
Utility slash commands (help, about, stats, tips, etc.).
"""

import re
import io
import pprint
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
    async def help(self, ctx: interactions.SlashContext):
        await ctx.send(
            embed=interactions.Embed(
                title="<:giga404:1330551323610976339>Help",
                description=(
                    "🎉 EVENT COMMANDS 🗓️ :\n\n"
                    "<:SantaCat:1444277069826494557> **/christmas** ║ Returns the current christmas projects on trending !\n"
                    "\n═══════════════════════════\n\n"
                    "<:search:1333037655902130247> **/about** ║ Gives interesting facts and stats about this bot !\n"
                    "🔗 **/bind** ║ Allows you to bind your scratch account to your discord account, through a simple authentication process.\n"
                    "<:newscratcher:1330550984971259954> **/check_username** ║ Tells you if a username is available or not, so you can claim it if you want to!\n"
                    "📧 **/embed** ║ Gives the embed version of a project, useful for websites.\n"
                    "🔔 **/followedby** ║ Checks if a user is followed by another user!\n"
                    "📃 **/forums** ║ Gets all topics in a forum category, with their stats. Language topics not supported yet because of discord limitations <a:sadcat:1330550126745227335>\n"
                    "🩺 **/health** ║ Gets 'health data' about Scratch such as version, uptime, and complex data. Made for very advanced tech users.\n"
                    "✅ **/modstatus** ║ Says if a project is rated either For Everyone (FE) or Not For Everyone (NFE).\n"
                    "🆕 **/newestprojects** ║ Gets newly shared projects.\n"
                    "<:ocular:1333041343668158515> **/bettersearch**  Allows searching projects just like in scratch, but better. For example, projects with high ids do show up, not like on scratch. Powered by ESDB.\n"
                    "📈 **/ontrend** ║ Checks if a project is on trending in a certain language (must be precised with 2 letters, such as en for english or fr for french) with a custom limit of how many projects the bot will look at.\n"
                    "💻 **/project** ║ Gives a lot of useful information about a specific project.\n"
                    "🎲 **/randomprojects** ║ Returns a pre-defined number of clickable random project titles. Powered by ESDB.\n"
                    "📋 **/scratchactivity** ║ Find a user's past activity on scratch. Because of API limitations, sometimes you will see '.' as where an action took place. WARNING : TOO HIGH LIMIT = ERROR\n"
                    "<:New1:1333793269636661288><:New2:1333793304822808677> <:catblock:1330552768171216897> **/scratchblocks** ║ Generates scratch-like blocks the same way the Scratch forums and wiki does. Uses [this syntax](https://en.scratch-wiki.info/wiki/Block_Plugin/Syntax).\n"
                    "<:ScratchTeam:1330549427580178472> **/scratchteam** ║ Gets all scratch team members !\n"
                    "<:tts:1344271467876974602> **/scratchtts** ║ Allows you to use text to speech... Using scratch's text to speech extension !\n"
                    "<:ScratchCat:1330547949721223238> **/s_profile** ║ Allows you to look at someone's profile easily, with high precision.\n"
                    "🗂️ **/studio** ║ Allows you to preview a studio.\n"
                    "🏷️ **/topic** ║ Previews a forum topic, not that useful right now.\n"
                    "🌟 **/trendscore** ║ Gives a trending score for a specific project, mainly to compare how trendy 2 projects are, can also be used to approximately predict if a project may go on trending.\n"
                    "🌐 **/webstats** ║ Gets statistics about Scratch, such as total projects count.\n"
                    "<:youtube:1340017536409927711> **/yttoscratch** ║ Converts any youtube video link into a forum video link. Better for sharing youtube videos on Scratch.\n"
                    "\n\nNeed assistance, have a suggestion or found a bug? Join our [🔧 support server](https://discord.gg/dgymF2Ye4k)!"
                    "\nBot profile picture by <:AJustEpic:1368235230749528276>AJustEpic, all rights reserved to them and ScratchOn Network."
                ),
                color=scratch_orange,
            )
        )

    @interactions.slash_command(
        name="about",
        description="Everything you need to know about ScratchOn !",
    )
    async def about(self, ctx: interactions.SlashContext):
        language_counts = Counter()

        for guild in self.bot.guilds:
            language_counts[str(guild.preferred_locale)] += 1

        top_languages = language_counts.most_common(2)

        langs = "\n**Top Languages :**\n"
        for i, (lang, count) in enumerate(top_languages, 1):
            langs = f"{langs}\n{i}. {lang} with {count} servers"

        unique_members = set()
        for guild in self.bot.guilds:
            unique_members.update(member.id for member in guild.members)
        total_unique_members = len(unique_members)

        bot_name = self.bot.user.username

        msg = interactions.Embed(title="🤔 About ScratchOn <:BestBot:1388503205373280337> :")
        msg.description = (
            "<:together:1330551758166036500> **Contributors :**\n\n"
            "- <:fluffy:1340009005581598820>** Fluffy**<:separator:1333808735101124668>Basically the bot founder and owner, who coded ScratchOn.\n"
            "- <:timmccool:1340009073990701238>** TimMcCool**<:separator:1333808735101124668>Maker of scratchattach, the python library this bot is mainly based on.\n"
            "- <:kRxZy_kRxZy:1455522693758849156>** kRxZy_kRxZy**<:separator:1333808735101124668>Very skilled ScratchOn Developer, working on this project for free.\n"
            "- <:AJustEpic:1368235230749528276>** A Just Epic**<:separator:1333808735101124668>The amazing artist behind the PFP, who did it for completely free.\n"
            f"- 🫵** You**<:separator:1333808735101124668> {bot_name} user, motivating me to continue updating this bot !\n"
            f"\n📍 **Where is {bot_name} ?** 🌎\n\n"
            f"📈 {bot_name} is in **{len(self.bot.guilds)}** servers, and used by **{total_unique_members}** unique scratchers worldwide. <:together:1330551758166036500>\n"
            f"{langs}"
            "\n\n🔗 **Links :**\n\n"
            f"- [➕ Add {bot_name}](https://discord.com/oauth2/authorize?client_id=1300009645078876170&permissions=274877990912&integration_type=0&scope=bot)\n"
            "- [🔧 Support server](https://discord.gg/dgymF2Ye4k)\n\n"
            f"**⬆️ Help {bot_name} by upvoting it there ⬆️ :**\n"
            "- [Top.gg](https://top.gg/bot/1300009645078876170)\n"
            "- [Discordbotlist.com](https://discordbotlist.com/bots/ScratchOn)\n"
            "- [Discordlist.gg](https://discordlist.gg/bot/1300009645078876170)\n"
            "Or you can directly contribute to the code there : https://github.com/Fluffyscratch/ScratchOn"
        )
        msg.color = scratch_orange
        await ctx.send(embed=msg)

    @interactions.slash_command(
        name="webstats",
        description="Returns statistics about scratch's website.",
    )
    async def webstats(self, ctx: interactions.SlashContext):
        stats = scratch.total_site_stats()

        embeded_message = interactions.Embed(
            title=":bar_chart: Statistics about Scratch :bar_chart:"
        )
        embeded_message.description = (
            f"**On scratch, there are :**\n\n"
            f"- {stats.get('PROJECT_COUNT')} projects 💻\n"
            f"- {stats.get('USER_COUNT')} users <:together:1330551758166036500>\n"
            f"- {stats.get('STUDIO_COUNT')} studios 🗂️\n\n"
            f"**There are {stats.get('COMMENT_COUNT')} comments 💬 :**\n\n"
            f"- {stats.get('PROFILE_COMMENT_COUNT')} are profile comments <:together:1330551758166036500>\n"
            f"- {stats.get('PROJECT_COMMENT_COUNT')} are project comments 💻\n"
            f"- {stats.get('STUDIO_COMMENT_COUNT')} are studio comments 🗂️"
        )
        embeded_message.color = scratch_orange
        await ctx.send(embed=embeded_message)

    @interactions.slash_command(
        name="health",
        description="Gets health data about scratch.",
    )
    async def scratchstatus(self, ctx: interactions.SlashContext):
        original_description = pprint.pformat(scratch.get_health())
        modified_description = re.sub(r"[{},]", "", original_description)
        modified_description = re.sub(r"'([^']+)'", r"**\1**", modified_description)

        await ctx.send(
            embed=interactions.Embed(
                title="❤️‍🩹 Scratch's health status :",
                description=(
                    f"{modified_description}\n\n"
                    "## Tip : press control + F (or command + F on mac) and search the health data you're looking for."
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
    async def yttoscratch(self, ctx: interactions.SlashContext, link: str):
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
    async def tips(self, ctx: interactions.SlashContext):
        msg = interactions.Embed()
        msg.title = "Here are some helpful tips and tricks for scratch !"
        msg.color = scratch_orange
        msg.description = (
            "**Cool emojis compatible with scratch:**\n\n"
            "☠️ ◼️ ◻️ ⚪ ⚫ 🔲 🔳 🔴 🔵 🔶 🔷 🔸 🔹 🟠 🟡 🟢 🔘 🟣 🟤 🔵 🟦 🟩 🟧 🟨 🟩\n"
            "🖤 🤖 📞 ⌛ ⏰ ⏱ 🕰 🔋 🔌 🖤 🛠 🛡 📱 📝 🔨 📖 🍵 ⚽ 🏀 ⚾ 🏐 🏆 🎮 🎯 🚗 🏎\n"
            "💣 🔑 🔒 🔓 🎁 🏠 🏡 🏢 🔑 🔒 🔒 🔌 🏠 🏡 🔷 🌐 💬 ✉ 🧩 🌟 🕹️ 🎮 🖋️ 🎨\n"
            "🎧 🎤 📷 📹 🎬 🏞 🖼 🖊️ 🎞 🎟 🎪 🎭 🎬 🕹️ 🎮 ⌨ 🖱 🔍 📝 🏁 🏆 🏅 🏆\n"
            "🏅 🏆 🏁 🏟 ⛹️‍♂️ 🏋️‍♀️ 💆‍♀️ 🚴‍♀️ 🏊‍♂️ 🤾‍♀️ 🤽‍♀️ 🧘‍♀️ 🎾 🏸 🏓 🏒\n"
            "🎳 🏏 🎯 ⚽ 🏀 🏐 🏓 🏒 🏆 🏅 🏆 ⛳ 🎯 🏆 🏅 🏅 🔗 📎 🖇 🏷️ 🎀 🎁 🧧\n\n"
            "**Scratchmojis :**\n"
            "Cats :\n\n"
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
        )

        msg.add_field(name="<:meow:1330549076223070269>", value="`_meow_`")
        msg.add_field(name="<:Gobo:1330552595390926948>", value="`_gobo_`")
        msg.add_field(name="<:10mil:1330548335471493241>", value="`_10mil_`")
        msg.add_field(name="<:waffle:1335195624127336451>", value="`_waffle_`")
        msg.add_field(name="<:taco:1330548746156638208>", value="`_taco_`")
        msg.add_field(name="<:sushi:1330548721355722817>", value="`_sushi_`")
        msg.add_field(name="<:apple:1330548350663131247>", value="`_apple_`")
        msg.add_field(name="<:broccoli:1330548400214511718>", value="`_broccoli_`")
        msg.add_field(name="<:pizza:1330548624215642183>", value="`_pizza_`")
        msg.add_field(name="<:candycorn:1330548437753794640>", value="`_candycorn_`")
        msg.add_field(name="<:map:1330548598508879922>", value="`_map_`")
        msg.add_field(name="<:camera:1330548417684045854>", value="`_camera_`")
        msg.add_field(name="<:suitcase:1330548697359974512>", value="`_suitcase_`")
        msg.add_field(name="<:compass:1330548457357967360>", value="`_compass_`")
        msg.add_field(name="<:binoculars:1330548366064484422>", value="`_binoculars_`")
        msg.add_field(name="<:cupcake:1330548475359920141>", value="`_cupcake_`")
        msg.add_field(name="<:pride:1330548644859871253>", value="`_pride_`")
        msg.add_field(name="<:blm:1330548384007852032>", value="`_blm_`")

        await ctx.send(embed=msg)

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
    ):
        await ctx.defer()

        audio_data, playback_rate = scratch.text2speech(
            text=text, voice_name=voice, language=language
        )

        audio_file = interactions.File(
            file=io.BytesIO(audio_data),
            file_name="output.mp3",
        )

        await ctx.send(
            embed=interactions.Embed(title="Done! Here is the output ⬆️", color=scratch_orange),
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
            interactions.SlashCommandChoice(name="Scratch 3.0 (high-contrast)", value="scratch3-high-contrast"),
            interactions.SlashCommandChoice(name="Scratch 2.0", value="scratch2"),
        ],
    )
    async def scratchblocks(
        self,
        ctx: interactions.SlashContext,
        code: str,
        style: str = "scratch3",
    ):
        from services import render_blocks_image

        await ctx.defer()
        filename = await render_blocks_image(code=code, style=style)
        await ctx.send(file=interactions.File(file=filename))


def setup(bot: interactions.Client):
    UtilityCommands(bot)
