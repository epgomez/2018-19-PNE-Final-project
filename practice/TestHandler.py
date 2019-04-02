import http.server
import socketserver
import termcolor

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        global base_op, length
        termcolor.cprint(self.requestline, 'green')
        path = self.path

        if path == '/':
            with open('home.html', 'r') as f:
                content = f.read()
                resp = 200

        elif path[:12] == '/listSpecies':
            pass
