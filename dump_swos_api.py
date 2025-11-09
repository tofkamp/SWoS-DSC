
#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

hostname = "192.168.88.1"
username = "admin"
password = ""
has_POE = False

allinfo = {}
def writeout(tabje):
    allinfo[tabje._page] = { "text": tabje._get(tabje._page).text,
                             "data": tabje._data }

from mikrotik_swos import mikrotik_system
system = mikrotik_system.Mikrotik_System(hostname,username,password)
writeout(system)
system.show()

from mikrotik_swos import mikrotik_vlans
vlans = mikrotik_vlans.Mikrotik_Vlans(hostname,username,password)
writeout(vlans)
vlans.show()

from mikrotik_swos import mikrotik_port
ports = mikrotik_port.Mikrotik_Port(hostname,username,password)
writeout(ports)
ports.show()

from mikrotik_swos import mikrotik_port_isolation
forward = mikrotik_port_isolation.Mikrotik_Forwarding(hostname,username,password)
writeout(forward)
forward.show()

from mikrotik_swos import mikrotik_lacp
lacp = mikrotik_lacp.Mikrotik_Lacp(hostname,username,password)
writeout(lacp)
lacp.show()

from mikrotik_swos import mikrotik_rstp
rstp = mikrotik_rstp.Mikrotik_Rstp(hostname,username,password)
writeout(rstp)
rstp.show()

if has_POE:
    from mikrotik_swos import mikrotik_poe
    poe = mikrotik_poe.Mikrotik_Poe(hostname,username,password)
    writeout(poe)
    poe.show()

from mikrotik_swos import mikrotik_snmp
snmp = mikrotik_snmp.Mikrotik_Snmp(hostname,username,password)
writeout(snmp)
snmp.show()

import json
from mikrotik_swos import utils

mkttype = utils.decode_string(system._data["brd"])   # type
mktsid = utils.decode_string(system._data["sid"])  # serial nr
#mktid = utils.decode_string(system._data["id"])   # naam ?
mktver = utils.decode_string(system._data["ver"])   # version
mktrev = utils.decode_string(system._data["rev"])   # revision
allinfo["board"] = mkttype
allinfo["version"] = mktver
allinfo["rev"] = mktrev
filename = mkttype + "_" + mktrev + "_" + mktver +  "_" + mktsid + ".json" 
with open(filename, "w") as f:
    json.dump(allinfo, f, indent = 4)
print("Wrote info to",filename)
