import socketserver, http.server,requests, termcolor
from Seq import Seq

PORT_server = 8000
server = 'http://rest.ensembl.org'
ENDPOINTS = ['/info/species?', '/info/assembly', '/overlap/region/human/{}:{}-{}?feature=gene',
             '/xrefs/symbol/homo_sapiens/{}', '/sequence/id/{}?expand=1']
headers = {"Content-Type": "application/json"}

socketserver.TCPServer.allow_reuse_address = True

# this is the future html file that will be sent to the client
# It has blank spaces that will be filled later

html: str = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{}</title></head><body><h3>{}</h3><a href="/">Main page</a><pre>{}</pre><a href="/">Main page</a></body></html>'

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        termcolor.cprint(self.requestline, 'green')
        path = self.path
        end = path[1:path.find('?')]

        try:
            if path == '/':

                resp = 200
                # This is the first html file that is sent to the client
                with open('home.html', 'r') as f:
                    info = f.read()

            elif end == 'listSpecies':

                resp = 200
                ext = ENDPOINTS[0]
                # Process the client's request using the request module
                r = requests.get(server + ext, headers=headers)
                decoded = r.json()

                # Limit to the length of the list selected by the user
                try:
                    if 'json=1' in path:
                        # In case that the user hasn't introduced any limit while writing the URL in the browser
                        # otherwise, the limit will be established at 1
                        if 'limit' not in path:
                            limit = len(decoded['species'])
                        else:
                            limit = path.split('=')[1].split('&')[0]
                    else:
                        limit = path.split('=')[1]
                # In case that the user hasn't introduced any limit while writing the URL in the browser
                except IndexError:
                    limit = len(decoded['species'])

                # If there is no limit entered, the limit used will be the species' list's length
                if limit == '':
                    limit = len(decoded['species'])

                add = ''
                info_dict = {}
                limit_passed = False

                if int(limit) > 199:
                    # If the limit entered by the user is over 199,
                    # a warning message is sent back with the full list
                    add += '<pre style = "color: red">CAREFUL! The maximum length is 199!</pre>(We are showing the maximum number of species possible)\n\n'
                    limit = 199
                    limit_passed = True
                    # Add the common and the scientific name of all the species to the list
                for i in range(int(limit)):

                    # I add the information in form of a string in case the user wants it like that and in form of a
                    # dictionary if the user wants a json
                    common = decoded['species'][i]['common_name']
                    add += 'Scientific name: {} \nCommon name: {}\n\n'.format(decoded['species'][i]['name'], common)

                    # If there is a "'" character in the common name of an species, this would make the later
                    # replacement of "'" by '"' introduce an extra " that would make the json file impossible for the
                    # client to read, so if I detect one I skip it
                    if "'" in common:
                        common = common.replace("'", '')

                    info_dict.update([(str(i+1), {'common_name': common, 'scientific_name': decoded['species'][i]['name']})])

                if limit_passed:
                    info_dict.update([('0', {'CAREFUL!':'The maximum length is 199! (We are showing the maximum number of species possible)'})])

                info_dict = str(info_dict).replace("'", '"')
                # The title of the html file is different in each case
                title = 'Species list'
                h = 'List of all the available species'

                # Include the information in the future html response text
                info = html.format(title, h, add)

            elif end == 'karyotype' :

                resp = 200
                if 'json=1' in path:
                    species = path.split('=')[1].split('&')[0]
                else:
                    species = path.split('=')[1]

                ext = ENDPOINTS[1] + '/' + species + '?'
                r = requests.get(server + ext, headers=headers)

                # In case that the species' name is not on the database
                # the client will receive a response message indicating so
                info_dict = {}
                if r.ok:
                    decoded = r.json()
                    add = ''

                    if not decoded['karyotype']:
                        add = "This species' karyotype is not stored in the database"
                        info_dict.update([('error', 'This species karyotype is not stored in the database')])
                    else:
                        # Add all the chromosomes to the list, avoiding the one called "MT",
                        # which is a parameter used by the database itself
                        for i, elem in enumerate(decoded['karyotype']):
                            if elem == 'MT':
                                continue
                            add += 'Chromosome number {}: {}\n'.format(str(i + 1), elem)
                            info_dict.update([(str(i), elem)])
                else:
                    add = 'Can not find internal name for species "{}"'.format(species)
                    info_dict.update([('error', 'Can not find internal name for species {}'.format(species))])

                info_dict = str(info_dict).replace("'", '"')

                # Like before, I include the title myself
                title = 'Karyotype'
                h = 'Karyotype of {}'.format(path.split('=')[1])
                info = html.format(title, h, add)

            elif end == 'chromosomeLength' :

                resp = 200
                # In this case, I receive two mandatory endpoints: "species" and "chromo"
                if 'json=1' in path:
                    species = path.split('&')[0].split('=')[1].split('&')[0]
                    chromo = path.split('&')[1].split('=')[1].split('&')[0]
                else:
                    species = path.split('&')[0].split('=')[1]
                    chromo = path.split('&')[1].split('=')[1]
                # Process the request
                ext = ENDPOINTS[1] + '/' + species + '/' + chromo + '?'
                r = requests.get(server + ext, headers=headers)

                info_dict = {}
                if r.ok:
                    decoded = r.json()
                    add = decoded['length']
                    info_dict.update([('length', decoded['length'])])
                else:
                    add = 'Can not find chromosome "{}" of species "{}"'.format(chromo, species)
                    info_dict.update([('error', 'Can not find chromosome {} of species {}'.format(chromo, species))])

                info_dict = str(info_dict).replace("'", '"')

                # Include the information in my future html file
                title = 'Chromosome length'
                h = 'Length of chromosome {} of species {}'.format(chromo, species)
                info = html.format(title, h, add)

            elif end == 'geneSeq' or end == 'geneInfo' or end == 'geneCalc' :

                resp = 200
                if 'json=1' in path:
                    gene = path.split('=')[1].split('&')[0]
                else:
                    gene = path.split('=')[1]

                ext1 = ENDPOINTS[3].format(gene)
                info_dict = {}

                try:
                    r1 = requests.get(server + ext1, headers=headers)
                    # I get the ensembl ID in order to be able to search
                    decoded1 = r1.json()
                    id = decoded1[0]['id']

                    # Once I have the ID, i use it to find the information i need about this gene
                    ext2 = ENDPOINTS[4].format(id)
                    r2 = requests.get(server + ext2, headers=headers)
                    decoded2 = r2.json()

                    # Now a different response is returned depending on the request. The information is stored in form
                    # of string in the variable "add" and in form of dictionary in variable "info_dict"

                    if end == 'geneSeq':
                        add = decoded2['seq']
                        info_dict.update([('sequence', decoded2['seq'])])

                        title = 'Gene {} seq'.format(gene)
                        h = 'Sequence of gene {}'.format(gene)

                    elif end == 'geneInfo':
                        a = decoded2['desc'].split(':')
                        chromo, start, end, id, length = a[2], a[3], a[4], decoded2['id'], decoded2['id']

                        add = "Start: {}\nEnd:{}\nLength: {}\nid: {}\nChromosome: {}".format(start, end, length, id, chromo)
                        info_dict.update([('start', start), ('end', end), ('length', length), ('id', id), ('chromosome', chromo)])

                        title = 'Gene {} inf'.format(gene)
                        h = 'Information about gene {}'.format(gene)

                    elif end == 'geneCalc':
                        seq = Seq(decoded2['seq'])
                        length = seq.len()
                        perc = [seq.perc('A'), seq.perc('C'), seq.perc('T'), seq.perc('G')]

                        add = 'Length: {}\n  Percentage of A: {}%\n  Percentage of C: {}%\n  Percentage of T: {}%\n  Percentage of G: {}%'.format(length, perc[0], perc[1], perc[2], perc[3])
                        info_dict.update([('length', length), ('perc_A', perc[0] + '%'), ('perc_C', perc[1] + '%'),("perc_T", perc[2] + '%'), ("perc_G", perc[3] + '%')])

                        title = 'Gene {} calc'.format(gene)
                        h = 'Calculations performed on gene {}'.format(gene)

                except Exception:
                    # In case that the gene entered by the user is not stored in the database
                    add = 'There is no "{}" gene stored in the database'.format(gene)
                    info_dict.update([('error', 'There is no {} gene stored in the database'.format(gene))])
                    title = 'ERROR'
                    h = '<pre style = "color: red; font-size: 18px">Wrong name!</pre>'

                info_dict = str(info_dict).replace("'", '"')
                info = html.format(title, h, add)

            elif end == 'geneList':

                resp = 200

                # I get the chromosome and start and end points
                chromo = path.split('&')[0].split('=')[1]
                start = path.split('&')[1].split('=')[1]
                end = path.split('&')[2].split('=')[1]

                ext = ENDPOINTS[2].format(chromo, start, end)
                info_dict = {}
                try:
                    r = requests.get(server + ext, headers=headers)
                    decoded = r.json()
                    add = ''
                    for i in range(len(decoded)):
                        add += 'Gene {}: {}\n'.format(i, decoded[i]['external_name'])
                        info_dict.update([(str(i), decoded[i]['external_name'])])
                # In case the user has commited an error while requesting the slice
                except Exception:
                    add = 'No slice found for location {}:{}-{}'.format(chromo, start, end)
                    info_dict.update([('error', 'No slice found for location {}:{}-{}'.format(chromo, start, end))])

                info_dict = str(info_dict).replace("'", '"')

                title = 'Gene list'
                h = 'Gene list of chromosome {} from {} to {}'.format(chromo, start, end)
                info = html.format(title, h, add)

            else:
                # In the case that I get an endpoint different from the ones I have decided to use,
                # the client receives an error message
                resp = 404
                f = open('error.html', 'r')
                info = f.read()

        except Exception:
            # If an exception is raised, I send back an error message
            resp = 404
            f = open('hugeerror.html', 'r')
            info = f.read()

        # Write the information in a response html file
        d = open('response.html', 'w')
        d.write(info)
        d.close()

        # Read the information from that response html file
        d = open('response.html', 'r')
        content = d.read()
        d.close()

        content_type = 'text/html'

        if 'json=1' in path and resp == 200:
            content_type = 'application/json'
            content = info_dict

        # Send the headers and the response html
        self.send_response(resp)
        self.send_header('Content-Type', content_type)
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