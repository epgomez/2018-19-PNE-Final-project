import requests

server = 'http://localhost:8000'
ENDPOINTS = ['/listSpecies?limit=&json=1', '/listSpecies?json=1',
             '/listSpecies?limit=7&json=1','/listSpecies?limit=3333&json=1',
             '/karyotype?specie=human&json=1', '/karyotype?specie=blabla&json=1',
             '/chromosomeLength?specie=human&chromo=X&json=1',
             '/chromosomeLength?specie=human&chromo=q&json=1',
             '/geneSeq?gene=FRAT1&json=1','/geneSeq?gene=FRAT13&json=1',
             '/geneInfo?gene=FRAT1&json=1', '/geneInfo?gene=FRAT13&json=1',
             '/geneCalc?gene=FRAT1&json=1', '/geneCalc?gene=FRAT13&json=1',
             '/geneList?chromo=X&start=0&end=3000000&json=1',
             '/geneList?chromo=X&start=0&end=300000e&json=1']

headers = {"Content-Type": "application/json"}

for i in ENDPOINTS:
    ENDPOINT = i
    r = requests.get(server + ENDPOINT, headers=headers)
    decoded = r.json()

    print(decoded)