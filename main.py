from http.server import HTTPServer, BaseHTTPRequestHandler
import db
from errors import *
from urllib.parse import parse_qs, urlparse
import re, json

def basic_errors_handler(func):
    def wrapper(self, *args, **kwargs):
        try: 
            return func(self, *args, **kwargs)
        except APIError as e:
            self.send_json_response(e.code,{"error":e.message})
        except Exception as e:
            print(str(e))
            self.send_json_response(500, {"error":"Server Error"})
    return wrapper

class MyHandler(BaseHTTPRequestHandler):
    def send_json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    @basic_errors_handler
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        exchange_params = parse_qs(parsed_url.query)

        if path == '/currencies':
            answer = db.get_all_currencies()

                
        elif path.startswith('/currency'):
            mask = r'/currency/[A-Za-z][A-Za-z][A-Za-z]'
            if re.search(mask, self.path):
                currency_code = self.path.split('/')[-1].upper()
                answer = db.get_currency_by_code(currency_code)
                if answer == None:
                    raise NotFound("Валюта не найдена")
            else: 
                raise BadRequest("Код валюты отсутствует в адресе")

        elif path == '/exchangeRates':
            answer = db.get_all_exchangeRates()

        elif path.startswith('/exchangeRate'):
            base_currency = self.path.split('/')[-1][:3]
            target_currency = self.path.split('/')[-1][3:]
            mask = r'/exchangeRate/[A-Za-z][A-Za-z][A-Za-z][A-Za-z][A-Za-z][A-Za-z]'
            if re.search(mask, self.path): 
                answer = db.get_exchangeRates_by_codes(base_currency, target_currency)
                if answer == None: raise NotFound('Обменный курс для пары не найден')
            else: raise BadRequest("Коды валют пары отсутствуют в адресе")

        elif path =='/exchange':
            answer = db.exchange(exchange_params.get('from',[None])[0],exchange_params.get('to',[None])[0],exchange_params.get('amount',[None])[0])

        self.send_json_response(200, answer)

    @basic_errors_handler
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        currency_data = parse_qs(post_data)

        if self.path == '/currencies':
            if not all(k in currency_data.keys() for k in ['name', 'code', 'sign']):
                raise BadRequest("Отсутствует нужное поле формы")
            if db.get_currency_by_code(currency_data.get('code',[None])[0]) != None:
                raise ConflictError('Валюта с таким кодом уже существует')
            db.add_currency(currency_data)
            answer = db.get_currency_by_code(currency_data.get('code',[None])[0])

        elif self.path == '/exchangeRates':
            if len(currency_data) !=3:
                raise BadRequest("Отсутствует нужное поле формы")
            
            if db.get_exchangeRates_by_codes(currency_data.get('baseCurrencyCode',[None])[0],currency_data.get('targetCurrencyCode',[None])[0]) != None:
                raise ConflictError('Валютная пара с таким кодом уже существует')
            
            if db.get_currency_by_code(currency_data.get('baseCurrencyCode',[None])[0]) == None or db.get_currency_by_code(currency_data.get('targetCurrencyCode',[None])[0]) == None:
                raise NotFound("Одна (или обе) валюта из валютной пары не существует в БД")
            
            db.add_exchangeRate(currency_data.get('baseCurrencyCode',[None])[0],currency_data.get('targetCurrencyCode',[None])[0],currency_data.get('rate',[None])[0])
            answer = db.get_exchangeRates_by_codes(currency_data.get('baseCurrencyCode',[None])[0],currency_data.get('targetCurrencyCode',[None])[0])
        
        self.send_json_response(201,answer)

    @basic_errors_handler
    def do_DELETE(self):
        if self.path.startswith('/currency'):
            db.delete_currency_by_code(self.path.split('/')[-1])
            self.send_json_response(200,{'status':'succes'})

    @basic_errors_handler
    def do_PATCH(self):
        if self.path.startswith('/exchangeRate'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            currency_data = parse_qs(post_data)
            if len(currency_data) != 1:
                raise BadRequest('Отсутствует нужное поле формы')
            base_currency = self.path.split('/')[-1][:3]
            target_currency = self.path.split('/')[-1][3:]
            if db.get_exchangeRates_by_codes(base_currency, target_currency) == None:
                raise NotFound("Валютная пара отсутствует в базе данных")
            
            answer = db.update_exchangeRates(base_currency, target_currency, currency_data.get('rate', [None])[0])
            self.send_json_response(200, answer)

host_name = "localhost"
server_port = 8000

web_server = HTTPServer((host_name,server_port), MyHandler)

try:
    web_server.serve_forever()
except KeyboardInterrupt:
    print("STOP")

web_server.server_close()