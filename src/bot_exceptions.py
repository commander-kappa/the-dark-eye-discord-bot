class BotException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DirectoryNotFoundError(FileNotFoundError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class PlayerDirectoryNotFoundError(DirectoryNotFoundError):
    def __init__(self, player_id):
        self.message = f"Player <{player_id}> does not have a directory"
        super().__init__(self.message)

class CharacterNotFoundError(FileNotFoundError):
    def __init__(self, char_name:str):
        self.message = f"Character \"{char_name}\" not found"
        super().__init__(self.message)

class ResFileNotFoundError(BotException):
    def __init__(self, file_name):
        self.message = f"File res/{file_name} not found"
        super().__init__(self.message)

class BotWarning(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
   
class UserIdError(BotException):
    def __init__(self, id:int):
        self.message = f"User ID <{id}>is invalid"
        super().__init__(self.message)

class PermissionError(BotException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotMasterError(PermissionError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotPlayerError(PermissionError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
