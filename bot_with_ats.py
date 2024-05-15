import discord
from discord.ext import commands

# pain and suffering
# do not change 

#
intents = discord.Intents.all()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)
#

@client.event
async def on_ready():
    print(f'{client.user} is gay')



def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

@client.event
async def on_message(message):
    if message.content.startswith('!OnRole'):
        role_mentions = message.role_mentions
        if not role_mentions:
            await message.channel.send('Please mention a role.')
            return

        role = role_mentions[0]
        members_with_role = [member for member in message.guild.members if role in member.roles]
        total_members = len(members_with_role)
                    
        if total_members > 0:
                chunks = list(chunk_list(members_with_role, 30))
                
                for i, chunk in enumerate(chunks):
                    response = (
                        f"Page {i+1}/{len(chunks)}: Users with the '{role_mentions}' role (Total: {total_members}):\n"
                    )
                    for member in chunk:
                        response += f"{member.nick or 'No nickname'} ({member.name})\n"
                    await message.channel.send(response)
        else:
            await message.channel.send(f"No one has the '{role_mentions}' role")
    else:

        #idk why this breaks it but it does. dont do it again
        #await message.channel.send(f"I can't find '{role_mentions}'")
        print("done")


client.run('')
