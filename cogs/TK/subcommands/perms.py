from __future__ import annotations

import discord
import typing
import utils.db as db
import json
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
                if self.result[str(target.id)]["add"]
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
                if self.result[str(target.id)]["edit"]
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
                if self.result[str(target.id)]["remove"]
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
                if self.result[str(target.id)]["leaderboard"]
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
                if self.result[str(target.id)]["list"]
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
                if self.result[str(target.id)]["perms"]
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

        if self.custom_id in [
            "add_Button",
            "edit_Button",
            "remove_Button",
            "leaderboard_Button",
            "list_Button",
            "perms_Button",
        ]:
            value = self.result[str(self.target.id)][
                self.custom_id.replace("_Button", "")
            ]
            self.result[str(self.target.id)][
                self.custom_id.replace("_Button", "")
            ] = not value

        await interaction.response.edit_message(
            view=PermsView(self.result, self.target, interaction)
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
        if int(self.target.id) == interaction.guild.id:
            targetMod = "@everyone"
        elif any(role.id == int(self.target.id) for role in interaction.guild.roles):
            targetMod = f"<@&{self.target.id}>"
        else:
            targetMod = f"<@{self.target.id}>"

        if self.custom_id == "confirm":
            if not any(value for value in self.result[str(self.target.id)].values()):
                self.result.pop(str(self.target.id))
            query = "UPDATE tk_bot.perms SET perms = $1 WHERE guild_id = $2"
            params = (
                json.dumps(self.result),
                interaction.guild_id,
            )
            await db.execute(query, *params)

            embed = EB(
                title="TK Perms",
                description=f"Permissions have been applied to {targetMod}...",
            )

        elif self.custom_id == "cancel":
            embed = EB(
                title="TK Perms",
                description=f"No changes have been applied to {targetMod}...",
            )

        elif self.custom_id == "clear":
            if self.result.get(str(self.target.id)):
                self.result.pop(str(self.target.id))
                query = "UPDATE tk_bot.perms SET perms = $1 WHERE guild_id = $2"
                params = (json.dumps(self.result), interaction.guild_id)
                await db.execute(query, *params)

            embed = EB(
                title="TK Perms",
                description=f"Permissions have been cleared from {targetMod}...",
            )

        await interaction.response.edit_message(embed=embed, view=None)


class permsSC:
    async def perms(
        interaction: discord.Interaction,
        target: typing.Union[discord.Member, discord.Role] = None,
    ) -> None:
        await interaction.response.defer()
        # Permission Check
        if not await CP(interaction, "perms"):
            return

        guild: discord.Guild = interaction.guild
        desc = ""
        if not target:
            query = f"SELECT perms FROM tk_bot.perms WHERE guild_id = '{guild.id}'"

            result = (await db.fetch(query))[0]["perms"]

            if isinstance(result, dict):
                result = json.dumps(result)

            result = json.loads(result)

            if result:
                for id in result:
                    perms = result[id]

                    if int(id) == guild.id:
                        desc += "@everyone - "
                    elif any(role.id == int(id) for role in guild.roles):
                        desc += f"<@&{id}> - "
                    else:
                        desc += f"<@{id}> - "

                    permissions_list = [
                        "Add" if perms["add"] else "",
                        "Edit" if perms["edit"] else "",
                        "Remove" if perms["remove"] else "",
                        "Leaderboard" if perms["leaderboard"] else "",
                        "List" if perms["list"] else "",
                        "Perms" if perms["perms"] else "",
                    ]
                    desc += ", ".join(filter(None, permissions_list))

                    if not list(result)[-1] == int(id):
                        desc += "\n"
            else:
                desc = "No permissions have been set in this server."

            embed = EB(title="TK Perms", description=desc)
            await interaction.followup.send(embed=embed)
            return

        query = f"SELECT perms FROM tk_bot.perms WHERE guild_id = '{guild.id}'"
        result = (await db.fetch(query))[0]["perms"]
        if isinstance(result, dict):
            result = json.dumps(result)

        result = json.loads(result)

        if int(target.id) == guild.id:
            targetMod = "@everyone"
        elif any(role.id == int(target.id) for role in guild.roles):
            targetMod = f"<@&{target.id}>"
        else:
            targetMod = f"<@{target.id}>"

        desc += f"Use the buttons below to control {targetMod}'s access to the TK Bot commands.\n**[ENABLED is Blue]** // **[DISABLED is Grey]**\nWhen finished press the ✅ to apply, the ❌ to cancel, or **CLEAR** to remove any permissions from the database.\n\nThis message will timeout in {tOut} seconds."

        if not result.get(str(target.id)):
            result[str(target.id)] = {
                "add": False,
                "edit": False,
                "remove": False,
                "leaderboard": False,
                "list": False,
                "perms": False,
            }

        view = PermsView(result, target, interaction)

        embed = EB(title="TK Perms", description=desc)
        await interaction.followup.send(embed=embed, view=view)
