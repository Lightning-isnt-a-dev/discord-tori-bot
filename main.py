import requests
from bs4 import BeautifulSoup

import nextcord
from nextcord.ext import commands

from typing import Optional

import os, subprocess, sys

with open("tokens.txt", "r") as t:
    lines = t.readlines()
    token = lines[0].strip()
    ServerIds = list(lines[1].strip())

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)


class Switcher(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @nextcord.ui.button(label="Previous", style=nextcord.ButtonStyle.blurple)
    async def Previous(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        self.value = "Previous"
        self.stop()
            

    @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.blurple)
    async def Next(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        self.value = "Next"
        self.stop()
    
    @nextcord.ui.button(label="End Search", style=nextcord.ButtonStyle.blurple)
    async def Stop(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        self.value = "Stop"
        self.stop()


@bot.event
async def on_ready():
    await bot.sync_all_application_commands()
    print("Bot is ready and commands are synced!")


@bot.slash_command(guild_ids=ServerIds, name="toriget", description="searches for products on tori.fi")
async def toriget(interaction: nextcord.Interaction, name: str, min_price: Optional[int] = 0, max_price: Optional[int] = 10000000):
    url = f"https://www.tori.fi/recommerce/forsale/search?price_from={min_price}&price_to={max_price}&q={name.replace(" ", "+")}&sort=PRICE_ASC&trade_type=1"

    html = BeautifulSoup(requests.get(url).content, "html.parser")
    useful_content = html.find("div", class_="mt-16 grid grid-cols-2 md:grid-cols-3 grid-flow-row-dense gap-16 items-start sf-result-list")

    embeds = []

    try:
        for item in useful_content:
            img = item.find("img", class_="w-full h-full object-center object-cover")
            img_url = img.get("src") if img else None
            price = item.find("span").text
            title = item.find("a", class_="sf-search-ad-link s-text! hover:no-underline").text
            if "|" in title:
                title.replace("|", "")
            loc = item.find("span", class_="whitespace-nowrap truncate mr-8").text
            link = item.find("a", class_="sf-search-ad-link s-text! hover:no-underline").get("href")
            if not link.startswith("http"):
                link = f"https://www.tori.fi{link}"

            embed = nextcord.Embed(
                title=title,
                url=link,
                description=f"Price: {price}\nLocation: {loc}",
                color=nextcord.Color.blue()
            )
            if img_url:
                embed.set_image(url=img_url)

            embeds.append(embed)

        view = Switcher()
        idx = 0

        await interaction.send(embed=embeds[0], ephemeral=True, view=view)

        while True:
            await view.wait()
            
            if view.value == "Next":
                if idx == len(embeds):
                    await interaction.send("You've reached the end, please go back.", ephemeral=True)
                    view.value = None
                    continue
                
                idx+=1
                
            
            elif view.value == "Previous":
                if idx-1 < 0:
                    await interaction.send("You've reached the end, please go forward.", ephemeral=True)
                    view.value = None
                    continue
                
                idx-=1
            
            elif view.value == "Stop":
                await interaction.edit_original_message(content="Thanks for searching!", embed=None, view=None)
                break

            view = Switcher()
            await interaction.edit_original_message(embed=embeds[idx], view=view)
            view.value = None

    except Exception as e:
        await interaction.send(content=f"couldnt be asked to do proper error checking: {e}", ephemeral=True)

@bot.slash_command(guild_ids=ServerIds, name="shutdown", description="Shuts down the bot.")
async def shutdown(interaction: nextcord.Interaction):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Shutting down the bot...")
        await bot.close()
    else:
        await interaction.response.send_message("You don't have permission to shut down the bot.", ephemeral=True)

@bot.slash_command(guild_ids=ServerIds, name="restart", description="Restarts the bot.")
async def restart(interaction: nextcord.Interaction):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Restarting the bot...", ephemeral=True)
        script_path = os.path.join(os.getcwd(), sys.argv[0])

        subprocess.Popen(["python", script_path])

        await bot.close()
    else:
        await interaction.response.send_message("You do not have permission to restart the bot.", ephemeral=True)

bot.run(token)