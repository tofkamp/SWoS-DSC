
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

hostname = "192.168.88.1"
username = "admin"
password = ""
has_POE = False


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

#from mikrotik_swos import mikrotik_poe
#poe = mikrotik_poe.Mikrotik_Poe(hostname,username,password)

from mikrotik_swos import mikrotik_snmp
snmp = mikrotik_snmp.Mikrotik_Snmp(hostname,username,password)
from mikrotik_swos import utils

mkttype = utils.decode_string(system._data["brd"])   # type
mktsid = utils.decode_string(system._data["sid"])  # serial nr
mktid = utils.decode_string(system._data["id"])   # naam ?
mktver = utils.decode_string(system._data["ver"])   # version
mktrev = utils.decode_string(system._data["rev"])   # revision
    
want_vlans = [
    { "name" : "beheer", "vlan_id" : 1 },
    { "name" : "werkstations", "vlan_id" : 4 },
    { "name" : "kantoor", "vlan_id" : 10 },
    { "name" : "publiek", "vlan_id" : 20 },
    { "name" : "OU", "vlan_id" : 50 },
    { "name" : "vmotion", "vlan_id" : 100 },
    { "name" : "vmkernel", "vlan_id" : 101 },
    { "name" : "Storage", "vlan_id" : 102 },
    { "name" : "Replication", "vlan_id" : 103 },
    { "name" : "Backup", "vlan_id" : 112 },
    { "name" : "Wifi", "vlan_id" : 201 },
    { "name" : "DMZ", "vlan_id" : 202 },
    { "name" : "wifi-AP", "vlan_id" : 220 },
    { "name" : "Test-ICT", "vlan_id" : 254 }
  ]
access_ports = [
      {
        "interface" : 1,
        "name"      : "sophos kan",
        "vlan_id"   : 10
      },
      {
        "interface" : 2,
        "name"      : "Kantoor",
        "vlan_id"   : 10
      },
      {
        "interface" : 3,
        "name"      : "sophos dmz",
        "vlan_id"   : 202
      },
      {
        "interface" : 4,
        "name"      : "publiek",
        "vlan_id"   : 20
      },
    ]
###### LACP bonding ports #######
bonding_ports = [
      {
        "interface1" : 11,
        "interface2" : 12,
        "name"       : "uplink2core",
        "vlans"      : [4, 10, 20, 50, 100, 101, 102, 103, 112, 201, 202, 220, 251, 254]
      },
    ]
###### Trunk ports ########
trunk_ports = [
  {
       "interface" : 9,
       "name"      : "bh3-k2-sw2",
       "vlans"     : [10, 20, 50, 100, 101, 201, 202, 220, 254]
     },
]
   
vlans.reset_member_cfg()    # remove all ports with vlan
dhcp_trusted_ports = []

vlans_defaults = { "port_isolation":False, "learning":True, "mirror": False, "igmp_snooping":False }
ports_defaults = { "enabled":True, "autoneg":True, "duplex":False, "tx_flow_control":True, "rx_flow_control":False }

def vlans_config(port, vlanss):
    for vlan in vlanss:
        if not vlans.get(vlan):   # does vlan exist ? no, create it
            vlans.add(vlan, name="VLAN {}".format(vlan), **vlans_defaults)
        vlans.add_port(vlan,port)

def ports_config(port,name):
    if ports._is_sfp_port(port):   # is there a sfp combo port ? then use that
        ports.configure(port, name=name, sfp_rate="high",combo_mode = "sfp", **ports_defaults)
    else:
        ports.configure(port, name=name, **ports_defaults)

def lacp_config(port,mode= "passive"):    # in future make it also work with static lacp groups
    lacp.port_lacp_mode(port, mode)

def forward_config(port, receive_mode, default_vlan_id=4090):
    forward.port_vlan_config(port, mode="strict",receive_mode = receive_mode, default_vlan_id = default_vlan_id, force_vlan_id = False)
   
for want in want_vlans:
    #print(want["vlan_id"],want["name"])
    vlans.add(want["vlan_id"],name = want["name"],**vlans_defaults)

if True:
    for access_port in access_ports:
        vlans_config(access_port["interface"], (access_port["vlan_id"],))
        ports_config(access_port["interface"], access_port["name"])
        lacp_config(access_port["interface"], mode = "passive")
        forward_config(access_port["interface"],receive_mode= "only untagged", default_vlan_id=access_port["vlan_id"])
else:
    for access_port in access_ports:
        #print(access_port["interface"],access_port["name"],access_port["vlan_id"])
        if ports._is_sfp_port(access_port["interface"]):
            ports.configure(access_port["interface"], name = "{interface} {name}".format(**access_port), enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0,sfp_rate="high",combo_mode = "sfp")
        else:
            ports.configure(access_port["interface"], name = "{interface} {name}".format(**access_port), enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0)
        vlans.add_port(access_port["vlan_id"],access_port["interface"])
        forward.port_vlan_config(access_port["interface"], mode="strict", receive_mode= "only untagged", default_vlan_id=access_port["vlan_id"],force_vlan_id = False)
        lacp.port_lacp_mode(access_port["interface"], mode = "passive")
if True:
    for trunk_port in trunk_ports:
        vlans_config(trunk_port["interface"], trunk_port["vlans"])
        ports_config(trunk_port["interface"], trunk_port["name"])
        lacp_config(trunk_port["interface"], mode = "passive")
        forward_config(trunk_port["interface"],receive_mode= "only tagged")
else:
    for trunk in trunk_ports:
        # check vlans
        for vlan in trunk["vlans"]:
            if not vlans.get(vlan):   # does vlan exist ? no, create it
                vlans.add(vlan, "VLAN {}".format(vlan), port_isolation=False, learning=True,mirror=False,igmp_snooping=False)
            vlans.add_port(vlan,trunk["interface"])
        if ports._is_sfp_port(trunk["interface"]):
            ports.configure(trunk["interface"],name = trunk["name"], enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0,sfp_rate="high",combo_mode = "sfp")
        else:
            ports.configure(trunk["interface"],name = trunk["name"], enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0)
        forward.port_vlan_config(trunk["interface"], mode = "strict", receive_mode = "only tagged", default_vlan_id = 2222, force_vlan_id = False)
        lacp.port_lacp_mode(trunk["interface"], mode = "passive")

if True:
    for bond_port in bonding_ports:   # in future iterate over interfaces
        vlans_config(bond_port["interface1"], bond_port["vlans"])
        ports_config(bond_port["interface1"], bond_port["name"])
        lacp_config(bond_port["interface1"], mode = "active")
        forward_config(bond_port["interface1"],receive_mode= "only tagged")
        vlans_config(bond_port["interface2"], bond_port["vlans"])
        ports_config(bond_port["interface2"], bond_port["name"])
        lacp_config(bond_port["interface2"], mode = "active")
        forward_config(bond_port["interface2"],receive_mode= "only tagged")

        dhcp_trusted_ports.append(bond_port["interface1"])
        dhcp_trusted_ports.append(bond_port["interface2"])
else:

    for bond in bonding_ports:
        for vlan in bond["vlans"]:
            if not vlans.get(vlan):   # does vlan exist ? no, create it
                vlans.add(vlan, name = "VLAN {}".format(vlan),port_isolation=False, learning=True,mirror=False,igmp_snooping=False)
                # or error "vlans does not exist"
            vlans.add_port(vlan,bond["interface1"])
            vlans.add_port(vlan,bond["interface2"])
        if ports._is_sfp_port(bond["interface1"]):
            ports.configure(bond["interface1"],name = bond["name"] + "1", enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0,sfp_rate="high",combo_mode = "sfp")
        else:
            ports.configure(bond["interface1"],name = bond["name"] + "1", enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0)
        dhcp_trusted_ports.append(bond["interface1"])
        
        if ports._is_sfp_port(bond["interface2"]):
            ports.configure(bond["interface2"],name = bond["name"] + "2", enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0,sfp_rate="high",combo_mode = "sfp")
        else:
            ports.configure(bond["interface2"],name = bond["name"] + "2", enabled=1,autoneg=1,duplex=0,tx_flow_control=1,rx_flow_control=0)
        dhcp_trusted_ports.append(bond["interface2"])
        
        forward.port_vlan_config(bond["interface1"], mode = "strict", receive_mode = "only tagged", default_vlan_id = 2222, force_vlan_id = False)
        forward.port_vlan_config(bond["interface2"], mode = "strict", receive_mode = "only tagged", default_vlan_id = 2222, force_vlan_id = False)
        lacp.port_lacp_mode(bond["interface1"], mode = "active")
        lacp.port_lacp_mode(bond["interface2"], mode = "active")

system.set(dhcp_add_information_option = False, identity="bh3-k1-sw6", dhcp_trusted_port = dhcp_trusted_ports)    # required if you use LAG, else you will be in trouble
           #allow_from_port = [] , igmp_fast_leave = [], discovery_protocol = [])


forward.save()
vlans.save()
ports.save()
system.save()
lacp.save()

"""
link COMBO ports
They can be SFP or copper
The "comb" contains which ports are combo ports (0x0f00) = port 9-12
"cm" selects the "Combo Mode"
auto = 0x00
copper = 0x01
sfp = 0x02
"sfpr" is the "SFP Rate Select"
low = 0x00
high = 0x01
"""
