import asyncio

import ecoflow
import ecoflow_send
import time

init_1 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x02\x01\x41\x62\xe0" #SERIAL (2, 1, 65, b'')
init_2 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x0b\x01\x41\xb2\xe2" #SERIAL (11, 1, 65, b'')

data_req1 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x02\x20\x02\x3b\x41" #PD  (2, 32, 2, b'')
data_req2 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x02\x01\x05\x62\xd3" #(2, 1, 5, b'')
data_req3 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x03\x20\x02\x6a\x81" #EMS (3, 32, 2, b'')
data_req4 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x03\x01\x05\x33\x13" # (3, 1, 5, b'')
data_req5 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x04\x20\x02\xdb\x40" #INVERTER (4, 32, 2, b'')
data_req6 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x04\x01\x05\x82\xd2" # (4, 1, 5, b'')
data_req7 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x05\x20\x02\x8a\x80" #MPPT (5, 32, 2, b'')
data_req8 = b"\xaa\x02\x00\x00\xb5\x0d\x00\x00\x00\x00\x00\x00\x20\x05\x01\x05\xd3\x12" # (5, 1, 5, b'')


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
        packet = ecoflow.decode_packet(packet)
        if ecoflow.is_serial_main(packet[0:3]):
            serial = ecoflow.parse_serial(packet[3])
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
            packet = ecoflow.decode_packet(packet)
            if ecoflow.is_pd(packet[0:3]):
                pd = ecoflow.parse_pd(packet[3],product_id)
                print("PD:",pd)
            elif ecoflow.is_bms(packet[0:3]):
                bms = ecoflow.parse_bms(packet[3],product_id)
                print("BMS:",bms)
            elif ecoflow.is_dc_in_current_config(packet[0:3]):
                dic = ecoflow.parse_dc_in_current_config(packet[3])
                print("DC IN CONFIG:",dic)
            elif ecoflow.is_dc_in_type(packet[0:3]):
                dit = ecoflow.parse_dc_in_type(packet[3])
                print("DC IN TYPE:",dit)
            elif ecoflow.is_ems(packet[0:3]):
                ems = ecoflow.parse_ems(packet[3],product_id)
                print("EMS:",ems)
            elif ecoflow.is_fan_auto(packet[0:3]):
                fa = ecoflow.parse_fan_auto(packet[3])
                print("FAN AUTO:",fa)
            elif ecoflow.is_inverter(packet[0:3]):
                inv = ecoflow.parse_inverter_delta(packet[3])# TODO what about River!!
                print("INVERTER:",inv)
            elif ecoflow.is_lcd_timeout(packet[0:3]):
                lcd = ecoflow.parse_lcd_timeout(packet[3])
                print("LCD TIMEOUT:",lcd)
            elif ecoflow.is_mppt(packet[0:3]):
                mppt = ecoflow.parse_mppt(packet[3],product_id)
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