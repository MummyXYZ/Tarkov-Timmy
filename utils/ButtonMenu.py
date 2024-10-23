from discord.ui import View
from discord import ui
import discord
from typing import Optional, List

class ButtonMenu(View):
    def __init__(self, pages: list, timeout: Optional[float] = None, user: Optional[discord.Member] = None) -> None:
        super().__init__(timeout=timeout)
        self.current_page = 0
        self.pages = pages
        self.user = user
        self.length = len(self.pages) - 1
        self.children[1].label = f'{self.current_page + 1} / {self.length + 1}'
        self.children[0].disabled, self.children[1].disabled = True, True

    async def update(self, page: int):
        self.current_page = page
        self.children[1].label = f'{self.current_page + 1} / {self.length + 1}'
        self.children[0].disabled = page == 0
        self.children[-1].disabled = page == self.length

    async def getPage(self, page) -> tuple[Optional[str], list[discord.Embed], list[discord.File]]:
        if isinstance(page, str):
            return page, [], []
        if isinstance(page, discord.Embed):
            return None, [page], []
        if isinstance(page, discord.File):
            return None, [], [page]
        if isinstance(page, List):
            embeds = [x for x in page if isinstance(x, discord.Embed)]
            files = [x for x in page if isinstance(x, discord.File)]
            if embeds or files:
                return None, embeds, files
            raise TypeError("Page must contain embeds or files.")
        return None, [], []

    async def showPage(self, page: int, interaction: discord.Interaction):
        if not 0 <= page <= self.length:
            raise ValueError("Invalid page number.")
        await self.update(page)
        content, embeds, files = await self.getPage(self.pages[page])
        await interaction.response.edit_message(
            content=content,
            embeds=embeds,
            attachments=files or [],
            view=self
        )

    @ui.button(emoji= '⬅', style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.Button):
        await self.showPage(self.current_page-1, interaction)
    
    @ui.button(label="1 / 1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator_button(self, interaction: discord.Interaction, button: ui.Button):
        pass

    @ui.button(emoji= '➡', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: ui.Button):
        if self.current_page < self.length:
            await self.showPage(self.current_page + 1, interaction)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message(
                    "This command is for someone else",
                    ephemeral=True
                )
                return False

        return True
    
    async def on_timeout(self):
        await self.message.edit(view=None)