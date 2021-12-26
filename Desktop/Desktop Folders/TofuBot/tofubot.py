import os
import random

import discord
from dotenv import load_dotenv
from discord.ext import commands

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(BASEDIR + '/.env.txt')
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

bot = commands.Bot(command_prefix='.')

bday_role = "1"
member_roles = ['ot9', 'nayeon', 'jeongyeon', 'momo', 'sana', 'jihyo', 'mina', 'dahyun', 'chaeyoung', 'tzuyu',
                'nayeon.', 'jeongyeon.', 'momo.', 'sana.', 'jihyo.', 'mina.', 'dahyun.', 'chaeyoung.', 'tzuyu.', 'vlive']

@bot.event
async def on_ready():
    print('{} has connected to Discord!'.format(bot.user.name))
    await bot.change_presence(activity=discord.Game(name='more output changes.'))

def embed_msg(command, role, name, icon_url, member, member_roles):
    if command == 'add':
        embed = discord.Embed(description='**Added {}**\nCurrent User\'s roles are: {}' .format(role, ', '.join(get_user_roles(member, member_roles))), colour=0x9fa8da)
        embed.set_author(name=name, icon_url=icon_url)
        return embed
    return None

# Checks if the user has vlive role or not
# Returns false - don't add vlive role, true otherwise
def check_vlive(member, vlive):
    if discord.utils.find(lambda r: r == vlive, member.roles): 
        return False
    return True

# Gets the Role object of the input role
def get_role(member_roles, inputrole):
    return discord.utils.find(lambda r: r == inputrole, member_roles)

# Gets the user's roles and stores them in a list
def get_user_roles(member, member_roles):
    get_member_roles = []
    for curr_role in member.roles:
        checkRole = get_role(member_roles, curr_role.name.lower())
        if checkRole != None and checkRole != 'vlive':
            get_member_roles.insert(0, checkRole)

    return get_member_roles

def get_birthday_role(member, member_roles):
    role_id = None
    for role in member.roles:
        if role.id == bday_role:
            role_id = bday_role

    return role_id

# Capitalize's the role, converts ot9 to all caps
def role_capitalize(role):
    if role == 'ot9':
        return 'OT9'
    return role.capitalize()

# Converts a primary role to a secondary role
def role_to_secondary(role):
    s = '.'
    secondary = ''.join((role, s))
    return secondary.capitalize()

# Checks if the role is Primary or Secondary
# Returns True if Primary, False if Secondary
def check_role(role):
    if role[-1] != '.':
        return True
    return False

@bot.event
async def set_role(member, inputrole):
    await member.add_roles(discord.utils.get(member.guild.roles, name = inputrole))

@bot.event
async def del_role(member, inputrole):
    await member.remove_roles(discord.utils.get(member.guild.roles, name = inputrole))

@bot.command(name='add', help='Usage: .add <Role>', pass_context=True)
async def add_role(ctx, role):
    inputrole = role.lower()
    member = ctx.message.author

    # check role is a member role
    checkRole = get_role(member_roles, inputrole)

    # adds 'vlive' role if they don't have the role
    if inputrole == 'vlive':
        if check_vlive(member, 'vlive'):
            await set_role(member, inputrole)
            await ctx.send('Added the vlive role')
        return

    # return if invalid input
    if checkRole is None:
        if inputrole == 'once':
            await ctx.send('This role is only available for server boosters!')
        elif inputrole == 'JYP':
            await ctx.send('This role is only available on JYPs birthday')
        else:
            await ctx.send('Invalid role!')
        return

    # check users roles (max 3)
    get_member_roles = get_user_roles(member, member_roles)
    birthday_role = get_birthday_role(member, member_roles)

    if len(get_member_roles) == 0 and birthday_role == None:
        if inputrole == "nayeon":
            await member.add_roles(discord.utils.get(member.guild.roles, id = bday_role))
            await ctx.send('Added Nayeon')
            return
        await set_role(member, role_capitalize(inputrole))
        name = ctx.message.author.name
        icon_url = ctx.message.author.avatar_url
        await ctx.send(embed=embed_msg('add', role_capitalize(inputrole), name, icon_url, member, member_roles))
        return

    # if birthday_role == bday_role:
    #     if len(get_member_roles) >= 2:
    #         await ctx.send('User already has 3 roles!')
    #         return
    #     if len(get_member_roles) == 0 or len(get_member_roles) == 1: # add as secondary
    #         if inputrole == "nayeon":
    #             await ctx.send('User already has this role!')
    #             return
    #         await set_role(member, role_to_secondary(inputrole))
    #         name = ctx.message.author.name
    #         icon_url = ctx.message.author.avatar_url
    #         await ctx.send(embed=embed_msg('add', role_to_secondary(inputrole), name, icon_url, member, member_roles))
    #         #await ctx.send('Added {}'.format(role_to_secondary(inputrole)))
    #         return

    # return if user has 3 or more bias roles
    if len(get_member_roles) >= 3:
        await ctx.send('User already has 3 roles!')
        return

    # case 1: no roles
    if len(get_member_roles) == 0:
        await set_role(member, role_capitalize(inputrole))
        await ctx.send('Added {}'.format(role_capitalize(inputrole)))
        return

    # if user has primary, try to add secondary only if role is not same member as primary
    #success = False
    first = get_member_roles[0]
    # case 2: 1 role (1 primary or 1 secondary)
    if len(get_member_roles) == 1:
        if check_role(first): # 1 primary
            if first == inputrole:
                await ctx.send('User already has this role!')
                return
            if inputrole == 'ot9':
                await ctx.send('Cannot add OT9 as a secondary role!')
                return
            await set_role(member, role_to_secondary(inputrole))
            name = ctx.message.author.name
            icon_url = ctx.message.author.avatar_url
            await ctx.send(embed=embed_msg('add', role_to_secondary(inputrole), name, icon_url, member, member_roles))
            #success = True
        else: # 1 secondary
            if first.replace('.', '') == inputrole:
                await ctx.send('User already has this role!')
                return
            await set_role(member, role_capitalize(inputrole))
            name = ctx.message.author.name
            icon_url = ctx.message.author.avatar_url
            await ctx.send(embed=embed_msg('add', role_capitalize(inputrole), name, icon_url, member, member_roles))
            #success = True

        # if success == True:
        #     await ctx.send('Added role')
        return

    # case 2: 2 roles (1 primary 1 secondary or 2 secondaries)
    second = get_member_roles[1]
    if check_role(first) and not check_role(second):
        if first == inputrole or second.replace('.', '') == inputrole:
            await ctx.send('User already has this role!')
            return
        elif inputrole == 'ot9':
            await ctx.send('Cannot add OT9 as a secondary role!')
            return
        await set_role(member, role_to_secondary(inputrole))
        success = True
    elif not check_role(first) and not check_role(second):
        if first.replace('.', '') == inputrole or second.replace('.', '') == inputrole:
            await ctx.send('User already has this role!')
            return
        await set_role(member, role_capitalize(inputrole))
        success = True

    if success == True:
        await ctx.send('Added role')

@bot.command(name='remove', help='Usage: .remove <Role>', pass_context=True)
async def remove_role(ctx, role):
    inputrole = role.lower()
    member = ctx.message.author

    # check role is a member role 
    checkRole = get_role(member_roles, inputrole)

    if inputrole == 'vlive':
        if check_vlive(member, 'vlive'):
            await del_role(member, inputrole)
            await ctx.send('Removed the vlive role')
        return

    if checkRole is None:
        await ctx.send('Invalid Role!')
        return

    get_member_roles = get_user_roles(member, member_roles)
    birthday_role = get_birthday_role(member, member_roles)

    if len(get_member_roles) == 0 and birthday_role == None:
        await ctx.send('User does not have a role!')
        return

    if birthday_role == bday_role and inputrole == "nayeon":
        await member.remove_roles(discord.utils.get(member.guild.roles, id = bday_role))
        await ctx.send('Removed role')
        return

    success = False
    first = get_member_roles[0]
    if len(get_member_roles) == 1:
        if check_role(first): # 1 primary
            if first == inputrole: # remove primary
                await del_role(member, role_capitalize(inputrole))
                success = True
        else: # 1 secondary
            if first.replace('.', '') == inputrole:
                await del_role(member, role_to_secondary(inputrole))
                success = True

        if success == True:
            await ctx.send('Removed role')
        elif success == False:
            await ctx.send('User does not have this role!')
        return
    
    second = get_member_roles[1]
    if len(get_member_roles) == 2:
        if check_role(first) and not check_role(second): # 1 primary & 1 secondary
            if first == inputrole: # remove primary
                await del_role(member, role_capitalize(inputrole))
                success = True
            elif second.replace('.', '') == inputrole: # remove secondary
                await del_role(member, role_to_secondary(inputrole))
                success = True

        elif not check_role(first) and not check_role(second): # 2 secondary
            if first.replace('.', '') == inputrole:
                await del_role(member, role_to_secondary(inputrole))
                success = True
            elif second.replace('.', '') == inputrole:
                await del_role(member, role_to_secondary(inputrole))
                success = True

        if success == True:
            await ctx.send('Removed role')
        elif success == False:
            await ctx.send('User does not have this role!')
        return

    third = get_member_roles[2]
    if check_role(first) and not check_role(second) and not check_role(third): # 1 primary & 2 secondary
        if first == inputrole: # remove primary
            await del_role(member, role_capitalize(inputrole))
            success = True
        elif second.replace('.', '') == inputrole: # remove secondary
            await del_role(member, role_to_secondary(inputrole))
            success = True
        elif third.replace('.', '') == inputrole: # remove secondary
            await del_role(member, role_to_secondary(inputrole))
            success = True

    if success == True:
        await ctx.send('Removed role')
    elif success == False:
        await ctx.send('User does not have this role!')

@bot.command(name='clear', help='Usage: .clear', pass_context=True)
async def roles_clear(ctx):
    member = ctx.message.author
    member_roles = ['ot9', 'nayeon', 'jeongyeon', 'momo', 'sana', 'jihyo', 'mina', 'dahyun', 'chaeyoung', 'tzuyu',
                    'nayeon.', 'jeongyeon.', 'momo.', 'sana.', 'jihyo.', 'mina.', 'dahyun.', 'chaeyoung.', 'tzuyu.', 'vlive']

    get_member_roles = get_user_roles(member, member_roles)

    if len(get_member_roles) == 0:
        await ctx.send('User has no roles!')
        return

    for role in get_member_roles:
        await del_role(member, role_capitalize(role))
    
    await ctx.send('All roles cleared!')

bot.run(TOKEN)