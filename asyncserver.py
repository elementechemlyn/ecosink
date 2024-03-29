import asyncio

import ecoflow_recieve
import ecoflow_send
import time

async def connection_init(reader,writer):
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
        if ecoflow_recieve.is_serial_main(packet[0:3]):
            serial = ecoflow_recieve.parse_serial(packet[3])
            print("Device Info:",serial)
            product_id = serial['product']
        buffer = buffer[18+size:]
    return product_id

async def handle(reader, writer):

    product_id = await connection_init(reader,writer)
    msg = b''
    while 1:
        data = ecoflow_send.get_pd()
        writer.write(data)
        data = ecoflow_send.get_ems_main()
        writer.write(data)
        data = ecoflow_send.get_inverter()
        writer.write(data)
        data = ecoflow_send.get_mppt()
        writer.write(data)
        msg += await reader.read(1024)
        while(len(msg)>=18):
            size = int.from_bytes(msg[2:4], 'little')
            packet = msg[:18+size]
            packet = ecoflow_recieve.decode_packet(packet)
            if ecoflow_recieve.is_pd(packet[0:3]):
                pd = ecoflow_recieve.parse_pd(packet[3],product_id)
                print("PD:",pd)
            elif ecoflow_recieve.is_bms(packet[0:3]):
                bms = ecoflow_recieve.parse_bms(packet[3],product_id)
                print("BMS:",bms)
            elif ecoflow_recieve.is_dc_in_current_config(packet[0:3]):
                dic = ecoflow_recieve.parse_dc_in_current_config(packet[3])
                print("DC IN CONFIG:",dic)
            elif ecoflow_recieve.is_dc_in_type(packet[0:3]):
                dit = ecoflow_recieve.parse_dc_in_type(packet[3])
                print("DC IN TYPE:",dit)
            elif ecoflow_recieve.is_ems(packet[0:3]):
                ems = ecoflow_recieve.parse_ems(packet[3],product_id)
                print("EMS:",ems)
            elif ecoflow_recieve.is_fan_auto(packet[0:3]):
                fa = ecoflow_recieve.parse_fan_auto(packet[3])
                print("FAN AUTO:",fa)
            elif ecoflow_recieve.is_inverter(packet[0:3]):
                inv = ecoflow_recieve.parse_inverter_delta(packet[3])# TODO what about River!!
                print("INVERTER:",inv)
            elif ecoflow_recieve.is_lcd_timeout(packet[0:3]):
                lcd = ecoflow_recieve.parse_lcd_timeout(packet[3])
                print("LCD TIMEOUT:",lcd)
            elif ecoflow_recieve.is_mppt(packet[0:3]):
                mppt = ecoflow_recieve.parse_mppt(packet[3],product_id)
                print("MPPT:",mppt)
            else:
                print(packet)
            msg = msg[18+size:]
        await asyncio.sleep(10)

async def main():
    server = await asyncio.start_server(
        handle, '0.0.0.0', 6500)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())