# todo
# add poe to acces/trunk/bond struct ?
# system: add dhcp_trusted_ports allow_from_port , igmp_fast_leave and discovery_protocol to acces/trunk/bond struct ?
# commandline options
# dryrun
# documentation
# 

import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


import argparse
parser = argparse.ArgumentParser(description='Write a config to a mikrotik SWoS switch')
parser.add_argument('--hostname')
parser.add_argument('--configfile',required=True)
parser.add_argument('--password')
parser.add_argument('--has_POE', action='store_true', help='Set this if the switch supports POE')
parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

args = parser.parse_args()

filename = args.configfile
password = args.password if args.password else ""

import json
with open(filename, 'r') as file:
    data = json.load(file)

username = "admin"    # there is no other user
#password = data["password"]
if "hostname" in data:
    hostname = data["hostname"]
else:
    hostname = "192.168.88.1"
if args.hostname:
    hostname = args.hostname

if "has_POE" in data:
    has_POE = data["has_POE"]
else:
    has_POE = False
if args.has_POE:
    has_POE = args.has_POE

from mikrotik_swos import mikrotik_system
system = mikrotik_system.Mikrotik_System(hostname,username,password)
#system.show()
#system.set(allow_from_port = [1,2,3,4], dhcp_trusted_port  = [5,6,7,8], igmp_fast_leave = [9,10,11,12], mikrotik_discovery_protocol =[1,3,5,7])

from mikrotik_swos import mikrotik_vlans
vlans = mikrotik_vlans.Mikrotik_Vlans(hostname,username,password)

from mikrotik_swos import mikrotik_port
ports = mikrotik_port.Mikrotik_Port(hostname,username,password)

from mikrotik_swos import mikrotik_port_isolation
forward = mikrotik_port_isolation.Mikrotik_Forwarding(hostname,username,password)

from mikrotik_swos import mikrotik_lacp
lacp = mikrotik_lacp.Mikrotik_Lacp(hostname,username,password)

from mikrotik_swos import mikrotik_rstp
rstp = mikrotik_rstp.Mikrotik_Rstp(hostname,username,password)

if has_POE:
    from mikrotik_swos import mikrotik_poe
    poe = mikrotik_poe.Mikrotik_Poe(hostname,username,password)

from mikrotik_swos import mikrotik_snmp
snmp = mikrotik_snmp.Mikrotik_Snmp(hostname,username,password)
from mikrotik_swos import utils



mkttype = utils.decode_string(system._data["brd"])   # type
mktsid = utils.decode_string(system._data["sid"])  # serial nr
mktid = utils.decode_string(system._data["id"])   # naam ?
mktver = utils.decode_string(system._data["ver"])   # version
mktrev = utils.decode_string(system._data["rev"])   # revision
    
want_vlans = data["vlans"]
access_ports = data["access_ports"]
bonding_ports = data["bonding_ports"]
trunk_ports = data["trunk_ports"]
if "poe_ports" in data:
    poe_ports = data["poe_ports"]
else:
    poe_ports = []
   
vlans.reset_member_cfg()    # remove all ports with vlan
dhcp_trusted_ports = []

vlans_defaults = { "port_isolation":False, "learning":True, "mirror": False, "igmp_snooping":False }
ports_defaults = { "enabled":True, "autoneg":True, "duplex":False, "tx_flow_control":True, "rx_flow_control":False, "speed":1000 }
poe_defaults = { "priority" : 4, "lldp_enabled" : False }

def vlans_config(port, vlanss):
    for vlan in vlanss:
        if not vlans.get(vlan):   # does vlan exist ? no, create it
            #print(vlans_defaults)
            vlans.add(vlan, name="VLAN {}".format(vlan), **vlans_defaults)
        vlans.add_port(vlan,port)

def ports_config(port,name):
    if ports._is_combo_port(port):   # is there a sfp combo port ? then use that
        ports.configure(port, name=name, sfp_rate="high",combo_mode = "sfp", **ports_defaults)
    else:
        ports.configure(port, name=name, **ports_defaults)

def figureitout(parameters, defaultconfig):
    result_parameters = {}
    #print(parameters)
    #print(defaultconfig)
    for parameter in defaultconfig:
        #print(parameter)
        result_parameters[parameter] = parameters.get(parameter, defaultconfig[parameter])
    return result_parameters

def ports_config2(port,parameters):
    defaultconfig = ports_defaults.copy()
    if ports._is_combo_port(port):   # is there a sfp combo port ? then use that
        defaultconfig["sfp_rate"] = "high"
        defaultconfig["combo_mode"] = "sfp"
    if "name" in parameters:
        parameters["name"] = (str(port) + " " + parameters["name"])[:16]
    defaultconfig["name"] = "Port " + str(port)
    result_parameters = figureitout(parameters, defaultconfig)
    ports.configure(port, **result_parameters)
    
def lacp_config(port,mode= "passive"):    # in future make it also work with static lacp groups
    lacp.port_lacp_mode(port, mode)

def lacp_config2(port, defaultmode, parameters):
    defaultconfig = { "mode": defaultmode }
    if "mode" in parameters:
        if parameters["mode"] == "static":
            if "group_id" not in parameters:
                print("Port {}: Error, static LACP without group_id",format(port))
                return
            defaultconfig["group_id"] = 1  # will be overwritten because group_id is in parameters
    result_parameters = figureitout(parameters, defaultconfig)
    lacp.port_lacp_mode(port, **result_parameters)

def forward_config(port, receive_mode, default_vlan_id=4090):
    forward.port_vlan_config(port, mode="strict",receive_mode = receive_mode, default_vlan_id = default_vlan_id, force_vlan_id = False)

# maybe add the poe setting to the access/trunk/bond port ???
def poe_configure2(port, parameters):
    poe_defaults["poe_output"] = "off"
    result_parameters = figureitout(parameters, poe_defaults)
    poe.configure_port(port, **poe_defaults)

def poe_configure(port,poe_output):
    poe.configure_port(port, poe_output = poe_output, **poe_defaults)
    
for want in want_vlans:
    #print(want["vlan_id"],want["name"])
    defaultconfig = vlans_defaults
    #defaultconfig["name"] = "VLAN " + str(want["vlan_id"])  ##### doe het anders
    result_parameters = figureitout(want, defaultconfig)
    #vlans.add(want["vlan_id"],name = want["name"],**vlans_defaults)
    vlans.add(want["vlan_id"],**result_parameters)

for access_port in access_ports:
    vlans_config(access_port["interface"], (access_port["vlan_id"],))
    #ports_config(access_port["interface"], access_port["name"])
    ports_config2(access_port["interface"], access_port)
    #lacp_config(access_port["interface"], mode = "passive")
    lacp_config2(access_port["interface"], "passive", access_port)
    forward_config(access_port["interface"],receive_mode= "only untagged", default_vlan_id=access_port["vlan_id"])

# Trunk ports
for trunk_port in trunk_ports:
    #ports_config(trunk_port["interface"], trunk_port["name"])
    ports_config2(trunk_port["interface"], trunk_port)
    #lacp_config(trunk_port["interface"], mode = "passive")
    lacp_config2(trunk_port["interface"], "passive", trunk_port)
    if "untagged_vlan" in trunk_port:   # is it a hybrid trunk ?
        forward_config(trunk_port["interface"],receive_mode= "any",default_vlan_id = trunk_port["untagged_vlan"])
        trunk_port["vlans"].append(trunk_port["untagged_vlan"])
    else:  # normal trunk
        forward_config(trunk_port["interface"],receive_mode= "only tagged")
    vlans_config(trunk_port["interface"], trunk_port["vlans"])

# LACP LAG ports
for bond_port in bonding_ports:   # in future iterate over interfaces
    vlans_config(bond_port["interface1"], bond_port["vlans"])
    ports_config(bond_port["interface1"], bond_port["name"])
    #lacp_config(bond_port["interface1"], mode = "active")
    lacp_config2(bond_port["interface1"], "active", bond_port)

    if "untagged_vlan" in bond_port:   # is it a hybrid trunk ?
        forward_config(bond_port["interface1"],receive_mode= "any",default_vlan_id = bond_port["untagged_vlan"])
        bond_port["vlans"].append(bond_port["untagged_vlan"])
    else:  # normal trunk
        forward_config(bond_port["interface1"],receive_mode= "only tagged")
        
    #forward_config(bond_port["interface1"],receive_mode= "only tagged")
    ########## interface 2
    vlans_config(bond_port["interface2"], bond_port["vlans"])
    ports_config(bond_port["interface2"], bond_port["name"])
    #lacp_config(bond_port["interface2"], mode = "active")
    lacp_config2(bond_port["interface2"], "active", bond_port)
    if "untagged_vlan" in bond_port:   # is it a hybrid trunk ?
        forward_config(bond_port["interface2"],receive_mode= "any",default_vlan_id = bond_port["untagged_vlan"])
        #bond_port["vlans"].append(bond_port["untagged_vlan"])
    else:  # normal trunk
        forward_config(bond_port["interface2"],receive_mode= "only tagged")
    
    #forward_config(bond_port["interface2"],receive_mode= "only tagged")

    dhcp_trusted_ports.append(bond_port["interface1"])
    dhcp_trusted_ports.append(bond_port["interface2"])

if has_POE:
    for poe_port in poe_ports:
        poe_configure(int(poe_port), poe_ports[poe_port])
    
system.set(dhcp_add_information_option = False, identity = data["identity"], dhcp_trusted_port = dhcp_trusted_ports)    # required if you use LAG, else you will be in trouble
           #allow_from_port = [] , igmp_fast_leave = [], discovery_protocol = [])


forward.save()
vlans.save()
ports.save()
system.save()
lacp.save()
if has_POE:
    poe.save()

mkttype = utils.decode_string(system._data["brd"])   # type
mktsid = utils.decode_string(system._data["sid"])  # serial nr
mktid = utils.decode_string(system._data["id"])   # naam ?
mktver = utils.decode_string(system._data["ver"])   # version
mktrev = utils.decode_string(system._data["rev"])   # revision
print("Wrote Desired Switch Config to",mktid,mktver,mkttype,mktrev,mktsid)

