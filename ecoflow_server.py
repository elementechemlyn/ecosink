import asyncio

import ecoflow_recieve
import ecoflow_send
import time

ecoflow_queue_tx = asyncio.Queue()
ecoflow_queue_rx = asyncio.Queue()

async def ecoflow_keepalive(rate_seconds = 10):
    data = ecoflow_send.get_pd()
    while True:
        print("Stayin alive!")
        await asyncio.gather(
            ecoflow_queue_tx.put(data),
            asyncio.sleep(rate_seconds)
        )

async def ecoflow_connection_init(reader,writer):
    buffer = b''
    data = ecoflow_send.get_serial_main()
    writer.write(data)
    await writer.drain()

    product_id = None

    buffer = await reader.read(1024)
    while(len(buffer)>=18):
        size = int.from_bytes(buffer[2:4], 'little')
        #TODO We should check the CRCs here (8 and 16)
        packet = buffer[:18+size]
        packet = ecoflow_recieve.decode_packet(packet)
        ecoflow_queue_rx.put_nowait(packet)
        if ecoflow_recieve.is_serial_main(packet[0:3]):
            serial = ecoflow_recieve.parse_serial(packet[3])
            print("Device Info:",serial)
            product_id = serial['product']
        buffer = buffer[18+size:]
    return product_id

async def handle_ecoflow(reader, writer):

    product_id = await ecoflow_connection_init(reader,writer)
    msg = b''
    while 1:
        data = await ecoflow_queue_tx.get()
        writer.write(data)
        await writer.drain()
        msg += await reader.read(1024)
        while(len(msg)>=18):
            size = int.from_bytes(msg[2:4], 'little')
            packet = msg[:18+size]
            packet = ecoflow_recieve.decode_packet(packet)
            ecoflow_queue_rx.put_nowait(packet)
            print(packet)
            msg = msg[18+size:]
        
