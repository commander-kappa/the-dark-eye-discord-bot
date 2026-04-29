import os; from os import path
import json, io, asyncio
import discord as dc
import bot_util as bot
from bot_util import ERROR_MESSAGES_SILENT_REPLY_DEFAULT as ESR_DEFAULT
from bot_util import UNEXPECTED_ERROR_DEFAULT_TEXT as UE_DEFAULT_TEXT
import bot_exceptions as exc
import helper

#TODO: getCharFromCache function!

#INFO: functions to reduce code redundancy
async def check_user(client: dc.Client, user_id:str) -> bool:
    if not bot.validate_user_id(user_id, verbose=True):
        return False
    user = await client.fetch_user(int(user_id))
    if user:
        print(f"RESOLVED: User ID <{user_id}> is @{user.name} \'{user.display_name}\'")
        return True
    else:
        print(f'WARNING: User ID <{user_id}> could not be resolved!')
        return False

async def check_master_respond(interaction: dc.Interaction) -> bool:
    if not (bot.check_master(interaction.user.id)):
        await interaction.followup.send(bot.WARNING_NOT_A_MASTER, ephemeral=ESR_DEFAULT)
        return False
    else:
        return True

async def check_player_or_master_respond(interaction: dc.Interaction, player: dc.Member, silent_reply:bool = True) -> bool:
    if interaction.user.id == player.id:
        if not bot.check_player(player.id):
            await interaction.followup.send(bot.WARNING_NOT_A_PLAYER, ephemeral=ESR_DEFAULT)
            return False
    else:
        if not bot.check_master(interaction.user.id):
            await interaction.followup.send(bot.WARNING_NOT_A_MASTER, ephemeral=ESR_DEFAULT)
            return False
        if not bot.check_player(player.id):
            await interaction.followup.send(f"@{player.name} is not registered as in the ACTIVE_PLAYER file!", ephemeral=ESR_DEFAULT)
            return False
    
    return True

async def init_char_action(interaction: dc.Interaction, player: dc.Member, silent_reply:bool = True) -> bool:
    await interaction.response.defer(ephemeral=silent_reply)
    if not await check_player_or_master_respond(interaction, player, silent_reply): return False
    if player.id not in bot.PLAYER_CHARACTER_CACHE.keys(): 
        try:
            bot.cache_player_character(player.id)
        except exc.BotException as e:
            print(e); silent_reply = ESR_DEFAULT
            await interaction.followup.send('ERROR: Character caching failed. ' + e.message, ephemeral=ESR_DEFAULT)
            return False
        except Exception as e:
            print(e); silent_reply = ESR_DEFAULT
            await interaction.followup.send('UNEXPECTED ERROR: Character caching failed.', ephemeral=ESR_DEFAULT)
            return False
    
    return True

class MyClient(dc.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        try:
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        print("Checking Masters:")
        for user_id in bot.load_masters():
            user_id = user_id.replace('\n', '')
            await check_user(client, user_id)

        print("Caching Player Characters:") 
        for user_id in bot.load_players():
            user_id = user_id.replace('\n', '')
            try:
                print(f"CACHING: <{user_id}>")
                bot.cache_player_character(user_id)
                print(f"SUCCESS: {bot.PLAYER_CHARACTER_CACHE[user_id].info['name']}")
            except Exception as e:
                print(e)
            
        print('CLIENT READY!')

    async def on_message(self, msg):
        try:
            print(f"[{msg.guild.name}]#{msg.channel.name} @{msg.author.name}: {msg.content}")
        except:
            pass

intents = dc.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
tree = dc.app_commands.CommandTree(client)

@tree.command(name="list_masters", description="List all registered Gamemasters")
async def list_masters(
    interaction: dc.Interaction,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
  
    out = 'Registered Gamemasteres:\n'

    for user_id in bot.load_masters():
        user_id = user_id.replace('\n', '')
        user = None
        if await check_user(client, user_id):
            user = await client.fetch_user(int(user_id))
            out += f"- {user.name}\n"

    await interaction.followup.send(out, ephemeral=silent_reply)
    return

@tree.command(name="list_players", description="MASTER ONLY: List all registered Players")
async def list_players(
    interaction: dc.Interaction,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=True)
    if not await check_master_respond(interaction):
        return
    
    out = 'Registered Players:\n'

    for user_id in bot.load_players():
        user_id = user_id.replace('\n', '')
        user = None
        if await check_user(client, user_id):
            user = await client.fetch_user(int(user_id))
            out += f"- {user.name}\n"

    await interaction.followup.send(out, ephemeral=silent_reply)
    return

@tree.command(name="add_player", description="MASTER ONLY: Adds a Player to the Directory")
async def add_player(
    interaction: dc.Interaction,
    player: dc.Member,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
    if not await check_master_respond(interaction): return

    reply = f"Added Player <{player.id}> @{player.name}"    
    try:
        bot.add_player(player.id)
    except exc.BotException as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'ERROR: ' + e.message
    except exc.BotWarning as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'WARNING: ' + e.message
    except Exception as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = UE_DEFAULT_TEXT
    
    print(reply)
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

@tree.command(name="remove_player", description="MASTER ONLY: Removes a Player from the Directory")
async def remove_player(
    interaction: dc.Interaction,
    player: dc.Member,
    clear_directory: bool = False, #TODO implement clear directory?
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
 
    if not await check_master_respond(interaction): return

    
    reply = f"Removed Player <{player.id}> @{player.name}"    
    try:
        bot.remove_player(player.id, clear_directory)
    except exc.BotException as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'ERROR: ' + e.message
    except exc.BotWarning as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'WARNING: ' + e.message
    except Exception as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = UE_DEFAULT_TEXT

    print(reply)
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

@tree.command(name="upload_character", description="Upload a character.json")
async def upload_character(
    interaction: dc.Interaction,
    upload_file: dc.Attachment,
    player: dc.Member = None,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None: player = interaction.user
    if not await check_player_or_master_respond(interaction, player): return

    if not (bot.check_player(player.id)):
        await interaction.followup.send(bot.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
     
    try:
        bot.create_player_dir(player.id)
    except:
        await interaction.followup.send('ERROR: Could not create Player dir', ephemeral=silent_reply)
        return

    if not helper.validate_file_name(upload_file.filename, 'json'):
        await interaction.followup.send('ERROR: File must be .json', ephemeral=silent_reply)
        return

    if upload_file.size > bot.MAX_CHAR_FILE_SIZE['INT']:
        await interaction.followup.send('ERROR: File size exceeds ' + bot.MAX_CHAR_FILE_SIZE['STR'], ephemeral=silent_reply)
        return
    
    #TODO: export to seperate function for reusability?
    #TODO: Harder file validation?
    json_cache = {}
    try:
        f = await upload_file.read()
        json_cache = json.loads(f.decode('UTF-8'))
    except Exception as e:
        print(e)
        await interaction.followup.send('ERROR: File could not be converted into JSON object', ephemeral=silent_reply)
        return
    
    reply = f"Uploaded {upload_file.filename}"
    
    try:
        bot.add_character(
            player.id,
            upload_file.filename,
            json_cache
        )
    except exc.BotException:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'ERROR: ' + e.message
    except exc.BotWarning as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'WARNING: ' + e.message
    except Exception as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = UE_DEFAULT_TEXT
   
    print(reply)
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

@tree.command(name="list_characters", description="List all uploaded characters from a player")
async def list_characters(
    interaction: dc.Interaction,
    player: dc.Member = None,
    silent_reply: bool = True
): 
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None: player = interaction.user
    if not await check_player_or_master_respond(interaction, player): return
    
    try:
        reply = f"@{player.name}'s characters:"
        for char in bot.list_characters(player.id):
            if char != 'ACTIVE_CHAR':
                reply += f"\n- {char.split('.')[0]}"
    except exc.DirectoryNotFoundError as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'ERROR: ' + e.message
        bot.create_player_dir(player.id)
    except Exception as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = UE_DEFAULT_TEXT

    await interaction.followup.send(reply, ephemeral=silent_reply)
    return


@tree.command(name="select_character", description="Select a character to use commands on")
async def select_character(
    interaction: dc.Interaction,
    file_name: str,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)

    if not bot.check_player(interaction.user.id):
        await interaction.followup.send(bot.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return

    file_name = file_name.replace('.json', '')
    
    reply = f"Character {file_name} selected!"
    try:
        bot.change_character(interaction.user.id, file_name + '.json')
        bot.cache_player_character(interaction.user.id)
    except exc.CharacterNotFoundError as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = "ERROR: " + e.message
    except Exception as e:    
        print(e); silent_reply = ESR_DEFAULT
        reply = UE_DEFAULT_TEXT
    
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

@tree.command(name="remove_character", description="Remove character from your directory")
async def remove_character(
    interaction: dc.Interaction,
    file_name: str
):
    await interaction.response.defer(ephemeral=True)

    if not bot.check_player(interaction.user.id):
        await interaction.followup.send(bot.WARNING_NOT_A_PLAYER, ephemeral=True)
        return

    file_name = file_name.replace('.json', ''); file_name += '.json'
    
    reply = f"SUCCESS: Character {file_name} removed from your directory!"
    try:
        bot.remove_player_character(interaction.user.id, file_name)
    except exc.DirectoryNotFoundError as e:
        reply = "ERROR: " + e.message
        bot.create_player_dir(interaction.user.id)
    except FileNotFoundError as e:
        reply = f"ERROR: Character {file_name} does not exist in your directory"
    except Exception as e:
        print(e)
        reply = UE_DEFAULT_TEXT

    await interaction.followup.send(reply, ephemeral=True)
    return

@tree.command(name="show_info", description="Shows info of the selected player character")
async def show_info(
    interaction: dc.Interaction,
    player: dc.Member = None,
    silent_reply: bool = True
):    
    if player is None: player = interaction.user
    if not await init_char_action(interaction, player, silent_reply): return
    
    char = bot.PLAYER_CHARACTER_CACHE[player.id]

    await interaction.followup.send(f"```{char.showInfo()}```", ephemeral=silent_reply)
    return

@tree.command(name="show_attributes", description="Shows attributes of the selected player character")
async def show_attributes(
    interaction: dc.Interaction,
    player: dc.Member = None,
    silent_reply: bool = True
):    
    if player is None: player = interaction.user
    if not await init_char_action(interaction, player, silent_reply): return
    
    char = bot.PLAYER_CHARACTER_CACHE[player.id]
    
    reply = f"Show talents of @{player.name}'s chararcter: {char.info['name']}\n" 
    reply += f"```{char.showAttributes()}```"
    
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

@tree.command(name="show_talents", description="Shows talents of the selected player character")
async def show_talents(
    interaction: dc.Interaction,
    id_1: int = 0,
    id_2: int = 58,
    player: dc.Member = None,
    silent_reply: bool = True
):
    if player is None: player = interaction.user
    if not await init_char_action(interaction, player, silent_reply): return

    char = bot.PLAYER_CHARACTER_CACHE[player.id]
    buffer = char.showTalente([id_1, id_2])

    try:
        inMemoryFile = io.BytesIO()
        writer = io.BufferedWriter(raw=inMemoryFile)

        writer.write(buffer.encode('utf-8'))
        
        writer.flush()
        inMemoryFile.seek(0)

        await interaction.followup.send(
            content = f"Show talents of @{player.name}'s chararcter: {char.info['name']}",
            file = dc.File(fp = inMemoryFile, filename='talents.txt'),
            ephemeral=silent_reply
            )
    
    except Exception as e:
        print(e)
        await interaction.followup.send("ERROR: Could not create Text file containing talents", ephemeral=silent_reply)
    finally:
        writer.close()
        inMemoryFile.close()

    return

@tree.command(name="roll_dice", description="Rolls times d size")
async def roll_dice(
    interaction: dc.Interaction,
    size: int,
    times: int,
    silent_reply: bool = False
):
    await interaction.response.defer(ephemeral=silent_reply)
    
    try:
        await interaction.followup.send(bot.dice_roll_string(times, size), ephemeral=silent_reply)
    except Exception as e:
        print(e)
        await interaction.followup.send("ERROR: Invalid Inputs", ephemeral=ESR_DEFAULT)    
    
    return

@tree.command(name="roll_3d20", description="Rolls 3d20")
async def roll_3d20(
    interaction: dc.Interaction,
    silent_reply: bool = False
):
    await interaction.response.send_message(bot.dice_roll_string(3, 20), ephemeral = silent_reply)


@tree.command(name="roll_attribute", description="Rolls on an attribute of a selected player character")
async def roll_attribute(
    interaction: dc.Interaction,
    id: str,
    mod: int = 0,
    player: dc.Member = None,
    silent_reply: bool = False
):
    if player is None: player = interaction.user
    if not await init_char_action(interaction, player, silent_reply): return
    
    char = bot.PLAYER_CHARACTER_CACHE[player.id]
    reply = f"Roll on Attribute [{id}] for {char.info['name']}:\n\n"

    try:
        reply += char.attributeValues[id].toStr(formatName = False)
        reply += char.doAttributeCheck(id, mod).toStr()
    #TODO: Raise invalid Attribute Exception in attributes.py
    except Exception as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = 'ERROR: Invalid Inputs'

    await interaction.followup.send(reply, ephemeral=silent_reply)        
    return

@tree.command(name="roll_talent", description="Rolls on a talent of a selected player character")
async def roll_talent(
    interaction: dc.Interaction,
    id: int,
    mod: int = 0,
    player: dc.Member = None,
    silent_reply: bool = False
):
    if player is None: player = interaction.user
    if not await init_char_action(interaction, player, silent_reply): return
     
    char = bot.PLAYER_CHARACTER_CACHE[player.id]
    reply = f"Roll on Talent [{id}] for {char.info['name']}:\n\n"

    
    try:
        reply += char.talentValues[id].toStr(formatName = False) + '\n'
        reply += char.doTalentCheck(id, mod).toStr()
    except Exception as e:
        print(e); silent_reply = ESR_DEFAULT
        reply = "ERROR: Invalid Inputs"

    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

def main() -> None:
    bot.setup_res()
    try:
        with open(path.join(bot.RES_PATH, 'TOKEN'), 'r') as file:
            os.environ['TOKEN'] = file.readline()
    except Exception as e:
        print(f"{e}\nERROR: Could not read TOKEN file")
        exit()

    client.run(os.environ['TOKEN'])

if __name__ == '__main__':
    main()