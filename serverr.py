import socketserver, http.server, requests, termcolor

PORT_server = 8000
server = 'http://rest.ensembl.org'
ENDPOINTS = ['/info/species?', '/info/assembly', '/overlap/region/human/{}:{}-{}?feature=gene','/xrefs/symbol/homo_sapiens/{}', '/sequence/id/{}?expand=1']
headers = {"Content-Type": "application/json"}
socketserver.TCPServer.allow_reuse_address = True

# this is the future html file that will be sent to the client
# It has blank spaces that will be filled later


html = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{}</title></head><body><h3>{}</h3><a href="/">Main page</a><pre>{}</pre><a href="/">Main page</a></body></html>'

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        print('Request: {}'.format(self.requestline))
        path = self.path

        try:
            if path == '/':
                # This is the first html file that is sent to the client
                with open('home.html', 'r') as f:
                    info = f.read()
                    resp = 200

            elif 'listSpecies' in path:

                resp = 200
                ext = ENDPOINTS[0]
                # Process the client's request using the request module
                r = requests.get(server + ext, headers=headers)
                decoded = r.json()

                # Limit to the length of the list selected by the user
                limit = path.split('=')[1]

                # If there is no limit, the limit used will be the species' list's length
                if limit == '':
                    limit = len(decoded['species'])
                add = ''

                # Add the common and the scientific name of all the species to the list
                for i in range(int(limit)):
                    add += 'Scientific name: {} \nCommon name: {}\n\n'.format(decoded['species'][i]['name'], decoded['species'][i]['common_name'])

                # The title of the html file is different in each case
                title = 'Species list'
                h = 'List of all the available species'

                # Include the information in the future html response text
                info = html.format(title, h, add)

            elif 'karyotype' in path:

                resp = 200
                species = path.split('=')[1]

                ext = ENDPOINTS[1] + '/' + species + '?'
                r = requests.get(server + ext, headers=headers)

                # In case that the specie's name is not on the database
                # the client will recieve a response message indicating so
                if r.ok:
                    decoded = r.json()
                    add = ''
                    if decoded['karyotype'] == []:
                        add = "This species' karyotype is not stored in the database"
                    else:
                        # Add all the chromosomes to the list, avoiding the one called "MT",
                        # which is a parameter used by the database itself
                        for i, elem in enumerate(decoded['karyotype']):
                            if elem == 'MT':
                                continue
                            add += 'Chromosome number {}: {}\n'.format(str(i+1), elem)
                else:
                    add = 'Can not find internal name for species "{}"'.format(species)

                # Like before, I include the title myself
                title = 'Karyotype'
                h = 'Karyotype of {}'.format(path.split('=')[1])
                info = html.format(title, h, add)

            elif 'chromosomeLength' in path:

                resp = 200
                # In this case, I receive two mandatory endpoints: "species" and "chromo"
                species = path.split('&')[0].split('=')[1]
                chromo = path.split('&')[1].split('=')[1]
                # Process the request
                ext = ENDPOINTS[1] + '/'+ species + '/'+ chromo + '?'
                r = requests.get(server + ext , headers=headers)

                if r.ok:
                    decoded = r.json()
                    add = decoded['length']
                else:
                    add = 'Can not find chromosome {} of species {}'.format(chromo,species)

                # Include the information in my future html file
                title = 'Chromosome lenght'
                h = 'Lenght of the {} chromosome of {}'.format(chromo, species)
                info = html.format(title, h, add)

            elif 'geneSeq' in path:

                resp = 200
                chromo = path.split('=')[1]

                ext = ENDPOINTS[3].format(chromo)
                r1 = requests.get(server + ext, headers=headers)

                if r1.ok:
                    decoded1 = r1.json()


            elif 'geneList' in path:

                resp = 200
                chromo = path.split('&')[0].split('=')[1]
                start = path.split('&')[1].split('=')[1]
                end = path.split('&')[2].split('=')[1]

                ext = ENDPOINTS[2].format(chromo, start, end)
                r = requests.get(server + ext, headers=headers)

                if r.ok:
                    decoded = r.json()
                    add = ''
                    for i in range(len(decoded)):
                        add += 'Gene {}: {}\n'.format(i, decoded[i]['external_name'])
                else:
                    add = 'No slice found for location {}:{}-{}'.format(chromo, start, end)

                title = 'Gene list'
                h = 'Gene list of chromosome {} from {} to {}'.format(chromo, start, end)
                info = html.format(title, h, add)

            else:
                # In the case that I get an endpoint different from the ones I have decided to use,
                # the client recieves an error message
                resp = 404
                f = open('error.html', 'r')
                info = f.read()

        except:
            # If an exception is raised, I send back an error message
            resp = 404
            f = open('error.html', 'r')
            info = f.read()

        # Write the information in a response html file
        d = open('response.html', 'w')
        d.write(info)
        d.close()

        # Read the information form that response html file
        d = open('response.html', 'r')
        content = d.read()
        d.close()

        # Send the headers and the response html
        self.send_response(resp)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(content)))
        self.end_headers()

        self.wfile.write(str.encode(content))


Handler = TestHandler

# Open the socket server
with socketserver.TCPServer(("", PORT_server), Handler) as httpd:
    print("Serving at PORT: ", PORT_server)

    # Main loop: Attend the client. Whenever there is a new
    # client, the handler is called
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stoped by the user")
        httpd.server_close()