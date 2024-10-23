from datetime import datetime
from discord import Embed
from typing import Optional

def embedbuilder(
    author: Optional[str] = None,
    author_url: Optional[str] = None,
    author_icon: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    thumbnail: Optional[str] = None,
    title_url: Optional[str] = None,
    footer: Optional[str] = None,
    footer_icon: Optional[str] = None,
    color: int = 0x000000,
    image_url: Optional[str] = None,
    timestamp: bool = False,
    support: bool = False,
):
    timestamp = datetime.now() if timestamp else None

    if support and description:
        description += "Enjoy using this Bot? Consider upvoting it [Here](https://top.gg/bot/815600918287613962/vote)."

    embed = Embed(
        title=title,
        url=title_url,
        description=description,
        timestamp=timestamp,
        color=color,
    )
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if author:
        embed.set_author(name=author, url=author_url, icon_url=author_icon)
    if footer_icon:
        embed.set_footer(text=footer, icon_url=footer_icon)
    elif footer:
        embed.set_footer(text=footer)
    if image_url:
        embed.set_image(url=image_url)

    return embed
