from discord.ui import View
from discord import ui
import discord
from typing import Optional, List

class ButtonMenu(View):
    def __init__(self, pages:list, timeout: Optional[float]=None, user:Optional[discord.Member]=None) -> None:
        super().__init__(timeout=timeout)
        self.current_page= 0
        self.pages = pages
        self.user = user
        self.length = len(self.pages)-1
        self.children[1].label = f'{self.current_page + 1} / {self.length + 1}'
        self.children[0].disabled, self.children[1].disabled = True, True

    async def update(self, page:int):
        self.current_page = page
        self.children[1].label = f'{self.current_page + 1} / {self.length + 1}'
        if page == 0:
            self.children[0].disabled = True
            self.children[-1].disabled = False
        elif page == self.length:
            self.children[0].disabled = False
            self.children[-1].disabled = True
        else:
            self.children[0].disabled = False
            self.children[-1].disabled = False

    async def getPage(self, page):
        if isinstance(page, str):
            return page, [], []
        if isinstance(page, discord.Embed):
            return None, [page], []
        if isinstance(page, discord.File):
            return None, [], [page]
        if isinstance(page, List):
            if all(isinstance(x, discord.Embed) for x in page):
                return None, page, []
            if all(isinstance(x, discord.File) for x in page):
                return None, [], page
            else:
                raise TypeError("Can't Have alternative files and embeds")
        else:
            pass

    async def showPage(self, page:int, interaction:discord.Interaction):
        await self.update(page)
        content, embeds, files = await self.getPage(self.pages[page])

        await interaction.response.edit_message(
            content = content,
            embeds = embeds,
            attachments = files or [],
            view=self
        )

    @ui.button(emoji= '⬅', style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.Button):
        await self.showPage(self.current_page-1, interaction)
    
    @ui.button(label= 'pages',style=discord.ButtonStyle.secondary)
    async def middle_button(self, interaction: discord.Interaction, button: discord.Button):
        pass

    @ui.button(emoji= '➡', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.Button):
        await self.showPage(self.current_page+1, interaction)
    
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