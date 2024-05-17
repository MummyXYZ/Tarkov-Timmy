from datetime import datetime
from discord import Embed


async def embedbuilder(
    author: str = "",
    author_url: str = "",
    author_icon: str = "",
    title: str = "",
    description: str = "",
    title_url: str = "",
    footer: str = "",
    footer_icon: str = "",
    color: int = 0x000000,
    image_url: str = "",
    timestamp: bool = False,
    support: bool = False,
):
    if timestamp:
        timestamp = datetime.now()
    else:
        timestamp = None

    if support:
        description += "Enjoy using this Bot? Consider upvoting it [Here](https://top.gg/bot/815600918287613962/vote)."

    embed = Embed(
        title=title,
        url=title_url,
        description=description,
        timestamp=timestamp,
        color=color,
    )
    if author:
        embed.set_author(name=author, url=author_url, icon_url=author_icon)
    if footer_icon:
        embed.set_footer(text=footer, icon_url=footer_icon)
    elif footer:
        embed.set_footer(text=footer)
    if image_url:
        embed.set_image(url=image_url)
    # embed.set_thumbnail()

    return embed
