import socketserver
from practice.TestHandler import TestHandler

PORT_server = 8050
PORT_client = 80
HOSTNAME = 'rest.ensembl.org'
METHOD = "GET"
ENDPOINTS = []

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
