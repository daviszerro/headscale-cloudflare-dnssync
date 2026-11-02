import requests, json
import ipaddress
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from termcolor import colored

### Get Data
def getTailscaleDevice(apikey, clientid, clientsecret, tailnet):
    if clientid and clientsecret:
        token = OAuth2Session(client=BackendApplicationClient(client_id=clientid)).fetch_token(token_url='https://api.tailscale.com/api/v2/oauth/token', client_id=clientid, client_secret=clientsecret)
        apikey = token["access_token"]
    url = "https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices".format(tailnet=tailnet)
    payload={}
    headers = {
    }
    response = requests.request("GET", url, headers=headers, data=payload, auth=HTTPBasicAuth(username=apikey, password=""))
    # print(response.text)
    # print(json.dumps(json.loads(response.text), indent=2))

    output=[]

    data = json.loads(response.text)
    if (response.status_code == 200):
        output = []
        # 仅同步本 Tailnet 自有设备，并以 Tailscale 管理的设备名称作为 DNS 名称来源。
        #
        # device['hostname'] 是客户端上报的操作系统主机名，可能包含空格、下划线，也可能是 localhost 等重复名称。
        # 原实现同时同步 hostname 和 name，导致多台设备共用 localhost.ts.*，甚至产生无效的 DNS 记录。
        #
        # device['name'] 是 Tailscale 管理的设备 DNS 名称，取第一个标签作为短主机名。
        # 跳过 isExternal 设备，避免将他人共享进来的节点发布到自己的 DNS 域；
        # 跳过空名称，防止生成 .ts.example.com 这样的非法记录。
        #
        # 取舍：不再为操作系统 hostname 创建额外别名，统一以 Tailscale 设备名称为准。
        # 设备重命名后，旧名称对应的记录将由后续 stale cleanup 清理。
        for device in data['devices']:
            if device.get('isExternal'):
                continue

            name = (device.get('name') or '').split('.')[0].lower()
            if not name:
                continue

            for address in device['addresses']:
                output.append({
                    'hostname': alterHostname(name),
                    'address': address
                })
        return output
    else:
        exit(colored("getTailscaleDevice() - {status}, {error}".format(status=str(response.status_code), error=data['message']), "red"))

def isTailscaleIP(ip):
    ip = ipaddress.ip_address(ip)

    if (ip.version == 6):
        if (ip in ipaddress.IPv6Network('fd7a:115c:a1e0::/48')):
            return True
        else:
            return False
    elif (ip.version == 4):
        if (ip in ipaddress.IPv4Network('100.64.0.0/10')):
            return True
        else:
            return False
    else:
        exit("isTailscaleIP(): - unknown IP version")

def alterHostname(hostname):
    from config import getConfig
    config = getConfig()
    pre = config.get("prefix", "")
    post = config.get("postfix", "")

    newHostname = "{pre}{hostname}{post}".format(pre=pre, post=post, hostname=hostname)
    return newHostname

if __name__ == '__main__':
    print(json.dumps(getTailscaleDevice(), indent=2))
