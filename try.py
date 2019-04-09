import socketserver, http.server,  requests,sys

PORT_server = 8050
server = 'http://rest.ensembl.org'
ENDPOINTS = ['/info/species?', '/info/assembly', '/overlap/region/human/X:140424943-140624564?feature=gene', '/xrefs/symbol/homo_sapiens/{}', '/sequence/id/{}?expand=1']
headers = {"Content-Type": "application/json"}
socketserver.TCPServer.allow_reuse_address = True


ext = ENDPOINTS[3].format('afdsfsdfsds')
r = requests.get(server + ext, headers=headers)

if not r.ok:
    print('frthwhuuhuf')

decoded = r.json()
print(decoded)
print(str(decoded))
print(type(decoded))

