from __future__ import annotations

import discord
import typing
import utils.db as db
from discord import Embed
from discord.ui import View
from utils.checkperms import checkperms as CP
from utils.embedbuilder import embedbuilder as EB

import logging
import logging.handlers

logger = logging.getLogger("discord")

tOut = 60


class PermsView(View):
    def __init__(self, result, target, int: discord.Interaction):
        self.result = result
        self.target = target
        self.int = int
        super().__init__(timeout=tOut)
        self.add_item(
            PermButton(
                result,
                target,
                label="Add",
                custom_id="add_Button",
                style=discord.ButtonStyle.primary
                if self.result[0]
                else discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            PermButton(
                result,
                target,
                label="Edit",
                custom_id="edit_Button",
                style=discord.ButtonStyle.primary
                if self.result[1]
                else discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            PermButton(
                result,
                target,
                label="Remove",
                custom_id="remove_Button",
                style=discord.ButtonStyle.primary
                if self.result[2]
                else discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            PermButton(
                result,
                target,
                label="Leaderboard",
                custom_id="leaderboard_Button",
                style=discord.ButtonStyle.primary
                if self.result[3]
                else discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            PermButton(
                result,
                target,
                label="List",
                custom_id="list_Button",
                style=discord.ButtonStyle.primary
                if self.result[4]
                else discord.ButtonStyle.secondary,
                row=0,
            )
        )
        self.add_item(
            PermButton(
                result,
                target,
                label="Perms",
                custom_id="perms_Button",
                style=discord.ButtonStyle.primary
                if self.result[5]
                else discord.ButtonStyle.secondary,
                row=1,
            )
        )
        self.add_item(
            OtherButton(
                result,
                target,
                emoji="✅",
                style=discord.ButtonStyle.secondary,
                custom_id="confirm",
            )
        )
        self.add_item(
            OtherButton(
                result,
                target,
                emoji="❌",
                style=discord.ButtonStyle.secondary,
                custom_id="cancel",
            )
        )
        self.add_item(
            OtherButton(
                result,
                target,
                label="CLEAR",
                style=discord.ButtonStyle.red,
                custom_id="clear",
            )
        )

    async def on_timeout(self):
        await self.int.edit_original_response(view=None)


class PermButton(discord.ui.Button):
    def __init__(self, result, target, label, custom_id, style, row):
        self.result = result
        self.target = target
        super().__init__(label=label, custom_id=custom_id, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        if self.style == discord.ButtonStyle.secondary:
            self.style = discord.ButtonStyle.primary
        else:
            self.style = discord.ButtonStyle.secondary

        match self.custom_id:
            case "add_Button":
                self.result[0] = 0 if self.result[0] else 1
            case "edit_Button":
                self.result[1] = 0 if self.result[1] else 1
            case "remove_Button":
                self.result[2] = 0 if self.result[2] else 1
            case "leaderboard_Button":
                self.result[3] = 0 if self.result[3] else 1
            case "list_Button":
                self.result[4] = 0 if self.result[4] else 1
            case "perms_Button":
                self.result[5] = 0 if self.result[5] else 1
        await interaction.response.edit_message(
            view=PermsView(self.result, self.self.target, interaction)
        )


class OtherButton(discord.ui.Button):
    def __init__(
        self,
        result,
        target,
        label=None,
        emoji=None,
        custom_id=None,
        row=1,
        style=discord.ButtonStyle.secondary,
    ):
        self.result = result
        self.target = target
        super().__init__(
            label=label, emoji=emoji, custom_id=custom_id, style=style, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        if self.custom_id == "confirm":
            # If exists query
            query = """Select * FROM perms WHERE guild_id = %s AND target_id = %s"""
            params = (interaction.guild_id, self.target.id)
            res = await db.query(query, params)

            if res:
                query = """UPDATE perms SET add_perm = %s, edit = %s, remove = %s, leaderboard = %s, list = %s, perms = %s WHERE guild_id = %s AND target_id = %s"""
                params = (
                    self.result[0],
                    self.result[1],
                    self.result[2],
                    self.result[3],
                    self.result[4],
                    self.result[5],
                    interaction.guild_id,
                    self.target.id,
                )
            else:
                query = """INSERT INTO perms (guild_id, target_id, add_perm, edit, remove, leaderboard, list, perms) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                params = (
                    interaction.guild_id,
                    self.target.id,
                    self.result[0],
                    self.result[1],
                    self.result[2],
                    self.result[3],
                    self.result[4],
                    self.result[5],
                )
            await db.query(query, params)

            if self.target.id == interaction.guild.id:
                embed = await EB(
                    title="TK Perms",
                    description="Permissions have been applied to @everyone...",
                )
            else:
                embed = await EB(
                    title="TK Perms",
                    description=f"Permissions have been applied to <@{self.target.id}>...",
                )

            await interaction.response.edit_message(embed=embed, view=None)

        elif self.custom_id == "cancel":
            if self.target.id == interaction.guild.id:
                embed = await EB(
                    title="TK Perms",
                    description="No changes have been applied to @everyone...",
                )
            else:
                embed = await EB(
                    title="TK Perms",
                    description=f"No changes have been applied to <@{self.target.id}>...",
                )

            await interaction.response.edit_message(embed=embed, view=None)

        elif self.custom_id == "clear":
            query = """DELETE FROM perms WHERE guild_id = %s AND target_id = %s"""
            params = (interaction.guild_id, self.target.id)
            await db.query(query, params)

            if self.target.id == interaction.guild.id:
                embed = await EB(
                    title="TK Perms",
                    description="Permissions have been cleared from @everyone...",
                )
            else:
                embed = await EB(
                    title="TK Perms",
                    description=f"Permissions have been cleared from <@{self.target.id}>...",
                )
            await interaction.response.edit_message(embed=embed, view=None)


class permsSC:
    async def perms(
        interaction: discord.Interaction,
        target: typing.Union[discord.Member, discord.Role] = None,
    ) -> None:
        # Permission Check
        if not await CP(interaction, "perms"):
            return

        guild: discord.Guild = interaction.guild
        desc = ""
        if not target:
            query = f"""SELECT target_id, add_perm, edit, remove, leaderboard, list, perms FROM perms WHERE guild_id = {guild.id}"""
            result = await db.query(query)
            for x in result:
                first = False

                if int(x[0]) == guild.id:
                    desc += "@everyone - "
                else:
                    desc += f"<@{x[0]}> - "

                if x[1]:
                    desc += "Add"
                    first = True
                if x[2]:
                    desc += f"{', ' if first else ''}Edit"
                    first = True
                if x[3]:
                    desc += f"{', ' if first else ''}Remove"
                    first = True
                if x[4]:
                    desc += f"{', ' if first else ''}Leaderboard"
                    first = True
                if x[5]:
                    desc += f"{', ' if first else ''}List"
                    first = True
                if x[6]:
                    desc += f"{', ' if first else ''}Perms"
                    first = True
                if not result[-1][0] == x[0]:
                    desc += "\n"

            embed = await EB(title="TK Perms", description=desc)
            await interaction.followup.send(embed=embed)
            return

        try:
            query = """SELECT add_perm, edit, remove, leaderboard, list, perms FROM perms WHERE guild_id = %s AND target_id = %s"""
            params = (guild.id, target.id)
            result = await db.query(query, params)

            if target.id == guild.id:
                desc += f"Use the buttons below to control @everyone's access to the TK Bot commands.\n**[ENABLED is Blue]** // **[DISABLED is Grey]**\nWhen finished press the ✅ to apply, the ❌ to cancel, or **CLEAR** to remove any permissions from the database.\n\nThis message will timeout in {tOut} seconds."
            else:
                desc += f"Use the buttons below to control <@{target.id}>'s access to the TK Bot commands.\n**[ENABLED is Blue]** // **[DISABLED is Grey]**\nWhen finished press the ✅ to apply, the ❌ to cancel, or **CLEAR** to remove any permissions from the database.\n\nThis message will timeout in {tOut} seconds."

            if not result:
                result.append((0, 0, 0, 0, 0, 0))

            myList = list(result[0])

            view = PermsView(myList, target, interaction)

            embed = await EB(title="TK Perms", description=desc)
            await interaction.followup.send(embed=embed, view=view)

        except Exception as e:
            logger.error(f"Perms error, {e}")
            embed: Embed = await EB(
                title="Error Occured",
                description="There has been an error. Please contact MummyX#2616.",
            )
            await interaction.followup.send(embed=embed)
