import requests
from bs4 import BeautifulSoup

import nextcord
from nextcord.ext import commands

with open("tokens.txt", "r") as t:
    lines = t.readlines()
    token = lines[0].strip()
    testServerId = int(lines[1].strip())

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    await bot.sync_all_application_commands()
    print("Bot is ready and commands are synced!")

@bot.slash_command(guild_ids=[testServerId], name="toriget", description="searches for products on tori.fi")
async def toriget(interaction: nextcord.Interaction, name: str):
    await interaction.response.defer(ephemeral=True)

    html = BeautifulSoup(requests.get(f"https://www.tori.fi/recommerce/forsale/search?q={name.replace(" ", "+")}&sort=PRICE_ASC&trade_type=1").content, "html.parser")

    useful_content = html.find("div", class_="mt-16 grid grid-cols-2 md:grid-cols-3 grid-flow-row-dense gap-16 items-start sf-result-list")

    filtered_content = []
    for item in useful_content:
        price = item.find("span").text
        if price != "Ostetaan":
            filtered_content.append(item)
        

    for item in filtered_content:
        img = item.find("img", class_="w-full h-full object-center object-cover").get("src")
        price = item.find("span").text
        title = item.find("a", class_="sf-search-ad-link s-text! hover:no-underline").text.replace()
        loc = item.find("span", class_="whitespace-nowrap truncate mr-8").text
        link = item.find("a", class_="sf-search-ad-link s-text! hover:no-underline").get("href")
        if not link.startswith("http"):
            link = f"https://www.tori.fi{link}"

        embed = nextcord.Embed(
            title=title,
            url=link,  # Using the corrected link
            description=f"Price: {price}\nLocation: {loc}",
            color=nextcord.Color.blue()
        )
        embed.set_image(url=img)

    await interaction.followup.send(embed=embed)

bot.run(token)