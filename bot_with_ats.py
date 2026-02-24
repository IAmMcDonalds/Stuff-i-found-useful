
import discord
from discord.ext import commands ,tasks
from discord import app_commands
import requests
import random
import json
import logging
import asyncio
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
import os


# idk this works, dont change
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.presences = True
intents.voice_states = True
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=",", intents=intents)

#logging.basicConfig(level=logging.INFO)

API_KEY = 'bungie api key here'
BASE_URL = 'https://www.bungie.net/Platform'
BUNGIE_API_KEY = 'different bungie api key here'
headers = {'X-API-Key': BUNGIE_API_KEY}
gAPI_KEY = 'idk what i used this for but im too scared to delete it'
gUSER_ID = 'idk what this is either but same reason as above' # i think it might have been a gelbooru api key but im not sure

logger = logging.getLogger(__name__)

D_SERVER_ID = 1155741159595966525  
L_SERVER_ID = 1209543967516004412  


#vc shit

WATCH_CHANNEL_ID = 1456196095528009839  
GUILD_ID = 1155741159595966525         

#botinfo shit
message_count = 0

server_message_counts = defaultdict(int)


# clan names go here
#  "name": "NAME FOR DISCORD", "id": "ID OF BUNGIE CLAN": DISCORD ROLE ID
# only used for .nuin

clans = [
#    {"name": "[Ω] Aphelion Clan", "id": "4291993", "role_id": 1169216268499435520},
    {"name": "[Ω] Aegis Clan", "id": "4924025", "role_id": 1159364367654064148},
    {"name": "[Ω] Kingslayers Clan", "id": "5150042", "role_id": 1156352868870266880},
    {"name": "[Ω] Barons Clan", "id": "4595985", "role_id": 1159202000303566929},
    {"name": "[Ω] Eternal Clan", "id": "5202951", "role_id": 1191386877555642438},
    {"name": "[Ω] Avalon Clan", "id": "4966586", "role_id": 1305641403686326272},
    {"name": "[Ω] Zenith Clan", "id": "5318667", "role_id": 1328760918770974720},
    {"name": "[Ω] Wrath Clan", "id": "5189664", "role_id": 1342162798137966662},
    {"name": "[Ω] Mythos Clan", "id": "5340477", "role_id": 1342163642464075942},
    {"name": "[Ω] Abyss Clan", "id": "5370770", "role_id": 1342163966142447717},
]

# only used for cless
Dclanlesss = [
#    {"name": "[Ω] Aphelion Clan", "id": "4291993", "role_id": 1157120847723634730},
    {"name": "[Ω] Aegis Clan", "id": "4924025", "role_id": 1157120847723634730},
    {"name": "[Ω] Kingslayers Clan", "id": "5150042", "role_id": 1157120847723634730},
    {"name": "[Ω] Barons Clan", "id": "4595985", "role_id": 1157120847723634730},
    {"name": "[Ω] Eternal Clan", "id": "5202951", "role_id": 1157120847723634730},
    {"name": "[Ω] Avalon Clan", "id": "4966586", "role_id": 1157120847723634730},
    {"name": "[Ω] Zenith Clan", "id": "5318667", "role_id": 1157120847723634730},
    {"name": "[Ω] Wrath Clan", "id": "5189664", "role_id": 1157120847723634730},
    {"name": "[Ω] Mythos Clan", "id": "5340477", "role_id": 1157120847723634730},
    {"name": "[Ω] Abyss Clan", "id": "5370770", "role_id": 1157120847723634730},
]

Lclanlesss = [
    {"name": "ethereal", "id": "5313354", "role_id": 1295446597911707699, "other_role": 1321258153177776128},

]

#fuck you
specified_role_ids = { 
    1155920950676697188, # com staff
    1334544381038039095, # trial
    1155929880316346479, # disco leader
    1267814116567945288 # flake muffin
}

#bungie shit

raids = ["Vault of Glass", "Deep Stone Crypt", "King’s Fall", "Last Wish", "Crota’s End", "Garden of Salvation", "Vow of the Disciple","Salvations Edge", "Desert Perpetual"]
dungeons = ["Pit of Heresy", "Grasp of Avarice", "Shattered Throne", "Ghosts of the Deep", "Duality", "Prophecy", "Shattered Throne", "Sundered doctrine" ,"Vespers Host" ,"equilibrium"]

def get_clan_members(group_id):
    endpoint = f'/GroupV2/{group_id}/Members/'
    url = BASE_URL + endpoint
    headers = {'X-API-Key': API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['ErrorCode'] == 1:  
            return data['Response']['results']
        else:
            return None
    else:
        print("Error:", response.status_code, response.text)
        return None

# if the 4 numbers at the end of the name starts with a 0, this will make it show a 0 

def format_bungie_display_name(member):
    display_name = member['destinyUserInfo']['bungieGlobalDisplayName']
    display_code = str(member['destinyUserInfo']['bungieGlobalDisplayNameCode'])
    if len(display_code) == 3:
        display_code = f'0{display_code}'
    return f"{display_name}#{display_code}"

# data base shit
conn = sqlite3.connect('TheEye.db')
c = conn.cursor()
cursor = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS post_ratings (
    post_id TEXT PRIMARY KEY,
    upvotes INTEGER,
    downvotes INTEGER,
    comments INTEGER,
    original_poster TEXT,
    discord_user_id TEXT,
    creation_date TEXT
)
''')
conn.commit()

c.execute('''
CREATE TABLE IF NOT EXISTS clans (
    id TEXT PRIMARY KEY,
    name TEXT,
    role_id INTEGER,
    server_id INTEGER
)
''')
conn.commit()

c.execute('''
CREATE TABLE IF NOT EXISTS servers (
    id TEXT PRIMARY KEY,
    server_name TEXT,
    server_id INTEGER
)
''')
conn.commit()

c.execute('''
CREATE TABLE IF NOT EXISTS UpOrDown (
    time TEXT PRIMARY KEY,
    post_id TEXT,
    server_name TEXT,
    up INTERGER,
    down INTERGER
)
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_roles (
        user_id INTEGER,
        nickname TEXT,
        role_id INTEGER,
        assignment_count INTEGER DEFAULT 0,
        last_post_time TEXT,
        has_role INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, role_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS role_assignment_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nickname TEXT,
        role_id INTEGER,
        assignment_time TEXT
    )
''')

conn.commit()

monitoring_tasks = {}

@bot.event
async def on_ready():
    print(f'{bot.user} is ready.')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s).')
    
    except Exception as e:
        print(f'Failed to sync commands: {e}')

# commands

@bot.event
async def setup_hook():
    await bot.tree.sync()
#    check_user_roles.start()

#kill your self



@bot.listen('on_member_update')
async def on_role_update(before: discord.Member, after: discord.Member):
    for role in after.roles:
        if role not in before.roles:
            nickname = after.nick if after.nick else after.name
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO user_roles (user_id, nickname, role_id, assignment_count, last_post_time, has_role)
                VALUES (?, ?, ?, 1, ?, 1)
                ON CONFLICT(user_id, role_id) DO UPDATE SET assignment_count = assignment_count + 1, has_role = 1
            ''', (after.id, nickname, role.id, current_time))
            cursor.execute('''
                INSERT INTO role_assignment_log (user_id, role_id, assignment_time)
                VALUES (?, ?, ?)
            ''', (after.id, role.id, current_time))
            # fucking kill your self trying to figure out what the fuck to do about remove_time
            print(f"Role {role.name} added to {after.name} at {current_time}")
    for role in before.roles:
        if role not in after.roles:
            cursor.execute('''
                UPDATE user_roles SET has_role = 0 WHERE user_id = ? AND role_id = ?
            ''', (after.id, role.id))
            
            print(f"Role {role.name} removed from {after.name}")
    if before.nick != after.nick:
        new_nick = after.nick if after.nick else after.name
        cursor.execute('''
            UPDATE user_roles SET nickname = ?
            WHERE user_id = ?
        ''', (new_nick, after.id))
        conn.commit()
        print(f"Updated nickname from {before.nick} to {new_nick}")

    conn.commit()

@bot.listen('on_message')
async def on_message(message: discord.Message):
    global message_count
    if message.author.bot or message.channel.id == 1225192976188440646:
        return
    message_count += 1

    if message.guild:
        server_message_counts[message.guild.id] += 1

    last_post_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nickname = message.author.nick if message.author.nick else message.author.name

    for role in message.author.roles:
        if role.id != message.guild.id: 
            cursor.execute('''
                INSERT INTO user_roles (user_id, nickname, role_id, assignment_count, last_post_time, has_role)
                VALUES (?, ?, ?, 1, ?, 1)
                ON CONFLICT(user_id, role_id) DO UPDATE SET 
                assignment_count = excluded.assignment_count + 1, 
                last_post_time = excluded.last_post_time,
                has_role = excluded.has_role
            ''', (message.author.id, nickname, role.id, last_post_time))

    conn.commit()
    print(f"Updated last post time for {message.author.name}")


@bot.event
async def on_member_remove(member: discord.Member):
    print(f"{member.display_name} has left the server")
    cursor.execute('''
        UPDATE user_roles
        SET has_role = 0
        WHERE user_id = ?
    ''', (member.id,))
    conn.commit()
    print(f"{member.display_name} has fucked off their roles")

@bot.tree.command(name="botinfo", description="Show bot info")
async def botinfo(interaction: discord.Interaction):
    global message_count

    guilds = bot.guilds
    embed = discord.Embed(
        title="Bot Information",
        description=f"The bot is currently in **{len(guilds)}** servers:\n\n"
                    f"Total messages processed since startup: **{message_count}**\n\n",
        color=discord.Color.green()
    )

    for guild in guilds:
        msgs = server_message_counts.get(guild.id, 0)
        embed.add_field(name=guild.name, value=f"Messages: {msgs}", inline=False)

    await interaction.response.send_message(embed=embed)



def split_message(message, char_limit=2000):
    """Helper function to split messages into chunks."""
    lines = message.split('\n')
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 > char_limit:
            yield current_chunk
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'

    if current_chunk:
        yield current_chunk

# never try to change this. you cant remember how to fix it
def get_post_details(post_id):
    try:
        url = f'https://www.bungie.net/Platform/Forum/GetPostAndParent/{post_id}/?showbanned=True'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('Response', {})
            post = data.get('results', [{}])[0]
            upvotes = post.get('upvotes', 0)
            downvotes = post.get('downvotes', 0)
            comments = post.get('replyCount', 0)
            creation_date = post.get('creationDate', '')
            membership_id = post.get('authorMembershipId', '')
            original_poster = next((author.get('displayName', 'Unknown') for author in data.get('authors', []) if author.get('membershipId') == membership_id), 'Unknown')
            return upvotes, downvotes, comments, original_poster, creation_date
    except Exception as e:
        logging.error(f"Error fetching post details: {e}")
    return None, None, None, None

def log_rating_change(post_id, server_name, up, down):
    if up != 0 or down != 0: 
        current_time = datetime.now().isoformat()
        c.execute('''
            INSERT INTO UpOrDown (time, post_id, server_name, up, down)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_time, post_id, server_name, up, down))
        conn.commit()

async def cancel_existing_task(server_id):
    """Cancel any existing monitoring task for the given server."""
    if server_id in monitoring_tasks:
        monitoring_tasks[server_id].stop()
        try:
            await monitoring_tasks[server_id]
        except asyncio.CancelledError:
            logging.info(f"Cancelled existing monitoring task for server {server_id}.")

async def monitor_post_details(post_id: str, channel: discord.TextChannel):
    server_id = channel.guild.id
    logging.info(f"Starting to monitor post ID {post_id} on server {server_id}.")
    while True:
        current_upvotes, current_downvotes, current_comments, _, creation_date = get_post_details(post_id)
        
        if current_upvotes is not None:
            c.execute("SELECT upvotes, downvotes, comments FROM post_ratings WHERE post_id = ?", (post_id,))
            row = c.fetchone()
            logging.info(f"Fetched previous data for post ID {post_id}: {row}")
            
            if row is None:
                previous_upvotes, previous_downvotes, previous_comments = (0, 0, 0)
            else:
                previous_upvotes, previous_downvotes, previous_comments = row
            
            logging.info(f"Current data fetched for post ID {post_id}: Upvotes={current_upvotes}, Downvotes={current_downvotes}, Comments={current_comments}")
            
            if (current_upvotes != previous_upvotes or
                current_downvotes != previous_downvotes or
                current_comments != previous_comments):
                logging.info(f"Detected changes for post ID {post_id}.")
                
                up_change = current_upvotes - previous_upvotes
                down_change = current_downvotes - previous_downvotes
                log_rating_change(post_id, channel.guild.name, up_change, down_change)

                if row is None:
                    c.execute("INSERT INTO post_ratings (post_id, upvotes, downvotes, comments, creation_date) VALUES (?, ?, ?, ?, ?)",
                              (post_id, current_upvotes, current_downvotes, current_comments, creation_date))
                else:
                    c.execute("UPDATE post_ratings SET upvotes = ?, downvotes = ?, comments = ? WHERE post_id = ?",
                              (current_upvotes, current_downvotes, current_comments, post_id))
                
                conn.commit()
                
                await channel.send(
                    f"Post ID {post_id} has been updated:\n"
                    f"Upvotes: {current_upvotes}\n"
                    f"Downvotes: {current_downvotes}\n"
                    f"Comments: {current_comments}."
                )
        
        await asyncio.sleep(120)  # Sleep for x seconds



@bot.event
async def on_user_update(before: discord.User, after: discord.User):
    if before.name != after.name:
        cursor.execute('''
            UPDATE user_roles SET nickname = ?
            WHERE user_id = ?
        ''', (after.name, after.id))
        conn.commit()
        print(f"Updated nickname from {before.name} to {after.name}")

@bot.tree.command(name="nuin", description="Number in role")
async def nuin(interaction: discord.Interaction, role: discord.Role):
    members_with_role = [member for member in role.guild.members if role in member.roles]
    total_members = len(members_with_role)
    await interaction.response.send_message(f"Members in '{role.name}': {total_members}")
    print(f'nuin command executed.')

def is_admin():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        else:
            await interaction.response.send_message("You do not have the necessary permissions to execute this command.", ephemeral=True)
            print(f'{interaction.user.id} tried to use invalid command')
            return False
    return discord.app_commands.check(predicate)




#remember to have the db in the same location

async def clan_autocomplete(interaction: discord.Interaction, current: str):
    server_id = interaction.guild.id  
    c.execute('SELECT id, name FROM clans WHERE name LIKE ? AND server_id = ?', (f'%{current}%', server_id))
    clans = c.fetchall()
    
    return [
        app_commands.Choice(name=clan_name, value=clan_id)
        for clan_id, clan_name in clans[:25]
    ]

def chunk_list(lst, chunk_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

@bot.tree.command(name="audit_edit", description="Check or remove a clan from the database")
@app_commands.autocomplete(clan=clan_autocomplete)
@is_admin()
async def audit_edit(interaction: discord.Interaction, clan: str, action: str):
    if action not in ['check', 'remove']:
        await interaction.response.send_message("Invalid action. Use 'check' or 'remove'.", ephemeral=True)
        return

    c.execute('SELECT id, name FROM clans WHERE id = ?', (clan,))
    existing_clan = c.fetchone()

    if action == 'check':
        if existing_clan:
            await interaction.response.send_message(f"Clan '{existing_clan[1]}' is already in the database.", ephemeral=True)
            return
        await interaction.response.send_message(f"Clan with ID {clan} would be added (functionality not implemented).", ephemeral=True)

    elif action == 'remove':
        if not existing_clan:
            await interaction.response.send_message("Clan not found in the database.", ephemeral=True)
            return
        c.execute('DELETE FROM clans WHERE id = ?', (clan,))
        conn.commit()
        await interaction.response.send_message(f"Clan '{existing_clan[1]}' has been removed from the database.", ephemeral=True)
        print(f"Removed clan {existing_clan[1]} from the database.")


@bot.tree.command(name="audit", description="Audit the clans")
@app_commands.autocomplete(clan=clan_autocomplete)
async def audit(interaction: discord.Interaction, clan: str):
    await interaction.response.defer()

    c.execute('SELECT name, role_id FROM clans WHERE id = ?', (clan,))
    selected_clan = c.fetchone()

    if not selected_clan:
        await interaction.followup.send("Choose a different clan, dickhead")
        return

    bungie_members = get_clan_members(clan)
    if bungie_members:
        bungie_member_count = len(bungie_members)
        bungie_response = f"Bungie: {bungie_member_count} in '{selected_clan[0]}'."
    else:
        bungie_response = "Error getting Bungie members."

    role = discord.utils.get(interaction.guild.roles, id=selected_clan[1])
    if role:
        discord_members_with_role = [member for member in interaction.guild.members if role in member.roles]
        discord_member_count = len(discord_members_with_role)
        discord_response = f"Discord: {discord_member_count} in '{role.name}'."
    else:
        discord_response = "Error finding Discord role."

    bungie_member_names = {format_bungie_display_name(member) for member in bungie_members}
    discord_member_names = {member.display_name for member in discord_members_with_role}

    only_in_discord = discord_member_names - bungie_member_names
    only_in_bungie = bungie_member_names - discord_member_names

    embed = discord.Embed(
        title="Clan and Discord Member Count",
        description=f"{bungie_response}\n{discord_response}",
        color=discord.Color.dark_purple()
    )

    for chunk in chunk_list(sorted(only_in_bungie), 50):
        embed.add_field(name="Only in Bungie", value=", ".join(chunk), inline=False)
    
    for chunk in chunk_list(sorted(only_in_discord), 50):
        embed.add_field(name="Only in Discord", value=", ".join(chunk), inline=False)

    await interaction.followup.send(embed=embed)
    print("Audit done")




@bot.tree.command(name="randoe", description="Random message")
async def randoe(interaction: discord.Interaction):
    await interaction.response.defer()  
    channel = interaction.channel
    messages = [message async for message in channel.history(limit=1000)] 
    if messages:
        random_msg = random.choice(messages)
        await interaction.followup.send(f"{random_msg.author.display_name}: {random_msg.content}")
    else:
        await interaction.followup.send("No messages found in this channel.")
    return



@bot.event
async def on_message(message):
    if message.content.startswith('.nuinall'):
        async with message.channel.typing():
            final_report = ""
            for clan in clans:
                
                selected_clan = clan
                
                bungie_members = get_clan_members(clan["id"])
                if bungie_members:
                    bungie_member_count = len(bungie_members)
                    bungie_response = f"Bungie: '{selected_clan['name']}' Members {bungie_member_count}"
                else:
                    bungie_response = f"thinking..."   
                role = discord.utils.get(message.guild.roles, id=selected_clan["role_id"])
                if role:
                    discord_members_with_role = [member for member in message.guild.members if role in member.roles]
                    discord_member_count = len(discord_members_with_role)
                    discord_response = f"Discord: '{role.name}' Members {discord_member_count}"
                else:
                    discord_response = f"thinking..."
                if bungie_members:
                    bungie_member_names = {format_bungie_display_name(member) for member in bungie_members}
                else:
                    bungie_member_names = set()
                discord_member_names = {member.display_name for member in discord_members_with_role}

                in_both = bungie_member_names.intersection(discord_member_names)
                only_in_discord = discord_member_names - bungie_member_names
                only_in_bungie = bungie_member_names - discord_member_names

                
                clan_report = (f"**{selected_clan['name']}**\n"
                                f"{discord_response}\n"
                                f"{bungie_response}\n\n")


                final_report += clan_report

            
            embed = discord.Embed(
                title="Total member count",
                description=final_report,
                color=discord.Color.dark_purple() 
            )

            await message.channel.send(embed=embed)
            print(f'.nuinall done')
    await bot.process_commands(message)

    if any(temp_channel.id == message.channel.id for temp_channel in temp_channels.values()):
        log_message(message.channel, message.author, message.content)

    await bot.process_commands(message)

headers = {
    'X-API-Key': BUNGIE_API_KEY
}

def get_forum_post_details(post_id):
    url = f'https://www.bungie.net/Platform/Forum/GetPostAndParent/{post_id}/?showbanned=True'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json().get('Response', {})
        post = data.get('results', [{}])[0]
        author_map = {author["membershipId"]: author for author in data.get('authors', [])}
        author_data = author_map.get(post.get('authorMembershipId'), {})
        author_name = f"{author_data.get('displayName', 'Unknown')}#{author_data.get('cachedBungieGlobalDisplayNameCode', '0000')}"
        author_picture_url = f"https://www.bungie.net{author_data.get('profilePicturePath', '/img/profile/avatars/default_avatar.gif')}"
        
        details = {
            "author_name": author_name,
            "profile_picture": author_picture_url,
            "post_title": post.get('subject', 'No title'),
            "upvotes": post.get('upvotes', 0),
            "downvotes": post.get('downvotes', 0),
            "rating": post.get('ratingScore', 0),
            "is_on_first_page": "True" if int(post.get('popularity', 0)) > 0 else "False",
            "post_url": f"https://www.bungie.net/en/Forums/Post/{post_id}"
        }
        return details
    else:
        return f"Shit! Couldn't fetch post data (Status Code: {response.status_code})"


@bot.tree.command(name="postratings", description="Get upvotes and downvotes for a forum post")
async def post_ratings(interaction: discord.Interaction, post_id: str):
    details = get_forum_post_details(post_id)
    #if too many aare going at once then this breaks. idk how to fix
    if isinstance(details, dict):
        embed = discord.Embed(
            title=details['post_title'],
            url=details['post_url'],
            color=discord.Color.purple()
        )
        embed.set_author(name=details['author_name'], icon_url=details['profile_picture'])
        embed.add_field(name="Upvotes", value=str(details['upvotes']), inline=True)
        embed.add_field(name="Downvotes", value=str(details['downvotes']), inline=True)
        embed.add_field(name="Rating", value=str(details['rating']), inline=True)
        embed.add_field(name="On First Page?", value=details['is_on_first_page'], inline=True)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(details)
        return

    server_id = interaction.guild.id

#    await cancel_existing_task(server_id)

    current_upvotes, current_downvotes, current_comments, original_poster, creation_date = get_post_details(post_id)
    discord_user_id = str(interaction.user.id)
    
    if current_upvotes is not None:
        logging.info(f"Inserting initial data for post ID {post_id} by user {interaction.user.name}.")
        c.execute("INSERT OR IGNORE INTO post_ratings (post_id, upvotes, downvotes, comments, original_poster, discord_user_id, creation_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (post_id, current_upvotes, current_downvotes, current_comments, original_poster, discord_user_id, creation_date))
        conn.commit()
        
        channel = interaction.channel
        monitoring_task = bot.loop.create_task(monitor_post_details(post_id, channel))
        monitoring_tasks[server_id] = monitoring_task
        
        print(f"Started monitoring new post ID {post_id} for server {server_id}.\nMonitoring executed by {interaction.user.name}.")
    else:
        print(f"Failed to retrieve initial post details to start monitoring of {post_id}")




@bot.tree.command(name="audit_add", description="Add a new clan to the database")
@is_admin()
async def audit_add(interaction: discord.Interaction, clan_id: str, name: str, role: discord.Role):
    try:
        valid_clan = await validate_clan_id(clan_id)
        
        if not valid_clan:
            await interaction.response.send_message(f"Your {clan_id} does not exist on Bungie.net, or you have fewer than 4 members", ephemeral=True)
            return

        role_id = role.id
        server_id = interaction.guild.id

        c.execute('INSERT INTO clans (id, name, role_id, server_id) VALUES (?, ?, ?, ?)', (clan_id, name, role_id, server_id))
        conn.commit()

        await interaction.response.send_message(f"Clan '{name}' with ID {clan_id}, role ID {role_id}, added successfully for this server.", ephemeral=True)
        print(f"Added clan {name} to the database for server {server_id}.")

    except sqlite3.IntegrityError:
        await interaction.response.send_message("A clan with that ID already exists in the database.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def validate_clan_id(clan_id: str):
    try:
        endpoint = f'/GroupV2/{clan_id}/'
        url = BASE_URL + endpoint
        response = requests.get(url, headers={'X-API-Key': API_KEY})

        if response.status_code == 200:
            data = response.json()
            if data.get('Response', {}).get('totalResults', 0) < 4:
                return True
        else:
            print(f"Failed to validate clan id {clan_id}: Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    return False


@bot.tree.command(name="clessaudit", description="Audit clanless members")
async def clessaudit(interaction: discord.Interaction):
    await interaction.response.defer()
    
    # Decide which list to use based on the guild ID
    if interaction.guild.id == D_SERVER_ID:
        clan_list = Dclanlesss
        check_extra_role = False
    elif interaction.guild.id == L_SERVER_ID:
        clan_list = Lclanlesss
        check_extra_role = True
    else:
        await interaction.followup.send("This command cannot be used in this server.")
        return
    
    final_report = ""
    for clan in clan_list:
        selected_clan = clan

        bungie_members = get_clan_members(clan["id"])
        if bungie_members:
            bungie_member_count = len(bungie_members)
            bungie_response = f"Bungie: '{selected_clan['name']}' Members {bungie_member_count}"
        else:
            bungie_response = f"thinking..."   
        
        role = discord.utils.get(interaction.guild.roles, id=selected_clan["role_id"])
        if role:
            discord_members_with_role = [member for member in interaction.guild.members if role in member.roles]
            if check_extra_role and "other_role" in selected_clan:
                extra_role = discord.utils.get(interaction.guild.roles, id=selected_clan["other_role"])
                if extra_role:
                    # Exclude members with the other role from "stuck" members
                    discord_members_with_role = [member for member in discord_members_with_role if extra_role not in member.roles]
            discord_member_count = len(discord_members_with_role)
            discord_response = f"Discord: '{role.name}' Members {discord_member_count}"
        else:
            discord_response = f"thinking..."

        if bungie_members:
            bungie_member_names = {format_bungie_display_name(member) for member in bungie_members}
        else:
            bungie_member_names = set()
        
        discord_member_names = {member.display_name for member in discord_members_with_role}

        in_both = bungie_member_names.intersection(discord_member_names)
        
        clan_report = (f"**{selected_clan['name']}**\n"
                       f"In clanless: {in_both}\n\n")

        final_report += clan_report

    embed = discord.Embed(
        title="Members stuck in Clanless",
        description=final_report,
        color=discord.Color.dark_purple() 
    )

    await interaction.followup.send(embed=embed)
    print(f'clessaudit done in {interaction.guild.id}')





@bot.tree.command(name="activitycheck", description="Check all members currently assigned a specified role and their last post time.")
async def activitycheck(interaction: discord.Interaction, role: discord.Role):
    guild = interaction.guild
    members_with_role = [member for member in guild.members if role in member.roles]

    for member in members_with_role:
        current_nick = member.nick if member.nick else member.name
        cursor.execute(
            'SELECT nickname FROM user_roles WHERE user_id = ? AND role_id = ?', 
            (member.id, role.id)
        )
        db_nick_result = cursor.fetchone()

        if db_nick_result is not None:
            db_nick = db_nick_result[0]
            if db_nick != current_nick:
                cursor.execute('''
                    UPDATE user_roles SET nickname = ? WHERE user_id = ? AND role_id = ?
                ''', (current_nick, member.id, role.id))
        
        cursor.execute('''
            INSERT INTO user_roles (user_id, nickname, role_id, assignment_count, last_post_time, has_role)
            VALUES (?, ?, ?, 0, NULL, 1)
            ON CONFLICT(user_id, role_id) DO UPDATE SET has_role = 1
        ''', (member.id, current_nick, role.id))

    conn.commit()

    cursor.execute('''
        SELECT nickname, last_post_time, assignment_count 
        FROM user_roles 
        WHERE role_id = ? AND has_role = 1
        ORDER BY last_post_time ASC
    ''', (role.id,))
    results = cursor.fetchall()

    if not results:
        await interaction.response.send_message(f"No current users found with the role: {role.name}")
        return

    embeds = create_paginated_embeds(role.name, results)
    await interaction.response.defer()

    message = await interaction.followup.send(embed=embeds[0])

    if message is not None:
        await paginate(interaction, message, embeds)
    else:
        await interaction.followup.send("Error: Could not send the initial message for pagination.")
        
def create_paginated_embeds(role_name, results):
    embeds = []
    now = datetime.now()
    current_time_display = now.strftime('%Y-%m-%d %H:%M:%S')
    items_per_page = 10

    for i in range(0, len(results), items_per_page):
        embed = discord.Embed(
            title=f"Users with the role **{role_name}**\nTime now: {current_time_display}",
            color=discord.Color.dark_purple()
        )
        for nickname, last_post_time, assignment_count in results[i:i + items_per_page]:
            if last_post_time:
                last_post_time = datetime.strptime(last_post_time, '%Y-%m-%d %H:%M:%S')
                duration = now - last_post_time
                days, seconds = divmod(duration.total_seconds(), 86400)
                hours, seconds = divmod(seconds, 3600)
                minutes = seconds // 60

                if days > 0:
                    duration_str = f"{int(days)} day(s) ago"
                elif hours > 0:
                    duration_str = f"{int(hours)} hour(s) ago"
                else:
                    duration_str = f"{int(minutes)} minute(s) ago"
            else:
                duration_str = 'Never'

            description = f"Last Post: {last_post_time.strftime('%Y-%m-%d %H:%M:%S') if last_post_time else 'Never'}\n{duration_str}"
            embed.add_field(name=nickname, value=description, inline=False)
        
        embeds.append(embed)
    return embeds



@bot.tree.command(name="roletimecount", description="Check how many times a user has been assigned a specific role.")
async def roletimecount(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    cursor.execute('SELECT assignment_count FROM user_roles WHERE user_id = ? AND role_id = ?', (member.id, role.id))
    result = cursor.fetchone()
    
    embed = discord.Embed(title="Role Assignment Count", color=discord.Color.purple())
    embed.add_field(name="User", value=member.display_name, inline=True)
    embed.add_field(name="Role", value=role.name, inline=True)

    if result is None:
        embed.add_field(name="Count", value="Never assigned", inline=False)
        embed.set_footer(text=f"{member.display_name} has never been assigned the role {role.name}.")
    else:
        assignment_count = result[0]
        embed.add_field(name="Count", value=f"{assignment_count} time(s)", inline=False)
        embed.set_footer(text=f"{member.display_name} has been assigned the role {role.name} {assignment_count} time(s).")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roletime", description="Find out how long a user has had a specific role.")
async def roletime(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    cursor.execute('''
        SELECT assignment_time 
        FROM role_assignment_log 
        WHERE user_id = ? AND role_id = ? 
        ORDER BY assignment_time DESC
        LIMIT 1
    ''', (member.id, role.id))
    result = cursor.fetchone()
    
    if result is None:
        await interaction.response.send_message(f"{member.display_name} does not appear to have been assigned the role {role.name}.")
        return

    assignment_time_str = result[0]
    assignment_time = datetime.strptime(assignment_time_str, '%Y-%m-%d %H:%M:%S')
    duration = datetime.now() - assignment_time
    days, seconds = divmod(duration.total_seconds(), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds // 60
    embed = discord.Embed(title=f"Role Duration for {member.display_name}", color=discord.Color.dark_purple())
    embed.add_field(name="Role", value=role.name, inline=True)
    embed.add_field(name="Duration", value=f"{int(days)} days, {int(hours)} hours, and {int(minutes)} minutes", inline=True)
    embed.set_footer(text=f"Time since: {assignment_time_str}")

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="afkcheck", description="members that havent posted in 1-21 days")
async def afkcheck(interaction: discord.Interaction, role: discord.Role, days: int = 21):
    if days < 1 or days > 21:
        await interaction.response.send_message("Please give a number between 1 and 21.")
        return

    cutoff_date = datetime.now() - timedelta(days=days)
    cutoff_date_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        SELECT nickname, last_post_time FROM user_roles
        WHERE role_id = ? AND has_role = 1
        AND (last_post_time IS NULL OR last_post_time < ?)
    ''', (role.id, cutoff_date_str))
    
    results = cursor.fetchall()
    
    if not results:
        await interaction.response.send_message(f"all members in **{role.name}** have posted within the last {days} days.")
        return

    embeds = create_inactive_embeds(role.name, results)
    await interaction.response.send_message(embed=embeds[0])

    for embed in embeds[1:]:
        await interaction.followup.send(embed=embed)



def create_inactive_embeds(role_name, results):
    embeds = []
    now = datetime.now()
    current_time_display = now.strftime('%Y-%m-%d %H:%M:%S')

    embed = discord.Embed(
        title=f"Members who haven't posted in: **{role_name}**\nTime now: {current_time_display}",
        color=discord.Color.dark_purple()
    )

    for index, (nickname, last_post_time) in enumerate(results):
        if index > 0 and index % 25 == 0:
            embeds.append(embed)
            embed = discord.Embed(
                title=f"Members who haven't posted in: **{role_name}** (cont.)",
                color=discord.Color.dark_purple()
            )

        if last_post_time:
            # doing the "ago" part
            last_dt = datetime.strptime(last_post_time, '%Y-%m-%d %H:%M:%S')
            delta = now - last_dt
            total_seconds = int(delta.total_seconds())

            d, rem = divmod(total_seconds, 86400)
            h, rem = divmod(rem, 3600)
            m, _ = divmod(rem, 60)

            if d > 0:
                duration_str = f"{d} day(s) ago"
            elif h > 0:
                duration_str = f"{h} hour(s) ago"
            else:
                duration_str = f"{m} minute(s) ago"
            description = f"Last Post: {last_dt.strftime('%Y-%m-%d %H:%M:%S')}\n{duration_str}"
        else:
            description = "Last Post: Never"

        embed.add_field(name=nickname, value=description, inline=False)

    embeds.append(embed)
    return embeds


@bot.tree.command(name="showtime", description="Convert a time to a relative time with timezone GMT support.")
async def showtime(interaction: discord.Interaction, timezone: str, time: str, date: str = None):
    offset_timezones = {
        # i wanna kms
        'GMT+0': 'Etc/GMT',
        'GMT+1': 'Etc/GMT+1',
        'GMT+2': 'Etc/GMT+2',
        'GMT+3': 'Etc/GMT+3',
        'GMT+4': 'Etc/GMT+4',
        'GMT+5': 'Etc/GMT+5',
        'GMT+6': 'Etc/GMT+6',
        'GMT+7': 'Etc/GMT+7',
        'GMT+8': 'Etc/GMT+8',
        'GMT+9': 'Etc/GMT+9',
        'GMT+10': 'Etc/GMT+10',
        'GMT+11': 'Etc/GMT+11',
        'GMT+12': 'Etc/GMT+12',
        'GMT-1': 'Etc/GMT-1',
        'GMT-2': 'Etc/GMT-2',
        'GMT-3': 'Etc/GMT-3',
        'GMT-4': 'Etc/GMT-4',
        'GMT-5': 'Etc/GMT-5',
        'GMT-6': 'Etc/GMT-6',
        'GMT-7': 'Etc/GMT-7',
        'GMT-8': 'Etc/GMT-8',
        'GMT-9': 'Etc/GMT-9',
        'GMT-10': 'Etc/GMT-10',
        'GMT-11': 'Etc/GMT-11',
        'GMT-12': 'Etc/GMT-12',
        # US Timezones
        'EST': 'US/Eastern',
        'CST': 'US/Central',
        'MST': 'US/Mountain',
        'PST': 'US/Pacific',
        # Europe Timezones
        'London': 'Etc/GMT',
        'Berlin': 'Etc/GMT-1',
        'Paris': 'Etc/GMT-1',
        'Moscow': 'Etc/GMT-3',
        'CEST': 'Ect/GMT+1',
        'NZST': 'Etc/GMT+12',
        # Australia
        'AEST': 'Australia/Sydney',
        'ACST': 'Australia/Adelaide',
        'AWST': 'Australia/Perth',
        'NZDT': 'Etc/GMT+13',
        'HKT': 'Asia/Hong_Kong',
        'JST': 'Asia/Tokyo',
        'NST': 'America/St_Johns',
    }
    
    timezone = offset_timezones.get(timezone, timezone)
    time_formats = ["%I:%M %p", "%H:%M:%S"]
    datetime_formats = ["%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M:%S"]
    
    if date is None:
        current_date = datetime.now().strftime("%Y-%m-%d")
        show_only_time = True
    else:
        current_date = date
        show_only_time = False
    try:
        timezone_obj = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        await interaction.response.send_message(f"Unknown timezone: {timezone}", ephemeral=True)
        return

    success = False
    for time_format in time_formats:
        for datetime_format in datetime_formats:
            try:
                date_time_str = f"{current_date} {time}"
                date_time_obj = datetime.strptime(date_time_str, datetime_format)
                
                local_dt = timezone_obj.localize(date_time_obj)
                


                timestamp = int(local_dt.timestamp())
                
                if show_only_time:
                    discord_timestamp = f"<t:{timestamp}:t>"
                else:
                    discord_timestamp = f"<t:{timestamp}:F>"
                
                await interaction.response.send_message(
                    f"The timestamp for `{date_time_str} in {timezone}` is {discord_timestamp} `{discord_timestamp}`"
                )
                success = True
                break
            except ValueError:
                continue
        if success:
            break

    if not success:
        await interaction.response.send_message(
            "Error parsing date and/or time. Please use appropriate formats like '5:00 PM' for time or 'YYYY-MM-DD 5:00 PM' if a date is specified.",
            ephemeral=True
        )



@bot.tree.command(name="random_activity", description="Get a random raid or dungeon")
@app_commands.choices(activity=[
    app_commands.Choice(name="Raid", value="raids"),
    app_commands.Choice(name="Dungeon", value="dungeons"),
])
async def random_activity(interaction: discord.Interaction, activity: app_commands.Choice[str]):
    if activity.value == "raids":
        choice = random.choice(raids)
    elif activity.value == "dungeons":
        choice = random.choice(dungeons)
    else:
        choice = "Unknown option"

    await interaction.response.send_message(f'Random {activity.name}: {choice}')

# why does this work but the other one doesnt
def split_list2(input_list, size):
    """Splits a list into chunks of a specified size."""
    return [input_list[i:i + size] for i in range(0, len(input_list), size)]

# please work
async def paginate(interaction, message, embeds):
    """Handles pagination through reaction navigation."""
    if len(embeds) <= 1:
        return

    current_page = 0
    await message.add_reaction('◀️')
    await message.add_reaction('▶️')

    def check(reaction, user):
        return (
            user == interaction.user and
            str(reaction.emoji) in ['◀️', '▶️'] and
            reaction.message.id == message.id
        )

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == '▶️':
                if current_page < len(embeds) - 1:
                    current_page += 1
                    await message.edit(embed=embeds[current_page])

            elif str(reaction.emoji) == '◀️':
                if current_page > 0:
                    current_page -= 1
                    await message.edit(embed=embeds[current_page])

            await message.remove_reaction(reaction, user)
        
        except asyncio.TimeoutError:
            break

# `monrole` command
@bot.tree.command(name="monrole", description="List members with two specific roles")
async def monrole(interaction: discord.Interaction, role1: discord.Role, role2: discord.Role):
    await interaction.response.defer()
    members_with_roles = [member for member in role1.guild.members if role1 in member.roles and role2 in member.roles]

    total_members = len(members_with_roles)

    if total_members == 0:
        await interaction.followup.send("There is no one with both of these roles.")
        return


    embeds = generate_paginated_embeds2(members_with_roles, role1, role2)
    message = await interaction.followup.send(embed=embeds[0])
    await paginate(interaction, message, embeds)

# `onrole` command
@bot.tree.command(name="onrole", description="List members with a specific role")
async def onrole(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    members_with_role = [member for member in role.guild.members if role in member.roles]

    total_members = len(members_with_role)

    if total_members == 0:
        await interaction.followup.send("There is no one with this role.")
        return


    embeds = generate_paginated_embeds2(members_with_role, role, None)
    message = await interaction.followup.send(embed=embeds[0])
    await paginate(interaction, message, embeds)

def generate_paginated_embeds2(members, role1, role2=None):
    """Generates paginated embed messages for members with specified roles."""
    parts = split_list2(members, 20)
    embeds = []
    total_members = len(members)
    title_context = f"{role1.name} & {role2.name}" if role2 else role1.name
    for index, part in enumerate(parts):
        member_strings = [f"{member.nick or 'None'} ({member.name})" for member in part]
        description = '\n'.join(member_strings) or 'None'
        
        embed = discord.Embed(
            title=f"Members with {title_context} Role: {total_members}  (Page {index+1}/{len(parts)})",
            description=description,
            color=discord.Color.dark_purple()
        )
        embeds.append(embed)
    
    return embeds



@bot.tree.command(name="online_check", description="Check for online members")
async def online_check(interaction: discord.Interaction, role: discord.Role):
    online_members = [
        member.display_name for member in role.members
        if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]
    ]
    total_members = len(online_members)

    if not online_members:
        await interaction.response.send_message(
            f"There are no online members with the role {role.name}.", ephemeral=True
        )
        return

    await interaction.response.defer()

    embeds = generate_paginated_embeds3(online_members, role.name, "Online", total_members)
    message = await interaction.followup.send(embed=embeds[0])

    await paginate(interaction, message, embeds)

@bot.tree.command(name="offline_check", description="Check for offline members")
async def offline_check(interaction: discord.Interaction, role: discord.Role):
    offline_members = [
        member.display_name for member in role.members if member.status == discord.Status.offline
    ]
    total_members = len(offline_members)

    if not offline_members:
        await interaction.response.send_message(
            f"There are no offline members with the role {role.name}.", ephemeral=True
        )
        return

    await interaction.response.defer()

    embeds = generate_paginated_embeds3(offline_members, role.name, "Offline", total_members)
    message = await interaction.followup.send(embed=embeds[0])

    await paginate(interaction, message, embeds)

def generate_paginated_embeds(members, role1, role2, total_members):
    """Generates paginated embed messages for members with specific roles."""
    parts = split_list(members, 20)  # more than 20 some times breaks
    embeds = []

    for index, part in enumerate(parts):
        #send help plz
        member_strings = [f"{member.name} (Nickname: {member.nick or 'None'})" for member in part]
        description = '\n'.join(member_strings) or 'None'
        
        embed = discord.Embed(
            title=f"Members with '{role1.name}' & '{role2.name}' Roles (Page {index+1}/{len(parts)})",
            description=description,
            color=discord.Color.dark_purple()
        )
        embeds.append(embed)
    
    return embeds
    

def generate_paginated_embeds3(members, role_name, status, total_members):
    parts = list(split_list(members, max_length=20))
    embeds = []

    for index, part in enumerate(parts):
        desc = '\n'.join(part) or 'None'
        
        embed = discord.Embed(
            title=f"{status} members with {role_name}: {total_members} (Page {index+1}/{len(parts)})",
            description=desc,
            color=discord.Color.dark_purple()
        )
        embeds.append(embed)
    
    return embeds
#dont delete this. shit breaks and i dont know why

def split_list(lst, max_length):
    """Helper function to split a list into chunks."""
    current_chunk = []
    current_length = 0

    for item in lst:
        if current_length + 1 <= max_length:
            current_chunk.append(item)
            current_length += 1
        else:
            yield current_chunk
            current_chunk = [item]
            current_length = 1

    if current_chunk:
        yield current_chunk



#whos playing command

@bot.tree.command(name="whosplaying", description="Show users playing a specified game")
async def whosplaying(interaction: discord.Interaction, game: str):
    guild = interaction.guild
    members_playing_game = []

    for member in guild.members:
        if member.activities:
            for activity in member.activities:
                if activity.type == discord.ActivityType.playing and activity.name.lower() == game.lower():
                    members_playing_game.append(member)

    if members_playing_game:
        embed = discord.Embed(
            title=f"Users playing {game}",
            color=discord.Color.green()
        )
        response = "\n".join(f"{member.display_name}" for member in members_playing_game)
        embed.add_field(name="Players:", value=response, inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"No users are currently playing {game}", ephemeral=True)


#color text command

foreground_colors = {
    "grey": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "bright grey": "90",
    "bright red": "91",
    "bright green": "92",
    "bright yellow": "93",
    "bright blue": "94",
    "bright magenta": "95",
    "bright cyan": "96",
    "bright white": "97"
}

background_colors = {
    "grey": "40",
    "red": "41",
    "green": "42",
    "yellow": "43",
    "blue": "44",
    "magenta": "45",
    "cyan": "46",
    "white": "47",
    "bright grey": "100",
    "bright red": "101",
    "bright green": "102",
    "bright yellow": "103",
    "bright blue": "104",
    "bright magenta": "105",
    "bright cyan": "106",
    "bright white": "107"
}



@bot.tree.command(name="colortext", description="Create colored text with ANSI codes")
async def colortext(interaction: discord.Interaction, fg_color: str, bg_color: str, text: str):
    fg_code = foreground_colors.get(fg_color.lower())
    bg_code = background_colors.get(bg_color.lower())
    
    if not fg_code or not bg_code:
        await interaction.response.send_message(
            "Invalid color! Available colors: grey, red, green, yellow, blue, magenta, cyan, white, " +
            "bright grey, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, bright white",
            ephemeral=True
        )
        return
    
    formatted_text = f"```ansi\n\x1b[0;{fg_code};{bg_code}m{text}\x1b[0m\n```"
    outer_code_block = f"```\n{formatted_text}\n```"
    await interaction.response.send_message(outer_code_block)


# the vc bot part lol i hope this doesnt break

temp_channels = {}

@bot.event
async def on_voice_state_update(member, before, after):
    guild = bot.get_guild(GUILD_ID)
    if after.channel and after.channel.id == WATCH_CHANNEL_ID:
        category = after.channel.category
        original_channel = after.channel
        overwrites = original_channel.overwrites
        overwrites[member] = discord.PermissionOverwrite(manage_channels=True)
        temp_channel = await guild.create_voice_channel(
            name=f"{member.nick or member.name}'s VC",
            category=category,
            overwrites=overwrites
        )
        temp_channels[temp_channel.id] = temp_channel
        await member.move_to(temp_channel)
    if before.channel and before.channel.id in temp_channels:
        temp_channel = temp_channels[before.channel.id]
        if len(temp_channel.members) == 0:
            await temp_channel.delete()
            del temp_channels[before.channel.id]

def log_message(channel, author, content):
    filename = f"{channel.name.replace(' ', '_')}_log.txt"

    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"[{channel.name}] {author}: {content}\n")

    print(f"Logged message to {filename}")




bot.run('botkey')




