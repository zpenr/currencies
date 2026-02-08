from http.server import HTTPServer, BaseHTTPRequestHandler
import db
from urllib.parse import parse_qs, urlparse
import re


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        exchange_params = parse_qs(parsed_url.query)

        if path == '/currencies':
            try:
                self.send_header("Content-type", "application/json")
                self.end_headers()
                answer = db.get_all_currencies()
                self.send_response(200)
                self.wfile.write(answer.encode("utf-8"))
                
            except:
                self.send_response(500)

        elif path.startswith('/currency'):
            try:
                self.send_header("Content-type", "application/json")
                self.end_headers()
                mask = r'/currency/[A-Za-z][A-Za-z][A-Za-z]'
                if re.search(mask, self.path):
                    currency_code = self.path.split('/')[-1].upper()
                    answer = db.get_currency_by_code(currency_code)
                    try:
                        self.wfile.write(answer.encode("utf-8"))
                        self.send_response(200)
                    except:
                        self.send_response(404)
                else: 
                    self.send_response(400)
            except:
                self.send_response(500)

        elif path == '/exchangeRates':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            answer = db.get_all_exchangeRates()
            self.wfile.write(answer.encode("utf-8"))

        elif path.startswith('/exchangeRate'):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            base_currency = self.path.split('/')[-1][:3]
            target_currency = self.path.split('/')[-1][3:]
            answer = db.get_exchangeRates_by_codes(base_currency, target_currency)
            self.wfile.write(answer.encode("utf-8"))

        elif path =='/exchange':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            answer = db.exchange(*exchange_params['from'],*exchange_params['to'],*exchange_params['amount'])
            self.wfile.write(answer.encode("utf-8"))

            
    def do_POST(self):
        if self.path == '/currencies':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            currency_data = parse_qs(post_data)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            db.add_currency(currency_data)
            answer = db.get_currency_by_code(*currency_data['code'])
            self.wfile.write(answer.encode("utf-8"))

    def do_DELETE(self):
        if self.path.startswith('/currency'):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            db.delete_currency_by_code(self.path.split('/')[-1])

    def do_PATCH(self):
        if self.path.startswith('/exchangeRate'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            currency_data = parse_qs(post_data)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            base_currency = self.path.split('/')[-1][:3]
            target_currency = self.path.split('/')[-1][3:]
            answer = db.update_exchangeRates(base_currency, target_currency, *currency_data['rate'])
            self.wfile.write(answer.encode('utf-8'))

host_name = "localhost"
server_port = 8000

web_server = HTTPServer((host_name,server_port), MyHandler)

try:
    web_server.serve_forever()
except KeyboardInterrupt:
    print("STOP")

web_server.server_close()