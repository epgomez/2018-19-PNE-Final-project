import socketserver, http.server, termcolor, requests

PORT_server = 8050
server = 'http://rest.ensembl.org'
ENDPOINTS = ['/info/species?']
headers = {"Content-Type": "application/json"}
socketserver.TCPServer.allow_reuse_address = True

html = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">    <title>{}</title></head><body><h3>{}</h3><pre>{}</pre><a href="/">Main page</a></body></html>'

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        global base_op, length
        termcolor.cprint(self.requestline, 'green')
        path = self.path

        if path == '/':
            with open('home.html', 'r') as f:
                info = f.read()
                resp = 200

        elif 'listSpecies' in path:
            resp = 200
            ext = ENDPOINTS[0]
            r = requests.get(server + ext, headers=headers)

            decoded = r.json()
            add = ''
            for i in range(len(decoded['species'])):
                add += 'Scientific name: {} \nCommon name: {}\n\n'.format(decoded['species'][i]['name'], decoded['species'][i]['common_name'])
            print(add)
            tytle = 'Species list'
            h = 'List of all the available species'
            info = html.format(tytle, h, add)

        else:
            resp = 404
            f = open('error.html', 'r')
            content = f.read()


        if resp == 404:
            self.send_response(resp)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(content)))
            self.end_headers()

        else:
            d = open('response.html', 'w')
            d.write(info)
            d.close()
            d = open('response.html', 'r')
            content = d.read()
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
