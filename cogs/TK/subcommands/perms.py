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

tOut = 60  # Timeout for the view


class PermsView(View):
    def __init__(self, result, target, int: discord.Interaction):
        self.result = result
        self.target = target
        self.int = int
        super().__init__(timeout=tOut)

        # First 5 permission buttons in row 0
        for perm in ["add", "edit", "remove", "leaderboard", "list"]:
            self.add_item(
                PermButton(
                    result,
                    target,
                    label=perm.capitalize(),
                    custom_id=f"{perm}_Button",
                    style=discord.ButtonStyle.primary
                    if self.result[str(target.id)][perm]
                    else discord.ButtonStyle.secondary,
                    row=0,
                )
            )

        # The last permission button in row 1
        self.add_item(
            PermButton(
                result,
                target,
                label="Perms",
                custom_id="perms_Button",
                style=discord.ButtonStyle.primary
                if self.result[str(target.id)]["perms"]
                else discord.ButtonStyle.secondary,
                row=1,  # Moved to row 1
            )
        )

        # Add Confirm, Cancel, and Clear buttons in row 1
        self.add_item(OtherButton(result, target, emoji="✅",
                      style=discord.ButtonStyle.secondary, custom_id="confirm", row=1))
        self.add_item(OtherButton(result, target, emoji="❌",
                      style=discord.ButtonStyle.secondary, custom_id="cancel", row=1))
        self.add_item(OtherButton(result, target, label="CLEAR",
                      style=discord.ButtonStyle.red, custom_id="clear", row=1))

    async def on_timeout(self):
        """Disable the view when the interaction times out."""
        await self.int.edit_original_response(view=None)


class PermButton(discord.ui.Button):
    def __init__(self, result, target, label, custom_id, style, row):
        self.result = result
        self.target = target
        super().__init__(label=label, custom_id=custom_id, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        """Toggle the button style and update the permission value."""
        # Toggle the button style (enabled/disabled)
        self.style = discord.ButtonStyle.primary if self.style == discord.ButtonStyle.secondary else discord.ButtonStyle.secondary

        # Toggle the corresponding permission
        perm_key = self.custom_id.replace("_Button", "")
        self.result[str(self.target.id)][perm_key] = not self.result[str(
            self.target.id)][perm_key]

        # Update the message to reflect the new permission states
        await interaction.response.edit_message(view=PermsView(self.result, self.target, interaction))


class OtherButton(discord.ui.Button):
    def __init__(self, result, target, label=None, emoji=None, custom_id=None, row=1, style=discord.ButtonStyle.secondary):
        self.result = result
        self.target = target
        super().__init__(label=label, emoji=emoji, custom_id=custom_id, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        """Handle confirm, cancel, and clear actions."""
        if int(self.target.id) == interaction.guild.id:
            targetMod = "@everyone"
        elif any(role.id == int(self.target.id) for role in interaction.guild.roles):
            targetMod = f"<@&{self.target.id}>"
        else:
            targetMod = f"<@{self.target.id}>"

        if self.custom_id == "confirm":
            # Apply the permissions changes
            if not any(self.result[str(self.target.id)].values()):
                self.result.pop(str(self.target.id))
            query = "UPDATE tk_bot.perms SET perms = $1 WHERE guild_id = $2"
            params = (json.dumps(self.result), interaction.guild.id)
            await db.execute(query, *params)

            embed = EB(title="TK Perms", description=f"Permissions have been applied to {targetMod}...")

        elif self.custom_id == "cancel":
            embed = EB(title="TK Perms", description=f"No changes have been applied to {targetMod}...")

        elif self.custom_id == "clear":
            # Clear the permissions for the target
            if self.result.get(str(self.target.id)):
                self.result.pop(str(self.target.id))
                query = "UPDATE tk_bot.perms SET perms = $1 WHERE guild_id = $2"
                params = (json.dumps(self.result), interaction.guild.id)
                await db.execute(query, *params)

            embed = EB(title="TK Perms", description=f"Permissions have been cleared from {targetMod}...")

        # Update the message to remove the view after the operation
        await interaction.response.edit_message(embed=embed, view=None)


class permsSC:
    async def perms(
        interaction: discord.Interaction,
        target: typing.Union[discord.Member, discord.Role] = None
    ) -> None:
        await interaction.response.defer()

        # Permission Check
        if not await CP(interaction, "perms"):
            return

        guild: discord.Guild = interaction.guild

        # Fetch permissions from the database using parameterized queries
        query = "SELECT perms FROM tk_bot.perms WHERE guild_id = $1"
        params = (guild.id,)
        result = await db.fetch(query, *params)

        result = result[0]["perms"]
        if isinstance(result, str):
            result = json.loads(result)

        # If no target is provided, display the current permissions
        if not target:
            desc = "No permissions have been set in this server." if not result else ""
            for id, perms in result.items():
                targetMod = "@everyone" if int(id) == guild.id else f"<@&{id}>" if any(role.id == int(id) for role in guild.roles) else f"<@{id}>"
                perm_list = [perm.capitalize() for perm, enabled in perms.items() if enabled]
                desc += f"{targetMod} - {', '.join(perm_list)}\n" if perm_list else f"{targetMod} - No permissions\n"

            embed = EB(title="TK Perms", description=desc)
            await interaction.followup.send(embed=embed)
            return

        # If a target is provided, allow permissions to be edited using buttons
        if not result.get(str(target.id)):
            result[str(target.id)] = {
                "add": False, "edit": False, "remove": False, "leaderboard": False, "list": False, "perms": False,
            }

        desc = f"Use the buttons below to control {target.mention}'s access to the TK Bot commands.\n**[ENABLED is Blue]** // **[DISABLED is Grey]**\nWhen finished, press ✅ to apply, ❌ to cancel, or **CLEAR** to remove any permissions. This message will timeout in {tOut} seconds."

        view = PermsView(result, target, interaction)
        embed = EB(title="TK Perms", description=desc)
        await interaction.followup.send(embed=embed, view=view)
