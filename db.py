import sqlite3, json

def create_table_Currencies():
    with sqlite3.connect('currencies.db') as connection:
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS currencies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    sign TEXT NOT NULL
);
        ''')

def add_base_records_to_Currencies():
    with sqlite3.connect('currencies.db') as connetion:
        cursor = connetion.cursor()
        cursor.execute('''INSERT INTO currencies (id, name, code, sign) VALUES
(0, 'United States dollar', 'USD', '$'),
(1, 'Euro', 'EUR', '€'),
(2, 'Japanese yen', 'JPY', '¥'),
(3, 'Pound sterling', 'GBP', '£'),
(4, 'Chinese yuan', 'CNY', '¥'),
(5, 'Australian dollar', 'AUD', '$'),
(6, 'Canadian dollar', 'CAD', '$'),
(7, 'Swiss franc', 'CHF', 'Fr'),
(8, 'Hong Kong dollar', 'HKD', '$'),
(9, 'Singapore dollar', 'SGD', '$');''')


def create_table_ExchangeRates():
    with sqlite3.connect('currencies.db') as connection:
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS ExchangeRates (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    BaseCurrencyId INTEGER NOT NULL,
    TargetCurrencyId INTEGER NOT NULL,
    Rate DECIMAL(10, 6) NOT NULL,
    

    FOREIGN KEY (BaseCurrencyId) REFERENCES currencies(id),
    FOREIGN KEY (TargetCurrencyId) REFERENCES currencies(id),
    

    UNIQUE (BaseCurrencyId, TargetCurrencyId)
);''')

def add_base_records_to_ExchangeRates():
    with sqlite3.connect('currencies.db') as connetion:
        cursor = connetion.cursor()
        cursor.execute('''INSERT INTO ExchangeRates (BaseCurrencyId, TargetCurrencyId, Rate) VALUES
(0, 1, 0.954201),
(0, 2, 152.345000),
(0, 3, 0.812340),
(0, 4, 7.284500),
(0, 5, 1.582300),
(0, 6, 1.412000),
(0, 7, 0.901200),
(0, 8, 7.821000),
(0, 9, 1.365400),
(1, 0, 1.048000),
(2, 0, 0.006564),
(3, 0, 1.231000); ''')
        
def get_all_currencies():
    with sqlite3.connect('currencies.db') as connetion:
        cursor = connetion.cursor()
        cursor.execute('''SELECT * FROM currencies''')
        table = cursor.fetchall()

        mass = list()
        for row in table:
            mass.append({
                "id": row[0],
                "name": row[1],
                "code": row[2],
                "sign": row[3]
            })
        return json.dumps(mass)
    
def get_currency_by_code(code):
    with sqlite3.connect('currencies.db') as connetion:
        cursor = connetion.cursor()
        cursor.execute('''SELECT * FROM currencies WHERE code = ?''', (code,))
        table = cursor.fetchall()
        mass = list()
        for row in table:
            mass.append({
                "id": row[0],
                "name": row[1],
                "code": row[2],
                "sign": row[3]
            })
        return json.dumps(mass)
    
def add_currency(currency_data):
    with sqlite3.connect('currencies.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO currencies (id, name, code, sign) VALUES ((SELECT max(id)+1 FROM currencies), ?,?,?)''', (*currency_data['name'],*currency_data['code'],*currency_data['sign'],))
    
def delete_currency_by_code(code):
    with sqlite3.connect('currencies.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''DELETE FROM currencies WHERE code = ?''', (code,))

def get_all_exchangeRates():
    with sqlite3.connect('currencies.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM (
            SELECT 
            ExchangeRates.ID, 
            ExchangeRates.BaseCurrencyId, 
            ExchangeRates.TargetCurrencyId, 
            ExchangeRates.Rate, 
            currencies.id AS t_id, 
            currencies.name AS t_name, 
            currencies.code AS t_code, 
            currencies.sign AS t_sign 
            FROM ExchangeRates 
            INNER JOIN currencies ON currencies.id = ExchangeRates.TargetCurrencyId) as ER INNER JOIN currencies ON currencies.id = ER.BaseCurrencyId''')
        table = cursor.fetchall()
        mass = list()
        for row in table:
            mass.append({
                "id": row[0],
                "baseCurrency": {
                    "id": row[1],
                    "name": row[9],
                    "code": row[10],
                    "sign": row[11]
                },
                "targetCurrency": {
                    "id": row[2],
                    "name": row[5],
                    "code": row[6],
                    "sign": row[7]
                },
                "rate": row[3]
            })
        return json.dumps(mass)
    
def get_exchangeRates_by_codes(frm,to):
    with sqlite3.connect('currencies.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''SELECT * FROM (SELECT 
                            ExchangeRates.ID, 
                            ExchangeRates.BaseCurrencyId, 
                            ExchangeRates.TargetCurrencyId, 
                            ExchangeRates.Rate, 
                            currencies.id AS t_id, 
                            currencies.name AS t_name, 
                            currencies.code AS t_code, 
                            currencies.sign AS t_sign 
                        FROM ExchangeRates  
                        INNER JOIN currencies ON currencies.id = ExchangeRates.TargetCurrencyId) as ER 
                        INNER JOIN currencies ON currencies.id = ER.BaseCurrencyId WHERE t_code = ? AND code = ? ''', (to,frm,))
        table = cursor.fetchall()
        mass = list()
        for row in table:
            mass.append({
                "id": row[0],
                "baseCurrency": {
                    "id": row[1],
                    "name": row[9],
                    "code": row[10],
                    "sign": row[11]
                },
                "targetCurrency": {
                    "id": row[2],
                    "name": row[5],
                    "code": row[6],
                    "sign": row[7]
                },
                "rate": row[3]
            })
        return json.dumps(mass)
    
def update_exchangeRates(base_currency, target_currency, rate):
    with sqlite3.connect('currencies.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''update ExchangeRates set rate = ? 
                       where BaseCurrencyId = (select id from currencies where code = ?) 
                       and TargetCurrencyId = (select id from currencies where code = ?);''', (rate, base_currency, target_currency,))
        cursor.execute('''SELECT * FROM (SELECT 
                            ExchangeRates.ID, 
                            ExchangeRates.BaseCurrencyId, 
                            ExchangeRates.TargetCurrencyId, 
                            ExchangeRates.Rate, 
                            currencies.id AS t_id, 
                            currencies.name AS t_name, 
                            currencies.code AS t_code, 
                            currencies.sign AS t_sign 
                        FROM ExchangeRates  
                        INNER JOIN currencies ON currencies.id = ExchangeRates.TargetCurrencyId) as ER 
                        INNER JOIN currencies ON currencies.id = ER.BaseCurrencyId WHERE t_code = ? AND code = ? ''', (target_currency,base_currency,))
        
        table = cursor.fetchall()
        mass = list()
        for row in table:
            mass.append({
                "id": row[0],
                "baseCurrency": {
                    "id": row[1],
                    "name": row[9],
                    "code": row[10],
                    "sign": row[11]
                },
                "targetCurrency": {
                    "id": row[2],
                    "name": row[5],
                    "code": row[6],
                    "sign": row[7]
                },
                "rate": row[3]
            })
        return json.dumps(mass)
    
def exchange(frm, to, amount):
   exp = json.loads(get_exchangeRates_by_codes(frm,to))
   exp[-1].update({'amount': int(amount), "convertedAmount": int(amount)*exp[-1]['rate']})
   return json.dumps(exp)

if __name__ == '__main__':
    create_table_Currencies()
    add_base_records_to_Currencies()
    create_table_ExchangeRates()
    add_base_records_to_ExchangeRates()