import getpass

import keyring
import questionary
from keyrings.alt.file import PlaintextKeyring

user = getpass.getuser()
keyring.set_keyring(PlaintextKeyring())


def _try_get_password():
    try:
        pwd = keyring.get_password("canvas", user)
        if isinstance(pwd, bytes):
            return pwd.decode().strip()
        return pwd.strip()
    except:
        return None


def set_token():
    token = questionary.password("Please paste your Access Token:").ask()
    keyring.set_password("canvas", user, token)
    replay = _try_get_password()

    if replay != token:
        raise RuntimeError("Fail to set token for current user")

    return replay


def get_token():
    token = _try_get_password()
    if token:
        return token
    return set_token()


if __name__ == "__main__":
    if _try_get_password():
        conf = questionary.confirm(
            "An access token had been set for current user. Do you want to overwrite?"
        ).ask()

        if not conf:
            exit(1)

    if set_token():
        print(f"Token has been stored for user {user}")
