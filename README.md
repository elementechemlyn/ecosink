# "Fake" Server for EcoFlow Portable Power Stations

This provides a server for Ecoflow power stations to comminucate with instead of the Ecoflow Internet servers. This allows use of the local API without sending data to the Internet.

It relies on running a local DNS server which is able to direct the addresses:

 - tcp.ecoflow.com
 - tcp.ecoflow.com.wswebpic.com

to an address on the LAN which is running this server.

It has been tested with a Delta Mini that has been previosuly connected to the Internet. It has not been testing with a device which has never been conected to the ecoflow servers.

All the server does is allow the power station to connect, send data and requests a PD packet every 10 seconds - which is enough to convince the power station it is online and to enable it's local API.

Once enabled the local API can be used by things like this:

https://github.com/vwt12eh8/hassio-ecoflow

# Credits

A large portion of this code is taken from the Ecoflow HASS plugin project:

https://github.com/vwt12eh8/hassio-ecoflow
