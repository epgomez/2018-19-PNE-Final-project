import socketserver, http.server, termcolor, requests,sys

PORT_server = 8050
server = 'http://rest.ensembl.org'
ENDPOINTS = ['/info/species?', '/info/assembly', '/overlap/region/human/7:140424943-140624564?feature=gene']
headers = {"Content-Type": "application/json"}
socketserver.TCPServer.allow_reuse_address = True


ext = ENDPOINTS[2]
print(server + ext)

r = requests.get(server + ext, headers=headers)

if not r.ok:
    r.raise_for_status()
    sys.exit()

decoded = r.json()


add = {}
for i in range(len(decoded)):
    add.update([(str(i), decoded[i]['external_name'])])

print(add)

