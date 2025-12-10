# emulate swos switch

import json
switch = "CRS312-4C+8XG_r2_2.18_HE208JZZ6YZ"
#switch="CRS354-48P-4S+2Q+_r4_2.18_HJP0AGA6JTB"

with open(f"Samples/{switch}.json") as fp:
    switch_data = json.load(fp)

with open("scraper/index.html") as fp:
    index_html = fp.read()

from bottle import route, run, request 

#app = Bottle(debug=True)

@route('/')
@route('/index.html')
def indexhtml():
    return switch_data["/index.html"]

@route('/sys.b')
def sys_b():
    return switch_data["/sys.b"]["text"]

@route('/acl.b')
def acl_b():
    return switch_data["/acl.b"]["text"]

@route('/sfp.b')
def sfp_b():
    return switch_data["/sfp.b"]["text"]

@route('/fan.b')
def fan_b():
    return switch_data["/fan.b"]["text"]

@route('/vlan.b')
def vlan_b():
    return switch_data["/vlan.b"]["text"]

@route('/link.b')
def link_b():
    return switch_data["/link.b"]["text"]

@route('/fwd.b')
def fwd_b():
    return switch_data["/fwd.b"]["text"]

@route('/lacp.b')
def lacp_b():
    return switch_data["/lacp.b"]["text"]

@route('/stats.b')
def stats_b():
    return switch_data["/stats.b"]["text"]

@route('/rstp.b')
def rstp_b():
    return switch_data["/rstp.b"]["text"]

@route('/snmp.b')
def snmp_b():
    return switch_data["/snmp.b"]["text"]

@route('/poe.b')
def poe_b():
    return switch_data["/poe.b"]["text"]

@route('/sys.b', method='POST')
@route('/vlan.b', method='POST')
@route('/fwd.b', method='POST')
@route('/link.b', method='POST')
@route('/lacp.b', method='POST')
def do_post():
    print("Pre",switch_data[request.path]["text"])
    switch_data[request.path]["text"] = request.body.getvalue()
    print("Post",switch_data[request.path]["text"],"\n\n")
    #print(request.body.getvalue())
    return "Yeah post"

run(host='localhost', port=80,debug=True, reloader=True)
