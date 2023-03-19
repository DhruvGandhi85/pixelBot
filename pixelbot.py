import os
from typing import List
from contextlib import suppress

import discord
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from bs4 import BeautifulSoup
from scipy.stats import linregress
from discord.ext import commands
from tabulate import tabulate


def get_user_url(user_id: str) -> str:
    return f"https://plancke.io/hypixel/player/stats/{user_id}"


def get_guild_url(user_id: str) -> str:
    return f"https://plancke.io/hypixel/guild/player/{user_id}"


def get_soup(url) -> BeautifulSoup:
    response = requests.get(
        url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(response, 'html.parser')
    return soup


def get_user_profile(url) -> pd.DataFrame:
    soup = get_soup(url)

    card_box = soup.find_all('div', {'class': 'card-box'})[0]

    tableList = ['Player Name', 'Rank History', 'Multiplier', 'Level', 'Karma',
                 'Achievement Points', 'Quests Completed', 'First login', 'Last login']
    textList = ['Player Name', 'Rank History', 'Multiplier:', 'Level:', 'Karma:',
                'Achievement Points:', 'Quests Completed:', 'First login: ', 'Last login: ']
    player_name, rank_history, multiplier, level, karma, achievement_points, quests_completed, first_login, last_login = 0, 0, 0, 0, 0, 0, 0, 0, 0
    statList = [player_name, rank_history, multiplier, level, karma,
                achievement_points, quests_completed, first_login, last_login]

    for i in range(len(textList)):
        if textList[i] == 'Player Name':
            statList[i] = card_box.find('span').text.strip()
        else:
            statList[i] = card_box.find(
                'b', text=textList[i]).next_sibling.text.strip()

    user_stats = dict(zip(tableList, statList))
    df_user = pd.DataFrame.from_dict(
        user_stats, orient='index', columns=[''])

    return df_user


def get_user_guild(url) -> pd.DataFrame:
    soup = get_soup(url)

    card_box = soup.find_all('div', {'class': 'card-box'})[1]

    tableList = ['Name', 'Members', 'Rank', 'Joined']
    textList = ['Name: ', 'Members: ', 'Rank: ', 'Joined: ']
    name, members, rank, joined = 0, 0, 0, 0
    statList = [name, members, rank, joined]

    for i in range(len(textList)):
        statList[i] = card_box.find(
            'b', text=textList[i]).next_sibling.text.strip()

    guild_stats = dict(zip(tableList, statList))
    df_guild = pd.DataFrame.from_dict(
        guild_stats, orient='index', columns=[''])

    return df_guild


def get_user_status(url) -> pd.DataFrame:
    soup = get_soup(url)

    card_box = soup.find_all('div', {'class': 'card-box'})[2]

    textList = ['Status']
    status = 0
    statList = [status]

    for i in range(len(textList)):
        statList[i] = card_box.find(
            'b').text.strip()

    status_stats = dict(zip(textList, statList))
    df_status = pd.DataFrame.from_dict(
        status_stats, orient='index', columns=[''])

    return df_status


def get_user_socials(url) -> pd.DataFrame:
    soup = get_soup(url)
    card_box = soup.find_all('div', {'class': 'card-box'})
    if card_box[3] is not None:
        card_box = card_box[3]
    tableList = ['Twitter', 'Youtube', 'Instagram',
                 'TikTok', 'Twitch', 'Discord', 'Hypixel Forums']
    textList = ['social_TWITTER', 'social_YOUTUBE',  'social_INSTAGRAM',
                'social_TIKTOK', 'social_TWITCH', 'social_DISCORD', 'social_HYPIXEL']
    twitter, youtube, instagram, tiktok, twitch, discord, hypixel_forums = 0, 0, 0, 0, 0, 0, 0
    statList = [twitter, youtube, instagram,
                tiktok, twitch, discord, hypixel_forums]
    for i in range(len(textList)):
        if card_box.find('a', id=textList[i]) is None:
            statList[i] = "N/A"
        elif card_box.find('a', id=textList[i])['href'] == "javascript:void(0)":
            soup = get_soup(url)
            javascript_disc = soup.find_all('script')[-3]
            if javascript_disc is not None:
                javascript_disc = javascript_disc.text.strip().replace('$(document).ready(function () {', '').replace(
                    '$("#social_DISCORD").click(function () {', '').replace('})', '').replace(');', '').replace('"', '').strip().split(', ')[1]
                statList[i] = javascript_disc
        else:
            statList[i] = card_box.find('a', id=textList[i])['href']

    user_socials = dict(zip(tableList, statList))
    df_socials = pd.DataFrame.from_dict(
        user_socials, orient='index', columns=[''])

    return df_socials


def get_bedwars_stats(url) -> pd.DataFrame:
    soup = get_soup(url)
    tableList = ['Coins', 'Winstreak', 'Level', 'Diamonds Collected',
                 'Emeralds Collected', 'Gold Collected', 'Iron Collected']
    textList = ['Coins:', 'Winstreak:', 'Level:', 'Diamonds Collected:',
                'Emeralds Collected:', 'Gold Collected:', 'Iron Collected:']
    coins, winstreak, level, diamonds_collected, emeralds_collected, gold_collected, iron_collected = 0, 0, 0, 0, 0, 0, 0
    statList = [coins, winstreak, level, diamonds_collected,
                emeralds_collected, gold_collected, iron_collected]
    bed_wars_box = soup.find('div', {'id': 'stat_panel_BedWars'})
    for i in range(len(textList)):
        statList[i] = bed_wars_box.find(
            'b', text=textList[i]).next_sibling.text.strip()
    bedwars_stats = dict(zip(tableList, statList))
    df_bed = pd.DataFrame.from_dict(
        bedwars_stats, orient='index', columns=[''])
    return df_bed


def get_bedwars_table(url) -> pd.DataFrame:
    soup = get_soup(url)
    bed_wars_box = soup.find('div', {'id': 'stat_panel_BedWars'})
    bed_wars_table = bed_wars_box.find('table', {'class': 'table'})

    data = []
    headers = ['', 'Normal ', 'Normal ', 'Normal ', 'Final ',
               'Final ', 'Final ', 'Total ', 'Total ', 'Total ', 'Total ']
    rows = bed_wars_table.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])
        data.append([cell.get_text(strip=True) for cell in cells])
    df_bed_table = pd.DataFrame(data)
    df_bed_table = df_bed_table.drop(index=0)
    for i, col in enumerate(df_bed_table.columns):
        df_bed_table.iloc[0, i] = headers[i] + str(df_bed_table.iloc[0, i])
    df_bed_table.columns = df_bed_table.iloc[0]
    df_bed_table = df_bed_table.drop(index=1)
    df_bed_table.fillna('', inplace=True)
    return df_bed_table


def get_skywars_stats(url) -> pd.DataFrame:
    soup = get_soup(url)
    tableList = ['Level', 'Prestige', 'Coins', 'Kills', 'Assists', 'Deaths', 'Kill/Death Ratio', 'Wins', 'Losses', 'Win/Loss Ratio', 'Blocks Broken', 'Blocks Placed',
                 'Soul Well Uses', 'Soul Well Legendaries', 'Soul Well Rares', 'Paid Souls', 'Souls Gathered', 'Eggs Thrown', 'Enderpearls', 'Arrows Shot', 'Arrows Hit', 'Arrow Hit/Miss Ratio']
    textList = ['Level:', 'Prestige:', 'Coins:', 'Kills:', 'Assists:', 'Deaths:', 'Kill/Death Ratio:', 'Wins:', 'Losses:', 'Win/Loss Ratio:', 'Blocks Broken:', 'Blocks Placed:',
                'Soul Well Uses:', 'Soul Well Legendaries:', 'Soul Well Rares:', 'Paid Souls:', 'Souls Gathered:', 'Eggs Thrown:', 'Enderpearls Thrown:', 'Arrows Shot:', 'Arrows Hit:', 'Arrow Hit/Miss Ratio:']
    level, prestige, coins, kills, assists, deaths, kdr, wins, losses, wlr, blocks_broken, blocks_placed, soul_well_uses, soul_well_legendaries, soul_well_rares, paid_souls, souls_gathered, eggs_thrown, enderpearls, arrows_shot, arrows_hit, arrow_hmr = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    statList = [level, prestige, coins, kills, assists, deaths, kdr, wins, losses, wlr, blocks_broken, blocks_placed,  soul_well_uses,
                soul_well_legendaries, soul_well_rares, paid_souls, souls_gathered, eggs_thrown, enderpearls, arrows_shot, arrows_hit, arrow_hmr]
    sky_wars_box = soup.find('div', {'id': 'stat_panel_SkyWars'})
    for i in range(len(textList)):
        statList[i] = sky_wars_box.find(
            'b', text=textList[i]).next_sibling.text.strip()
    skywars_stats = dict(zip(tableList, statList))
    df_sky = pd.DataFrame.from_dict(
        skywars_stats, orient='index', columns=[''])
    return df_sky


def get_skywars_table(url) -> pd.DataFrame:
    soup = get_soup(url)
    sky_wars_box = soup.find('div', {'id': 'stat_panel_SkyWars'})
    sky_wars_table = sky_wars_box.find('table', {'class': 'table'})
    data = []
    rows = sky_wars_table.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])
        data.append([cell.get_text(strip=True) for cell in cells])
    df_sky_table = pd.DataFrame(data)

    df_sky_table.columns = df_sky_table.iloc[0]
    df_sky_table = df_sky_table.drop(index=0)
    df_sky_table.replace('-', np.nan, inplace=True)
    df_sky_table.replace('', np.nan, inplace=True)
    df_sky_table = df_sky_table.apply(lambda x: x.str.replace(',', '')
                                      if x.dtype == "object" else x)
    df_sky_table = df_sky_table.astype(
        {'Kills': float, 'Deaths': float, 'K/D': float, 'Wins': float, 'Losses': float, 'W/L': float})
    df_sky_table.loc[len(df_sky_table.index)] = ['Overall', df_sky_table['Kills'].sum(), df_sky_table['Deaths'].sum(
    ), df_sky_table['K/D'].sum(), df_sky_table['Wins'].sum(), df_sky_table['Losses'].sum(), df_sky_table['W/L'].sum()]
    return df_sky_table


def combine_features(df, table_type) -> pd.DataFrame:
    df_vector = df.copy()
    if table_type == 'bedwars':
        df_vector['Final Kills'] = df_vector['Final Kills'].apply(
            lambda x: x*3)
        df_vector['Final Deaths'] = df_vector['Final Deaths'].apply(
            lambda x: x*-3)
        df_vector['Final K/D'] = df_vector['Final K/D'].apply(lambda x: x*2)
        df_vector['Total Wins'] = df_vector['Total Wins'].apply(lambda x: x*5)
        df_vector['Total Losses'] = df_vector['Total Losses'].apply(
            lambda x: x*-5)
        df_vector['Total W/L'] = df_vector['Total W/L'].apply(lambda x: x*5)
        df_vector['Total Beds Broken'] = df_vector['Total Beds Broken'].apply(
            lambda x: x*2)
    elif table_type == 'skywars':
        df_vector['Kills'] = df_vector['Kills'].apply(
            lambda x: x*5)
        df_vector['Deaths'] = df_vector['Deaths'].apply(
            lambda x: x*-5)
        df_vector['K/D'] = df_vector['K/D'].apply(lambda x: x*4)
        df_vector['Wins'] = df_vector['Wins'].apply(lambda x: x*3)
        df_vector['Losses'] = df_vector['Losses'].apply(
            lambda x: x*-5)
        df_vector['W/L'] = df_vector['W/L'].apply(lambda x: x*2)
    colList = list(df_vector.columns)
    df_vector['Grade'] = df_vector[colList].sum(axis=1)
    df_vector = df_vector['Grade']
    return df_vector


def vectorize(df, table_type) -> pd.DataFrame:
    if table_type == 'bedwars':
        df = df.drop(columns=['Type', 'Normal Kills',
                     'Normal Deaths', 'Normal K/D'])
    elif table_type == 'skywars':
        df = df.drop(columns=['Mode'])
    df.replace('-', np.nan, inplace=True)
    df.replace('', np.nan, inplace=True)
    df = df.apply(lambda x: x.str.replace(',', '')
                  if x.dtype == "object" else x)
    df = df.astype(float)
    df_vector = combine_features(df, table_type)
    df = pd.concat([df, df_vector], axis=1)
    return df


def compare_users(user_id, user_source, game_mode) -> pd.DataFrame:
    comparison = []
    new_list = []
    user_list = []
    if user_source == 'guild':
        guild_url = get_soup(get_guild_url(user_id))
        guild_body = guild_url.find('tbody')
        rows = guild_body.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            comparison.append([cell.get_text(strip=True) for cell in cells])
        new_list = comparison.copy()
        user_list = comparison.copy()
        for i in range(len(comparison)):
            new_list[i] = comparison[i][0]
            user_list[i] = new_list[i].split(' ')[1]
    else:
        user_list.append(user_id)
        user_list.append(user_source)
    user_grades = user_list.copy()
    for i in range(len(user_list)):
        if game_mode == 'bedwars':
            df_grades = vectorize(get_bedwars_table(
                get_user_url(user_list[i])), 'bedwars')
        if game_mode == 'skywars':
            df_grades = vectorize(get_skywars_table(
                get_user_url(user_list[i])), 'skywars')
        user_grades[i] = df_grades['Grade'].iloc[-1]
    user_dict = dict(zip(user_list, user_grades))
    df_compare = pd.DataFrame.from_dict(
        user_dict, orient='index', columns=[''])
    df_compare.sort_values(by=[''], ascending=False, inplace=True)
    return df_compare


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='.', intents=intents)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$user'):
        args = message.content.split(' ')
        user_url = get_user_url(args[1])

        if len(args) == 1:
            user_profile = get_user_profile(user_url).to_string()
            output = '```' + user_profile + '```'
            return await message.channel.send(output)
        elif len(args) == 3 and args[2] == 'guild':
            user_guild = get_user_guild(user_url).to_string()
            output = '```' + user_guild + '```'
            return await message.channel.send(output)
        elif len(args) == 3 and args[2] == 'status':
            user_status = get_user_status(user_url).to_string()
            output = '```' + user_status + '```'
            return await message.channel.send(output)
        elif len(args) == 3 and args[2] == 'socials':
            user_socials = get_user_socials(user_url).to_string()
            output = '```' + user_socials + '```'
            return await message.channel.send(output)
        elif len(args) == 3 and args[2] == 'bedwars':
            bedwars_stats = get_bedwars_stats(user_url).to_string()
            output = '```' + bedwars_stats + '```'
            return await message.channel.send(output)
        elif len(args) == 3 and args[2] == 'skywars':
            skywars_stats = get_skywars_stats(user_url).to_string()
            output = '```' + skywars_stats + '```'
            return await message.channel.send(output)
        elif len(args) == 4 and args[2] == 'bedwars' and args[3] == 'table':
            bedwars_table = get_bedwars_table(user_url)
            formatted_table = tabulate(bedwars_table.values, headers=list(
                bedwars_table.columns), tablefmt='plain')
            chunks = [formatted_table[i:i+1000]
                      for i in range(0, len(formatted_table), 1000)]
            for chunk in chunks:
                await message.channel.send(f'```{chunk}```')
        elif len(args) == 4 and args[2] == 'skywars' and args[3] == 'table':
            skywars_table = get_skywars_table(user_url)
            formatted_table = tabulate(skywars_table.values, headers=list(
                skywars_table.columns), tablefmt='plain')
            chunks = [formatted_table[i:i+1000]
                      for i in range(0, len(formatted_table), 1000)]
            for chunk in chunks:
                await message.channel.send(f'```{chunk}```')
        else:
            output = 'Invalid command. Please try again.'
            await message.channel.send(output)
    if message.content.startswith('$compare'):
        args = message.content.split(' ')
        user_url = get_user_url(args[1])

        if len(args) == 4 and args[2] == 'guild':
            if args[3] == "bedwars":
                compare = compare_users(args[1], 'guild', 'bedwars')
                output = '```' + compare.to_string() + '```'
                return await message.channel.send(output)
            elif args[3] == "skywars":
                compare = compare_users(args[1], 'guild', 'skywars')
                output = '```' + compare.to_string() + '```'
                return await message.channel.send(output)
        elif len(args) == 4 and args[2] != 'guild':
            if args[3] == "bedwars":
                compare = compare_users(args[1], args[2], 'bedwars')
                output = '```' + compare.to_string() + '```'
                return await message.channel.send(output)
            elif args[3] == "skywars":
                compare = compare_users(args[1], args[2], 'skywars')
                output = '```' + compare.to_string() + '```'
                return await message.channel.send(output)
        else:
            output = 'Invalid command. Please try again.'
            await message.channel.send(output)

with open('token.txt', 'r') as f:
    token = f.readline()
client.run(token)
