import socketserver, http.server, termcolor, requests,sys

PORT_server = 8050
server = 'http://rest.ensembl.org'
ENDPOINTS = ['/info/species?', '/info/assembly']
headers = {"Content-Type": "application/json"}
socketserver.TCPServer.allow_reuse_address = True


specie = '/' + input('enter: ')
chromo = '/' + input('chr: ')
ext = ENDPOINTS[1] + specie + chromo +'?'
print(server + ext + specie)

r = requests.get(server + ext, headers=headers)

if not r.ok:
    r.raise_for_status()
    sys.exit()

decoded = r.json()
print(decoded)