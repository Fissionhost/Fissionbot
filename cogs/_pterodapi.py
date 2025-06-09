import aiohttp
import asyncio
from json import dumps, loads

egg_ids: dict[tuple, int] = {
    ('Minecraft', 'Pocketmine'): 19,
    ('Minecraft', 'Nukkit'): 18,
    ('Discord Bot', 'Javascript'): 17,
    ('Discord Bot', 'Python'): 16,
    ('Minecraft', 'Fabric'): 15,
    ('Minecraft', 'Paper'): 5,
    ('Minecraft', 'Vanilla'): 4,
    ('Minecraft', 'Forge'): 3,
    ('Minecraft', 'Bungeecord'): 1,
}

code_docker_images: dict[tuple, int] = {
    ('Discord Bot', 'Javascript'): ("ghcr.io/parkervcp/yolks:nodejs_21", "node index.js"),
    ('Discord Bot', 'Python'): ("ghcr.io/parkervcp/yolks:python_3.12", "python app.py"),
    ('Minecraft', 'Fabric'): ("ghcr.io/parkervcp/yolks:java_21", "java -jar server.jar"),
    ('Minecraft', 'Paper'): ("ghcr.io/parkervcp/yolks:java_21", "java -jar server.jar"),
    ('Minecraft', 'Vanilla'): ("ghcr.io/parkervcp/yolks:java_21", "java -jar server.jar"),
    ('Minecraft', 'Forge'): ("ghcr.io/parkervcp/yolks:java_21", "java -jar server.jar"),
    ('Minecraft', 'Bungeecord'): ("ghcr.io/parkervcp/yolks:java_21", "java -jar server.jar"),
    ('Minecraft', 'Pocketmine'): ("ghcr.io/parkervcp/yolks:java_21", "java -jar server.jar"),
    ('Minecraft', 'Nukkit'): ("ghcr.io/parkervcp/yolks:java_21", "java -jar server.jar")
}

bot_egg_ids: list[int] = [
    16,  # Discord Bot - Python
    17,  # Discord Bot - Javascript
]

server_egg_ids: list[int] = [
    1,  # Minecraft - Bungeecord
    3,  # Minecraft - Forge
    4,  # Minecraft - Vanilla
    5,  # Minecraft - Paper
    15,  # Minecraft - Fabric
    18,  # Minecraft - Nukkit
    19,  # Minecraft - Pocketmine
]

id_eggs: dict[tuple, int] = {
    19: ('Minecraft - Pocketmine'),
    18: ('Minecraft - Nukkit'),
    17: ('Discord Bot - Javascript'),
    16: ('Discord Bot - Python'),
    15: ('Minecraft - Fabric'),
    5: ('Minecraft - Paper'),
    4: ('Minecraft - Vanilla'),
    3: ('Minecraft - Forge'),
    1: ('Minecraft - Bungeecord'),
}


class Users:
    def __init__(self, address: str, application_token: str, user_token: str, debug=False):
        self.address = address
        self.application_token = application_token
        self.user_token = user_token
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {self.application_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.user_headers = {
            "Authorization": f"Bearer {self.user_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_users(self) -> str:
        """Fetches every user from the Pterodactyl API."""
        url = f'{self.address}/api/application/users'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()

    async def get_details(self, username: str) -> str:
        """Fetches user details by username."""
        url = f'{self.address}/api/application/users?filter[username]={username}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()

    async def get_servers(self, userid) -> str:
        """Fetches all servers associated with a user ID."""
        url = f'{self.address}/api/application/users/{userid}?include=servers'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()

    async def get_id(self, username: str):
        """Fetches the user ID for a given username."""
        data = await self.get_details(username)
        attribs = loads(data)["data"]
        return attribs[0]["attributes"]["id"] if attribs != [] else None

    async def create_user(self, username: str, email: str, firstname: str, surname: str) -> str:
        """Creates a new user with the given details."""
        url = f'{self.address}/api/application/users'
        payload = '{{"email": "{}","username": "{}","first_name": "{}","last_name": "{}"}}'.format(email, username, firstname, surname)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=self.headers) as response:
                return await response.text()
    
    async def delete_user(self, id: int):
        """Deletes a user by ID."""
        url = '{}/api/application/users/{}'.format(self.address, id)
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as response:
                return await response.text()
     
    async def update_user_password(self, id: int, email: str, username: str, first_name: str, last_name: str, password: str):
        """Updates user details including password."""
        url = '{}/api/application/users/{}'.format(self.address, id)
        payload = '{{"email": "{}","username": "{}","first_name": "{}","last_name": "{}","language": "en","password": "{}"}}'.format(email, username, first_name, last_name, password)
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, data=payload, headers=self.headers) as response:
                return await response.text()

    async def mop(self, username: str): # My sister came up with this function name
        """Cleans the name of a user so it can be used in pterodactyl."""
        invalid_chars = [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '.', ',', ';', '!', '@', '#', '$', '%', '^', '&', '(', ')', '=', '+', '-', '_']
        return ''.join(char for char in username if char not in invalid_chars).lower()


class Nodes:
    def __init__(self, address: str, application_token: str, user_token: str, debug=False):
        self.address = address
        self.application_token = application_token
        self.user_token = user_token
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {self.application_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.user_headers = {
            "Authorization": f"Bearer {self.user_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def list_nodes(self) -> str:
        """Fetches all nodes from the Pterodactyl API."""
        url = f'{self.address}/api/application/nodes'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()

    async def get_details(self, node_id: int) -> str:
        """Fetches details of a specific node by its ID."""
        url = f'{self.address}/api/application/nodes/{node_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()


class Servers:
    def __init__(self, address: str, application_token: str, user_token: str, debug=False):
        self.address = address
        self.application_token = application_token
        self.user_token = user_token
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {self.application_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.user_headers = {
            "Authorization": f"Bearer {self.user_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_available_allocations(self, node_id: int) -> list:
        url = f"{self.address}/api/application/nodes/1/allocations"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                data = await response.json()
                available = [alloc for alloc in data["data"] if alloc["attributes"]["assigned"] is False]
                return available[0:1]

    async def create_server(self, egg: list[str, str], user_id: int) -> str:
        """Creates a server with the specified egg type and user ID."""

        if isinstance(egg, int):
            egg = id_eggs[egg]
            print(egg)

        egg_tuple = tuple(egg)
        if egg_tuple not in egg_ids:
            return '{"errors":"Invalid egg type"}'

        egg_id = egg_ids[egg_tuple]
        docker_id = code_docker_images[egg_tuple]
        allocation = await self.get_available_allocations(node_id=1)

        if not allocation or allocation == []:
            return '{"errors":"No available allocations"}'
        
        allocation = allocation[0]["attributes"]["id"]

        url = f'{self.address}/api/application/servers'
        server_payload = {
            "name": "{}-{}".format(egg[0].replace(" ","-"), egg[1]),
            "user": user_id,
            "egg": egg_id,
            "docker_image": "ghcr.io/pterodactyl/yolks:java_21",
            "startup": "java -jar server.jar",
            "environment": {
                "BUNGEE_VERSION": "latest",
                "SERVER_JARFILE": "server.jar",
                "APP_PY": "app.py",
                "AUTO_UPDATE": False,
                "USER_UPLOADED_FILES": False,
                "USER_UPLOAD": False,
                "PY_FILE": "app.py",
                "REQUIREMENTS_FILE": "requirements.txt",
                "VERSION": "PM5",
                "BUILD_NUMBER": "latest"
            },
            "limits": {
                "memory": 2048,
                "swap": 0,
                "disk": 4096,
                "io": 500,
                "cpu": 50
            },
            "feature_limits": {
                "databases": 2,
                "backups": 3
            },
            "allocation": {
                "default": allocation
            }
        }
        bot_payload = {
            "name": "{}-{}".format(egg[0].replace(" ","-"), egg[1]),
            "user": user_id,
            "egg": egg_id,
            "docker_image": docker_id[0],
            "startup": docker_id[1],
            "environment": {
                "lang": docker_id[1],
                "APP_PY": "app.py",
                "AUTO_UPDATE": False,
                "USER_UPLOADED_FILES": False,
                "USER_UPLOAD": False,
                "PY_FILE": "app.py",
                "REQUIREMENTS_FILE": "requirements.txt"
            },
            "limits": {
                "memory": 512,
                "swap": 0,
                "disk": 4096,
                "io": 500,
                "cpu": 20
            },
            "feature_limits": {
                "databases": 2,
                "backups": 3
            },
            "allocation": {
                "default": allocation
            }
        }

        payload = dumps(bot_payload if egg_tuple[0] == "Discord Bot" else server_payload)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=self.headers) as response:
                return await response.text()

    async def delete_server(self, serverid) -> str:
        """Deletes a server by its ID."""
        url = f"{self.address}/api/application/servers/{serverid}"
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as response:
                return await response.text()

    async def edit_server_build(self, serverid: int, payload: dict | None = None):
        if not payload:
            # Right now only payloads are supported
            print("[PTERODAPI][ERROR] No payload provided. Only payloads[dict] are supported currently.")
            return '{"errors":"No payload provided"}'

        url = f"{self.address}/api/application/servers/{serverid}/build"
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=self.headers, data=dumps(payload)) as response:
                return await response.text()

    async def reinstall_server(self, serverid) -> str:
        """Reinstalls a server by its ID."""
        url = f"{self.address}/api/application/servers/{serverid}/reinstall"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers) as response:
                return await response.text()

    async def get_details(self, server_id: int) -> str:
        """Fetches details of a server by its ID."""
        url = f"{self.address}/api/application/servers/{server_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()

    async def get_servers(self) -> str:
        """Fetches all servers"""
        url = f"{self.address}/api/application/servers"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.text()

    async def get_server_utilisation(self, server_id: int) -> str:
        """Fetches the amount of resources a server is actively using"""
        url = f"{self.address}/api/client/servers/{server_id}/resources"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.user_headers) as response:
                return await response.text()


class API:    
    def __init__(self, address: str, application_token: str, user_token: str, debug=False):
        self.address = address
        self.application_token = application_token
        self.user_token = user_token
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {self.application_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.user_headers = {
            "Authorization": f"Bearer {self.user_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self.Users = Users(address, application_token, user_token, debug)
        self.Servers = Servers(address, application_token, user_token, debug)
        self.Nodes = Nodes(address, application_token, user_token, debug)


async def test():
    # api = API(address="https://panel.fissionhost.org", application_token="ptla_4fB6pnehpUVKDEUY6L3IkFbKNfFuzFT4PXl9Gd6iBqp", 							 user_token="ptlc_1qcXqvxqhFdQyBDk4UvvF0sw6IM2TDTd5UTFFc6BHUO", debug=True)
    pass


if __name__ == "__main__":
	asyncio.run(test())
	