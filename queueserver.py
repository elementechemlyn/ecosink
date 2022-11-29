import asyncio

import ecoflow_server
import time

async def main():
    server = await asyncio.start_server(
        ecoflow_server.handle_ecoflow, '0.0.0.0', 6500)

    addr1 = server.sockets[0].getsockname()
    print(f'Serving 1 on {addr1}')

    #keepalive = asyncio.Task(ecoflow_server.ecoflow_keepalive())
    """
    #TODO This needs to be an mqtt client!!!!
    server2 = await asyncio.start_server(
        ecoflow_server.handle_ecoflow, '0.0.0.0', 6501)

    addr2 = server2.sockets[0].getsockname()
    print(f'Serving 2 on {addr2}')
    """
    async with server:
        await asyncio.gather(
            ecoflow_server.ecoflow_keepalive(),
            server.serve_forever())

asyncio.run(main())