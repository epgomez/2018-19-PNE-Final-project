import requests, sys

server = "http://rest.ensembl.org"
ext = "/info/species?"

r = requests.get(server + ext, headers={"Content-Type": "text/xml"})

if not r.ok:
    r.raise_for_status()
    sys.exit()

print(r.text)