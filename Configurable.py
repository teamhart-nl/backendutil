import json
import os

# File all configs are stored in
__CONFIG_FILE__ = "config.json"

# Default configuration.
# If you want to add custom configuration to classes, do so by setting a variable in the class to that value.
# See the Monitor class for examples.
__DEFAULT_CONFIG__ = {
    "use-config": False,
    "use-config-comment": [
        "Set to true if you edit the config file manually.",
        "If false, the config file will be overwritten with the default config every restart."
    ]
}

# Types allowed to be included in the configuration file
__CONFIGURABLE_TYPES__ = [dict, str, int, float, bool, tuple]

# The dictionary mirror of the configuration file.
# Do not access this variable externally without also calling #save_config()
__CONFIGURABLES__ = json.loads("\n".join(open(__CONFIG_FILE__, "r").readlines())) if os.path.exists(__CONFIG_FILE__) else __DEFAULT_CONFIG__
if "use-config" not in __CONFIGURABLES__ or not __CONFIGURABLES__["use-config"]:
    __CONFIGURABLES__ = __DEFAULT_CONFIG__

# Whether to debug print any new registrations
__PRINT_REGISTRATIONS__ = False


class Configurable:
    """Stores fields in any class to the global configuration of the program"""

    def __init__(self, section: str = "", **kwargs) -> None:

        # Name
        name = self.make_name()

        # Add section if missing
        if section != "" and section not in __CONFIGURABLES__:
            __CONFIGURABLES__[section] = {}
        c = (__CONFIGURABLES__[section] if section != "" else __CONFIGURABLES__)
        
        # Add name if missing and init counters
        if name not in c:
            c[name] = {}
        
        # Redirect
        c = c[name]

        # Counters
        configured = 0
        default = 0

        # Add configurable attributes that are missing from defaults
        for key in self.__dir__():
            if key.startswith("_"):
                continue
            value = self.__getattribute__(key)
            if type(value) not in __CONFIGURABLE_TYPES__:
                continue
            if key not in c:
                c[key] = value
                default += 1
            else:
                self.__setattr__(key, c[key])
                configured += 1


        # Save the config file if any edits were made
        if default > 0:
            Configurable.save_config()

        # Print registrations
        if __PRINT_REGISTRATIONS__:
            print("'{} ({})' registered {} configured and {} default attributes".format(name, self.__class__.__name__, configured, default))

        # Init super
        super().__init__(**kwargs)

    @staticmethod
    def save_config() -> None:
        """Save the configuration to disk"""
        open(__CONFIG_FILE__, "w").writelines(Configurable.make_config())
    
    @staticmethod
    def make_config() -> str:
        """Make a config json from the current configuration"""
        return json.dumps(__CONFIGURABLES__, indent=4)

    def make_name(self) -> str:
        """Make a name for the class to be used in the config json.
        
        Uses the string representation of the class if it has been overwritten with `__str__`, or the class name otherwise."""
        return str(self.__class__.__name__).lower() if str(self)[0] == "<" else str(self)

if __name__ == "__main__":
    class Testi(Configurable):
        def __init__(self) -> None:
            super().__init__({"config1": 0.5})
    class RandomName(Configurable):
        def __init__(self) -> None:
            super().__init__({"config2": 0.69})
        def __str__(self) -> str:
            return "example-name"
    Testi()
    RandomName()
    print(Configurable.make_config())