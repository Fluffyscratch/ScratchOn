"""
Manages the binding of Discord and Scratch accounts.
"""
async def dc2scratch(username: str) -> str | None:
    """
    Converts a Discord username to a Scratch username using stored bindings.

    :param username: Discord username to look up.
    :return: Corresponding Scratch username, or None if not found.
    """
    with (
        open("private/dcusers.txt") as discord_file,
        open("private/scusers.txt") as scratch_file,
    ):
        dc_users = [line.strip() for line in discord_file.readlines()]
        sc_users = [line.strip() for line in scratch_file.readlines()]

        if username in dc_users:
            index = dc_users.index(username)
            return sc_users[index]
        return None

async def scratch2dc(username: str) -> str | None:
    """
    Converts a Scratch username to a Discord username using stored bindings.

    :param username: Scratch username to look up.
    :return: Corresponding Discord username, or None if not found.
    """
    with (
        open("private/dcusers.txt") as discord_file,
        open("private/scusers.txt") as scratch_file,
    ):
        dc_users = [line.strip() for line in discord_file.readlines()]
        sc_users = [line.strip() for line in scratch_file.readlines()]

        if username in sc_users:
            index = sc_users.index(username)
            return dc_users[index]
        return None

async def bind_user(dc_username: str, sc_username: str) -> None:
    """
    Binds a Discord username to a Scratch username by appending them to the respective files.

    :param dc_username: Discord username to bind.
    :param sc_username: Scratch username to bind.
    """
    with (
        open("private/dcusers.txt", "a") as discord_users,
        open("private/scusers.txt", "a") as scratch_users,
    ):
        discord_users.write(f"{dc_username}\n")
        scratch_users.write(f"{sc_username}\n")

async def unbind_user(dc_username: str) -> None:
    """
    Unbinds a Discord username from its corresponding Scratch username by removing them from the respective files.

    :param dc_username: Discord username to unbind.
    """
    with (
        open("private/dcusers.txt", "r") as discord_file,
        open("private/scusers.txt", "r") as scratch_file,
    ):
        dc_users = [line.strip() for line in discord_file.readlines()]
        sc_users = [line.strip() for line in scratch_file.readlines()]

    if dc_username in dc_users:
        index = dc_users.index(dc_username)
        del dc_users[index]
        del sc_users[index]

        with (
            open("private/dcusers.txt", "w") as discord_file,
            open("private/scusers.txt", "w") as scratch_file,
        ):
            discord_file.write("\n".join(dc_users) + "\n")
            scratch_file.write("\n".join(sc_users) + "\n")

async def modify_binding(dc_username: str, new_sc_username: str) -> None:
    """
    Modifies the Scratch username bound to a given Discord username.

    :param dc_username: Discord username whose binding is to be modified.
    :param new_sc_username: New Scratch username to bind.
    """
    with (
        open("private/dcusers.txt", "r") as discord_file,
        open("private/scusers.txt", "r") as scratch_file,
    ):
        dc_users = [line.strip() for line in discord_file.readlines()]
        sc_users = [line.strip() for line in scratch_file.readlines()]

    if dc_username in dc_users:
        index = dc_users.index(dc_username)
        sc_users[index] = new_sc_username

        with (
            open("private/dcusers.txt", "w") as discord_file,
            open("private/scusers.txt", "w") as scratch_file,
        ):
            discord_file.write("\n".join(dc_users) + "\n")
            scratch_file.write("\n".join(sc_users) + "\n")
        return True
    return False