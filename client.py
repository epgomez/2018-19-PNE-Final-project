import requests

server = 'http://rest.ensembl.org'
ENDPOINTS = ['/info/species?', '/info/assembly', '/overlap/region/human/{}:{}-{}?feature=gene',
             '/xrefs/symbol/homo_sapiens/{}', '/sequence/id/{}?expand=1']

headers = {"Content-Type": "application/json"}

ENDPOINT = ENDPOINTS[2].format('1','0','100000')
r = requests.get(server + ENDPOINT, headers=headers)
decoded = r.json()

print(decoded)