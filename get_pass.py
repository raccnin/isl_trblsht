from onepassword.client import Client, DesktopAuth


async def open_client(user: str):
    return await Client.authenticate(
            auth=DesktopAuth(
                account_name=user
                ),
            integration_name="diag",
            integration_version="v1"
            )


async def get_pass(client: Client, url):
    return await client.secrets.resolve(url)
