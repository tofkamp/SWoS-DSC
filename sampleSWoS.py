
import requests
import json
from mikrotik_swos import utils

class SWOS:

    def _get(self, page):
        ret = requests.get(self._url + page, auth=self._auth)
        assert(ret.status_code == 200)
        return ret


    def __init__(self, url, login, password):
        if 'http://' not in url:
            self._url = "http://%s" % url
        else:
            self._url  = url
        self._auth = requests.auth.HTTPDigestAuth(login, password)
        self._data = ""
        self._page = ""

    def load_tab_data(self, page):
        self._page = page
        self._text = self._get(page).text
        self._data = utils.mikrotik_to_json(self._text)

    def show(self):
        print(self._data)

allinfo = {}
def writeout(tabje):
    allinfo[tabje._page] = { "text": tabje._text,
                             "data": tabje._data }
restapis = [ "/sys.b","/vlan.b","/link.b","/fwd.b","/lacp.b","/rstp.b","/host.b", "/acl.b","/snmp.b","/fan.b","/sfp.b","/stats.b","/poe.b"]

for api in restapis:
    print(api)
    #swos = SWOS("192.168.88.1","admin","")
    swos = SWOS("10.10.1.86","admin","gatvuln")
    swos.load_tab_data(api)
    #swos.show()
    writeout(swos)
    if api == "/sys.b":
        mkttype = utils.decode_string(swos._data["brd"])   # type
        mktsid = utils.decode_string(swos._data["sid"])  # serial nr
        #mktid = utils.decode_string(swos._data["id"])   # naam ?
        mktver = utils.decode_string(swos._data["ver"])   # version
        mktrev = utils.decode_string(swos._data["rev"])   # revision
        allinfo["board"] = mkttype
        allinfo["version"] = mktver
        allinfo["rev"] = mktrev

#swos = SWOS("192.168.88.1","admin","")
index_html = swos._get("/index.html")
allinfo["/index.html"] = index_html.text

filename = mkttype + "_" + mktrev + "_" + mktver +  "_" + mktsid + ".json" 
with open(filename, "w") as f:
    json.dump(allinfo, f, indent = 4)
print("Wrote info to",filename)
