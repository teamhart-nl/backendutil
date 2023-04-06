################################################
# This script will register all .json files in #
# the current working directory to the API.    #
# Move this script to the directory with the   #
# .json files and run it.                      #
# Alternatively, call the #register function   #
################################################
import glob, json, requests, os
from requests import Session

class BackendIO:
    """Interface with the backend
    
    Requires the backend to be running.

    Full documentation available here: https://github.com/teamhart-nl/vibration-engine#api-usage

    If placed in a folder and ran directly, will register all .json files in the folder to the backend.
    """

    # Configurable
    __use_session__ = False
    __url__: str = None
    __port__: int = None
    __log_info__ = True
    __log_verbose__ = False

    # Session
    __session__: Session = None

    def __init__(
            self,
            use_session: bool,
            url: str = "http://localhost:",
            port: int = 8000,
            headers: 'dict[str, str]' = {'Content-Type' : 'application/json'},
            log_info: bool = True,
            log_verbose: bool = False
    ):
        """Initializes the class.

        Args:
        - use_session (`bool`): whether to use a session for the requests.
                Makes transmission faster, but it occupies the connection,
                which may cause problems when using multiple instances.
        - url (`str`, optional): The URL to the backend. Defaults to `http://localhost:`
        - port (`int`, optional): The port of the backend. Defaults to `8000`
        - headers (`dict[str, str]`, optional): The headers to use for the requests.
                Defaults to `{'Content-Type' : 'application/json'}`.
                Ignored if `use_session` is `False`.
        - log_info (`bool`, optional): Whether to log info messages. Defaults to `True`.
        - log_verbose (`bool`, optional): Whether to log verbose messages. Defaults to `False`.
        """
        self.__use_session__ = use_session
        self.__url__ = url
        self.__port__ = port
        self.__log_info__ = log_info
        self.__log_verbose__ = log_verbose

        if self.__use_session__:
            self.__session__ = Session()
            self.__session__.headers.update(headers)

    def __url__(self):
        """Returns the URL to the backend.

        Returns:
            str: The URL to the backend.
        """
        return self.__url__ + str(self.__port__)
    
    def __del__(self):
        """Deletes the session."""
        self.__log_info__("Deleting BackendIO session.")
        if self.__use_session__:
            self.__session__.close()
        self.__log_info__("Deleted BackendIO session.")

    def __log_info__(self, message: str):
        """Logs an info message.

        Args:
        - message (`str`): The message to log.
        """
        if self.__log_info__:
            print(message)

    def __log_verbose__(self, message: str):
        """Logs a verbose message.

        Args:
        - message (`str`): The message to log.
        """
        if self.__log_verbose__:
            print(message)

    def register_patterns(self, patterns: 'list[(str, str)]' = [], path = "*.json") -> 'tuple(int, list[str])':
        """Registers patterns to the backend.\n
        - Uses patterns in the `patterns` argument.
        - Uses `.json` found in the 'current-working-directory/path'.
        - See https://github.com/teamhart-nl/vibration-engine#register

        Args:
        - patterns (`list[(str, str)]`, optional): The patterns to register. Defaults to `[]`.
                    Must be a list of tuples, where the first element is the name of the pattern
                    and the second element is the json string.
        - path (`str`, optional): the path to the json files from the cwd. Defaults to `*.json`.

        Returns:
        - `tuple(int, list[str])`: The return code and the registered patterns.
        """
        self.__log_verbose__("Registering patterns. Patterns: {}, Path: {}".format(patterns, path))

        # Load all .json files in the cwd
        files = glob.glob(os.getcwd() + path)

        # If there are none, print a message and exit
        if len(files) == 0:
            self.__log_info__("No .json files found in the {} directory to register.".format(os.getcwd() + path))
            return

        # Create the dictionary
        register_datapacket = {
            "patterns": []
        }

        # For each file load the data and add it to the dictionary
        for file in files:
            data = json.load(open(file))

            # Add the data to the dictionary
            register_datapacket['patterns'].append({
                "pattern_name": file.replace('.json', '').replace("\\", "/").split("/")[-1],
                "pattern": data
            })

        # Add the patterns to the dictionary
        for pattern in patterns:
            register_datapacket['patterns'].append({
                "pattern_name": pattern[0],
                "pattern": pattern[1]
            })

        self.__log_info__("Registering patterns: {}".format(
            ", ".join([pattern['pattern_name'] for pattern in register_datapacket['patterns']])
        ))

        # Make a post request to the API
        if self.__use_session__:
            r = self.__session__.post(self.__url__(), json=register_datapacket)
        else:
            r = requests.post(self.__url__(), json=register_datapacket)
        code = r.status_code

        self.__log_verbose__("Registered patterns. Return code: {}, Patterns: {}".format(code, register_datapacket['patterns']))

        return code, register_datapacket['patterns']
    
    def pattern(self, pattern_name: str, force_now: bool = False) -> int:
        """Transmits a pattern to the backend.
        See https://github.com/teamhart-nl/vibration-engine#pattern

        Args:
        - pattern_name (`str`): The name of the pattern to transmit.
        - force_now (`bool`, optional): Whether to force the pattern to be transmitted now.
                Removes the queue of patterns. Defaults to `False`.
        
        Returns:
        - `int`: The return code.
        """
        payload = {
            "pattern_name": pattern_name,
            "force_now": force_now
        }
        self.__log_info__("Transmitting pattern. Pattern: {}, Force now: {}".format(pattern_name, force_now))
        if self.__use_session__:
            r = self.__session__.post(self.__url__() + "/devices/pattern", json=payload)
        else:
            r = requests.post(self.__url__() + "/devices/pattern", json=payload)
        return r.status_code

    def encoding(self, encoding: str) -> int:
        """Transmits an encoding to the backend.
        See https://github.com/teamhart-nl/vibration-engine#encoding

        Args:
        - encoding (`str`): The encoding string

        Returns:
        - `int`: The return code.
        """
        # Make a post request to the API
        self.__log_info__("Transmitting encoding. Encoding: {}".format(encoding))
        if self.__use_session__:
            r = self.__session__.post(self.__url__() + "/devices/encoding", json={"encoding": encoding})
        else:
            r = requests.post(self.__url__() + "/devices/encoding", json={"encoding": encoding})
        code = r.status_code

        return code
    

if __name__ == "__main__":
    BackendIO(use_session=True).register_patterns()