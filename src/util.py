from os import path, makedirs
#TODO: Manage dependencies?
import json
import helper

MAX_CHAR_FILE_SIZE = {
    'INT': 1024 * 100,
    'STR': '100KB'
}

DIR_PATH = path.dirname(path.abspath(__file__))
RES_PATH = path.join(DIR_PATH, '..', 'res')

WARNING_EMPTY_MASTER_FILE = 'You have not entered any Gamemasters in the MASTER file. Please Enter the discord ID for all users that are suppossed to have Master permissions'
WARNING_NOT_A_MASTER = "You are not registered in the MASTER file. Ask the bot host to add you manually or consult the documentation."
WARNING_NOT_A_PLAYER = "You are not registered in the PLAYER file. Ask a registered Gamemaster to add you."

def validate_user_id(user_id:str, verbose:bool = True) -> bool:
    #INFO: I don't know the exact user ID length constraints, but they appear to me as 17-19 digits
    if len(user_id) >= 20 or len(user_id) <= 16:
        if verbose:
            print(f'WARNING: User ID <{user_id}> is invalid length (17 - 19 digits)')
        return False
    if not user_id.isdigit():
        if verbose:
            print(f'WARNING: User ID <{user_id}> contains non-digit characters')
        return False
    return True

def create_file_if_not_exists(file_name:str) -> None:
    #TODO: implement sepearte sanitize_file_name function?
    file_name = file_name.replace('..', '')
    file_name = file_name.replace('\\', '')
    file_name = file_name.replace('/', '')
    file_name = file_name.replace(':', '')
    
    file_path = path.join(RES_PATH, file_name)
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

#TODO: replace int return codes with ExceptionClasses >:/
#Is this function over-engineered?
#TODO: find fitting Exceptions and remove inner try blocks
def add_player(id:int) -> int:
    try:
        try:
            create_player_dir(id)
        except Exception as e:
            print(e)
            return 1 #FAILED TO CREATE DIR

        players_dir_path = path.join(RES_PATH, 'Players')
        player_path = path.join(players_dir_path, str(id))
        create_file_if_not_exists('ACTIVE_PLAYER')

        if not validate_user_id(str(id)):
            return 2 #USER ID INVALID
        
        try:
            if check_player(id):
                return 3 #PLAYER ALREADY ADDED
        except Exception as e:
            print(e)
            return 4 #FAILED TO READ FILE
        try:
            with open(path.join(RES_PATH, 'ACTIVE_PLAYER'), 'a+') as file:
                file.write(f"{id}\n")
        except Exception as e:
            print(e)
            return 5 #FAILED TO APPEND FILE
        
        return 0 #SUCCESS

    except Exception as e:
        print(e)
        return 127 #UNEXPECTED ERROR

REPLIES_ADD_PLAYER = {
    0: "SUCCESS: Registered",
    1: "ERROR: Failed to create directory for",
    2: "ERROR: Invalid User ID", #This cant possibly happen according to my code (yet)
    3: "ERROR: Already added Player",
    4: "ERROR: Failed to read ACTIVE_PLAYER file for",
    5: "ERROR: Failed to append ACTIVE_PLAYER file for",
    127: "ERROR: Unexpected failure for adding"
}  

def remove_player(id:int) -> int:
    try:        
        active_player_path = path.join(RES_PATH, 'ACTIVE_PLAYER')
        players_dir_path = path.join(RES_PATH, 'Players')
        player_path = path.join(players_dir_path, str(id))
        
        if not path.exists(active_player_path):
            try:
                file = open(active_player_path, 'x'); file.close() 
                return 1 #ACTIVE_PLAYER FILE DOES NOT EXIST!
            except Exception as e:
                print(e)
                return 2 #ACTIVE_PLAYER DOES NOT EXIST AND COULD NOT CREATE

        if not path.exists(players_dir_path):
            try:
                makedirs(players_dir_path)
                return 3 #PLAYERS DIR DOES NOT EXIST
            except:
                print(e)
                return 4 #PLAYERS DIR DOES NOT EXIST AND COULD NOT CREATE            
        
        if not validate_user_id(str(id)):
            return 5 #USER ID INVALID
        
        playerFound = False
        try:
            with open(active_player_path, 'r+') as file:
                lines = file.readlines()
                #TODO: Add a safety mechanism for truncate()
                file.truncate(0)
                for line in lines:
                    line = line.replace('\n', '')
                    if line == str(id):
                        playerFound = True
                    else:
                        file.write(line + '\n')
        except Exception as e:
            print(e)
            return 6 #FAILED TO MODIFY FILE
        
        if playerFound:
            return 0 #SUCCESS
        else:
            return 7 #PLAYER NOT IN FILE
    except Exception as e:
        print(e)
        return 127 #UNEXPECTED ERROR

REPLIES_REMOVE_PLAYER = {
    0: "SUCCESS: Removed player",
    1: "ERROR: ACTIVE_PLAYER file does not exist. Created file. Could not remove",
    2: "ERROR: ACTIVE_PLAYER file does not exist. Could not create file. Could not remove",
    3: "ERROR: Players dir does not exist. Created dir. Could not remove",
    4: "ERROR: Players dir does not exist. Could not create dir. Could not remove",
    5: "ERROR: Invalid User ID", #This cant possibly happen according to my code (yet)
    6: "ERROR: Failed to modify ACTIVE_PLAYER file for",
    7: "ERROR: File did not contain Player",
    127: "ERROR: Unexpected failure for adding"
}  

def add_character(id:int, file_name:str, json_object:dict):        
    try:
        players_dir_path = path.join(RES_PATH, 'Players')
        player_path = path.join(players_dir_path, str(id))
        character_path = path.join(player_path, file_name)
        
        if path.exists(character_path):
            return 1 #CHARACTER ALREADY EXISTS

        json_object = helper.recursive_dict_merge(helper.create_empty_json(), json_object)
        try:
            with open(character_path, 'w') as file:
                file.write(json.dumps(json_object))
        #TODO: Differenciate Excpetions
        except Exception as e:
            print(e)
            return 2 #FAILED TO WRITE CHARACTER FILE
        
        return 0 #SUCCESS

    except Exception as e:
        print(e)
        return 127 #UNEXPECTED ERROR

REPLIES_ADD_CHAR = {
    0: "SUCCESS: Uploaded character",
    1: "ERROR: Character already exists",
    2: "ERROR: Failed to write character file",
    127: "ERROR: Unexpected failure for adding"
}  
if __name__ == '__main__':
    exit()