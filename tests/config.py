import os
from configparser import BasicInterpolation, ConfigParser


class SecEnvInterpolation(BasicInterpolation):
    secure_vars_env = os.environ.get("office365_python_sdk_securevars", None)
    if not secure_vars_env:
        raise EnvironmentError(
            "The environment variable 'office365_python_sdk_securevars' is not set."
        )

    secure_vars = secure_vars_env.split(";")

    def before_get(self, parser, section, option, value, defaults):
        value = super(SecEnvInterpolation, self).before_get(
            parser, section, option, value, defaults
        )
        if option == "password":
            return self.secure_vars[1]
        elif option == "client_secret":
            return self.secure_vars[3]
        else:
            return value


def load_config():
    cp = ConfigParser(interpolation=SecEnvInterpolation())
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(root_dir, "settings.cfg")
    cp.read(config_file)
    return cp
