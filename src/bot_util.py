from bot_exceptions import BotWarning
from bot_exceptions import BotException
#TODO: replace with pathlib?
import os; from os import path, makedirs, listdir
import json
import helper
import dice, character, parse_json
import bot_exceptions as exc

#INFO: DO NOT DECLARE NEW CONSTANTS IN constants.py AS IT IS DOWNSTREAM OF MY OTHER PROJECT AND WILL BE REPLACED AFTER EACH UPDATE

#TODO: Use a SQLite db in the backend for everything instead of the dir files?
#Replace ACTIVE_CHAR with Character Caching completely? 

ERROR_MESSAGES_SILENT_REPLY_DEFAULT = True
UNEXPECTED_ERROR_DEFAULT_TEXT = 'UNEXPECTED ERROR'

PLAYER_CHARACTER_CACHE ={
    #INFO: key -> val 
    #player_id -> characterObject
}

MAX_CHAR_FILE_SIZE = {
    'INT': 1024 * 100,
    'STR': '100KB'
}

DIR_PATH = path.dirname(path.abspath(__file__))
RES_PATH = path.join(DIR_PATH, '..', 'res')

WARNING_EMPTY_MASTER_FILE = 'You have not entered any Gamemasters in the MASTER file. Please Enter the discord ID for all users that are suppossed to have Master permissions'
WARNING_NOT_A_MASTER = "You are not registered in the MASTER file. Ask the bot host to add you manually or consult the documentation."
WARNING_NOT_A_PLAYER = "You are not registered in the ACTIVE_PLAYER file. Ask a registered Gamemaster to add you."

def validate_user_id(user_id:str, verbose:bool = True) -> bool:
    #INFO: I don't know the exact user ID length constraints, but they appear to me as 17-19 digits
    #TODO: Exception messages
    if len(user_id) >= 20 or len(user_id) <= 16:
        if verbose:
            print(f'WARNING: User ID <{user_id}> is invalid length (17 - 19 digits)')
        return False
    if not user_id.isdigit():
        if verbose:
            print(f'WARNING: User ID <{user_id}> contains non-digit characters')
        return False
    return True

#TODO: rework
def create_file_if_not_exists(file_name:str, file_path:str = RES_PATH) -> None:
    #TODO: implement sepearte sanitize_file_name function?
    file_name = file_name.replace('..', '')
    file_name = file_name.replace('\\', '')
    file_name = file_name.replace('/', '')
    file_name = file_name.replace(':', '')
    
    file_path = path.join(file_path, file_name)
    if not path.exists(file_path):
        print(f"{file_name} file does not exist!")
        print(f"Creating {file_path}")
        file = open(file_path, 'x'); file.close() 

def setup_res() -> None:
    makedirs(RES_PATH, exist_ok=True)
    
    create_file_if_not_exists('ACTIVE_PLAYER')
    players_dir_path = path.join(RES_PATH, 'Players')
    makedirs(players_dir_path, exist_ok=True)

    token_path = path.join(RES_PATH, 'TOKEN')
    create_file_if_not_exists('TOKEN')
    with open(token_path, 'r+') as file:
        if file.read() == '':
            print('TOKEN file empty!')
            file.write(input('Enter your discord bot TOKEN: ').strip())
     
    master_path = path.join(RES_PATH, 'MASTER')
    create_file_if_not_exists('MASTER')
    with open(master_path, 'r+') as file:
        if file.read() == '':
            print(WARNING_EMPTY_MASTER_FILE)
            print("You will now be prompted to enter all Gamemasters discord IDs. You may exit by typing 'exit'.")
            while True:
                user_input = input('Enter a discord user ID: ')
                if user_input == 'exit':
                    break
                elif validate_user_id(user_input):
                    print(f"Adding <{user_input}> to MASTER file.")
                    file.write(user_input + '\n')


def create_player_dir(id:int) -> None:
    makedirs(path.join(RES_PATH, 'Players'), exist_ok=True)
    makedirs(path.join(RES_PATH, 'Players', str(id)), exist_ok=True)
    create_file_if_not_exists('ACTIVE_CHAR', path.join(RES_PATH, 'Players', str(id)))

#TODO: make function that only returns valid masters?
def load_masters() -> list:
    with open(path.join(RES_PATH, 'MASTER'), 'r') as file:
        return file.readlines()

def check_master(user_id:int) -> bool:
    for master in load_masters():
        master = master.replace('\n', '')
        if validate_user_id(master):
            if int(master) == user_id:
                return True
    return False

def load_players() -> list:
    with open(path.join(RES_PATH, 'ACTIVE_PLAYER'), 'r') as file:
        return file.readlines()

def check_player(user_id:int) -> bool:
    for player in load_players():
        player = player.replace('\n', '')
        if validate_user_id(player):
            if int(player) == user_id:
                return True
    return False


def add_player(id:int) -> None:
    create_player_dir(id)
    create_file_if_not_exists('ACTIVE_PLAYER')

    if not validate_user_id(str(id)):
        raise exc.UserIdError(id)
    if check_player(id):
        raise exc.BotWarning(f"Player <{id}> already added")
        
    try:
        with open(path.join(RES_PATH, 'ACTIVE_PLAYER'), 'a+') as file:
            file.write(f"{id}\n")
    except:
        raise BotException(f"Could not append ACTIVE_PLAYER file for <{id}>")

    return

def remove_player(id:int, remove_player_dir:bool = False) -> None:
    active_player_path = path.join(RES_PATH, 'ACTIVE_PLAYER')
        
    #TODO: clear/remvoe dir option? 
    if remove_player_dir:
        print("Clear directory not implemented yet")
        players_dir_path = path.join(RES_PATH, 'Players')
        player_path = path.join(players_dir_path, str(id))
        #clear_dir()

    if not path.exists(active_player_path):
        try:
            file = open(active_player_path, 'x'); file.close() 
            raise exc.BotException('ACTIVE_PLAYER FILE DID NOT EXIST. CREATED SUCCESSFULLY')
        except:
            raise exc.BotException('ACTIVE_PLAYER FILE DID NOT EXIST. COULD NOT CREATE FILE')

    if not validate_user_id(str(id)): raise exc.UserIdError(id)

    player_found = False
    try:
        with open(active_player_path, 'r+') as file:
            lines = file.readlines()
            #TODO: Add a safety mechanism for truncate()
            file.seek(0)
            file.truncate(0)
            for line in lines:
                line = line.replace('\n', '')
                if line == str(id):
                    player_found = True
                else:
                    file.write(line + '\n')
    except Exception as e:
        raise exc.BotException('FAILED TO MODIFY ACTIVE_PLAYER FILE')
    
    if not player_found: raise exc.BotWarning('PLAYER NOT FOUND IN ACTIVE_PLAYER')
    
    return

def add_character(id:int, file_name:str, json_object:dict) -> None: 
    players_dir_path = path.join(RES_PATH, 'Players')
    player_path = path.join(players_dir_path, str(id))
    character_path = path.join(player_path, file_name)
    
    if path.exists(character_path):
        raise exc.BotException(f"Character {file_name} already exists")

    json_object = parse_json.recursive_dict_merge(parse_json.create_empty_json(), json_object)
    with open(character_path, 'w') as file:
        file.write(json.dumps(json_object))
    
    return

def list_characters(player_id:int):
    player_dir = path.join(RES_PATH, 'Players', str(player_id))
    if not path.exists(player_dir):
        raise exc.DirectoryNotFoundError(player_dir)
    return listdir(player_dir)

def change_character(player_id:int, character_file_name:str) -> None:
    create_player_dir(player_id)
    player_dir = path.join(RES_PATH, 'Players', str(player_id))
    create_file_if_not_exists('ACTIVE_CHAR', player_dir)
    if character_file_name not in listdir(player_dir):
        raise exc.CharacterNotFoundError(character_file_name)
    with open(path.join(player_dir, 'ACTIVE_CHAR'), 'w') as f: 
        f.write(character_file_name)

def read_active_char_file(player_id:int) -> str:
    player_dir = path.join(RES_PATH, 'Players', str(player_id))
    if not path.exists(player_dir):
        raise exc.PlayerDirectoryNotFoundError(f"")
    
    active_char_path = path.join(player_dir, 'ACTIVE_CHAR')
    if not path.exists(active_char_path):
        raise exc.BotException("Player does not have a ACTIVE_CHAR file")
    with open(active_char_path, 'r') as file:
        return file.readline().replace('\n', '')

def remove_player_character(player_id:int, character_file_name:str) -> None:
    player_dir = path.join(RES_PATH, 'Players', str(player_id))
    if not path.exists(player_dir):
        raise exc.PlayerDirectoryNotFoundError(player_id)
    os.remove(path.join(player_dir, character_file_name))

def cache_player_character(player_id:int) -> None:   
    player_dir = path.join(RES_PATH, 'Players', str(player_id))
    file_name = read_active_char_file(player_id)
    #TODO: validate file_name
    if file_name == '':
        raise exc.BotException(f"Player <{player_id}> has selected no Character")

    if file_name not in list_characters(player_id):
        raise exc.BotException(f"Character \"{file_name}\" does not exist")

    #TODO: Exception for get_json_from_file
    PLAYER_CHARACTER_CACHE[player_id] = character.Character(
        parse_json.get_json_from_file(
            path.join(player_dir, file_name)
        )
    )
    print(f"SUCCESS: Cached \"{file_name}\" for <{player_id}>")

def dice_roll_string(times:int, size:int) -> str:
    return f"Roll {times}d{size} = {dice.ROLL_DICE(times, size)}"

if __name__ == '__main__':
    exit()
