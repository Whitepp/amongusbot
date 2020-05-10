import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime


client = discord.Client()

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

url = 'https://docs.google.com/spreadsheets/d/1WI7W0KjLaebqQUuLpf7BqhPYEKnLa2ppNLEiXasOce4/edit#gid=0'

current_time = lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=9)


@client.event
async def on_ready():
    global Harang
    await client.wait_until_ready()
    game = discord.Game("테스트")
    print("login: Harang Main")
    print(client.user.name)
    print(client.user.id)
    print("---------------")
    await client.change_presence(status=discord.Status.online, activity=game)


async def get_spreadsheet(ws_name):
    creds = ServiceAccountCredentials.from_json_keyfile_name("HarangTest-130d0649c09f.json", scope)
    auth = gspread.authorize(creds)

    if creds.access_token_expired:
        auth.login()

    try:
        #worksheet = auth.open('HarangTest').sheet1
        worksheet = auth.open_by_url(url).worksheet(ws_name)
    except gspread.exceptions.APIError:
        return
    return worksheet


def has_role(member, role):
    return role in map(lambda x: x.name, member.roles)


async def get_member_by_battletag(battletag):
    global grace
    grace = client.get_guild(708306592465944587)

    for member in grace.members:
        try:
            if member.nick.startswith(battletag + '/'):
                return member
        except:
            continue


@client.event
async def on_message(message):
    author = message.author
    content = message.content
    channel = message.channel

    print('{} / {}: {}'.format(channel, author, content))

    if message.content.startswith(">>"):
        author = message.content
        author = author.split(">>")
        author = author[1]

        if author == '':
            return

        if author == "운영진":
            spreadsheet = await get_spreadsheet('staff')
            data = spreadsheet.get_all_values()
            log = '\n\n'.join(map(lambda x: '\n'.join([t for t in x if t != '']), data))
            embed = discord.Embed(title=":fire: 운영진 목록\n", description=log, color=0x5c0bb7)
            await channel.send(embed=embed)
            return

        spreadsheet = await get_spreadsheet('responses')
        roles = spreadsheet.col_values(6)
        battletags = spreadsheet.col_values(2)

        nickname = spreadsheet.col_values(3)

        try:
            index = nickname.index(author) + 1
            print(index)
        except gspread.exceptions.CellNotFound:
            return
        except gspread.exceptions.APIError:
            return

        #mention = spreadsheet.cell(index, 1).value
        battletag = spreadsheet.cell(index, 2).value
        link = spreadsheet.cell(index, 4).value
        description = spreadsheet.cell(index, 5).value
        imagelink = spreadsheet.cell(index, 6).value
        thumbnaillink = spreadsheet.cell(index, 7).value
        league = spreadsheet.cell(index, 8).value
        print(index, battletag, link, description, imagelink, thumbnaillink, league)

        member = await get_member_by_battletag(battletag)
        if member == None:
            return
        elif has_role(member, '클랜 마스터'):
            role = '클랜 마스터'
        elif has_role(member, '운영진'):
            role = '운영진'
        elif has_role(member, '클랜원'):
            role = '클랜원'
        elif has_role(member, '신입 클랜원'):
            role = '신입 클랜원'
        else:
            return

        print(battletag)
        print(role)
        if role == "클랜 마스터":
            roleimage = ":pen_ballpoint:"
        elif role == "운영진":
            roleimage = ":construction_worker:"
        elif role == "클랜원":
            roleimage = ":boy:"
        elif role == "신입 클랜원":
            roleimage = ":baby:"

        embed = discord.Embed(title="한줄소개", description=description, color=0x5c0bb7)
        if link is not '':
            embed = discord.Embed(title="바로가기", url=link, description=description, color=0x5c0bb7)

        embed.set_author(name=battletag)
        embed.add_field(name="League", value=":trophy: 제" + league + "회 우승", inline=False)
        embed.add_field(name="직책", value=roleimage + role, inline=True)
        if imagelink is not '':
            embed.set_image(url=imagelink)
        if thumbnaillink is not '':
            embed.set_thumbnail(url=thumbnaillink)

        await channel.send(embed=embed)

client.run("NzA4MzAzMDc0NTE4NjMwNDY0.XrVYug.ZqLaCm7Rb2-QdMN2Z_0OssYLtgE")