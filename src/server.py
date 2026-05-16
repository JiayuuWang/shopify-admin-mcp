import os
from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings
from shopify import shopify, shopify_tools


def create_server() -> MCPServer:
    return MCPServer(
        name="shopify-admin-mcp",
        connections=[shopify],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai"),
    )


async def main() -> None:
    server = create_server()
    server.collect(*shopify_tools)
    await server.serve(port=8080)