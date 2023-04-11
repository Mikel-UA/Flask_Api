from exceptions import InvalidCurrencyException
from flask import Flask
import pandas as pd
import numpy as np
import requests
import re


app = Flask(__name__)

CURRENCY = None

@app.route('/symbol/<user_curr>')
def symbol(user_curr):
    """
    Endpoint que acepta un símbolo de moneda introducido por el usuario como parámetro. 
    Si el símbolo de moneda coincide con un patrón regex de una moneda base y una contra-moneda, 
    envía una petición GET a una API externa para recuperar una lista de símbolos de moneda, 
    y utiliza el paquete Pandas para transformar los datos en un DataFrame. A continuación, 
    comprueba si el símbolo de moneda introducido por el usuario coincide con algún símbolo del
    DataFrame y envía otra petición GET a la API para recuperar información sobre la moneda. 
    Si el símbolo de la divisa es válido, establece una variable global y devuelve la respuesta. 
    Si el símbolo de moneda no es válido, lanza una excepción personalizada.
    """

    if re.match('^[A-Z]{3,8}-[A-Z]{3,8}$', user_curr):
        symbols = requests.get('https://api.blockchain.com/v3/exchange/symbols')
        symbols = symbols.json()
        
        df = pd.DataFrame.from_dict(pd.json_normalize(symbols.values()), orient='columns')
        
        base_curr, counter_curr = user_curr.split('-')

        x = df.apply(lambda x: 1 if x.base_currency == base_curr and x.counter_currency == counter_curr else 0, axis=1)
        if (x.eq(1)).any():
            print("Correct currency")
            response = requests.get('https://api.blockchain.com/v3/exchange/l3/{}'.format(user_curr))
            response = response.json()
            global CURRENCY 
            CURRENCY = user_curr
            return response
        else:
            raise InvalidCurrencyException(message = "Currency does not exist")
    else:
        raise InvalidCurrencyException(message = "Currency symbol does not match regex requirements")
    



@app.route('/bid_statistics')
def bid_statistics():
    """
     Endpoint que recupera estadísticas de pujas para una divisa específica enviando una petición GET 
     a una API externa. Los datos de las pujas se transforman en un DataFrame de Pandas, 
     que se utiliza para calcular los valores medio, mayor y menor de las pujas.

     El valor medio se calcula utilizando el método mean, que toma la columna value del DataFrame 
     El valor mayor se calcula encontrando la fila con el valor más alto 
     en la columna valor utilizando el método idxmax y recuperando el valor de esa fila. 
     Del mismo modo, el valor menor se calcula encontrando la fila con el valor más bajo en la columna 
     de valor utilizando el método idxmin y recuperando el valor de esa fila.

     El precio total y la cantidad total de las pujas se calculan utilizando el método sum, 
     que toma las columnas px y qty del DataFrame, respectivamente, y calcula su suma. 
     Las estadísticas de las pujas se devuelven como un objeto JSON que contiene las estadísticas calculadas.
    """
    
    if CURRENCY is None:
        raise InvalidCurrencyException(message = "Currency symbol is not set")
    else:
        response = requests.get('https://api.blockchain.com/v3/exchange/l3/{}'.format(CURRENCY))
        response = response.json()

        print(response)
        df = pd.DataFrame.from_dict(pd.json_normalize(response['bids']), orient='columns')
        df['value'] = df['px'] * df['qty']

        greater_value = df.loc[df['value'].idxmax()]['value']
        lesser_value = df.loc[df['value'].idxmin()]['value']
        average_value = df['value'].mean(axis = 0, skipna = False)

        total_px = df['px'].sum()
        total_qty = df['qty'].sum()

        response_json = {
            "bids": {
                "average_value": average_value,
                "greater_value": greater_value,
                "lesser_value": lesser_value,
                "total_qty": total_qty,
                "total_px": total_px
                }
            }
        return response_json



@app.route('/ask_statistics')
def ask_statistics():
    """
     Endpoint que recupera estadísticas de pujas para una divisa específica enviando una petición GET
     A continuación, utiliza pandas para convertir la respuesta en un marco de datos y añade una nueva 
     columna llamada "valor", que es el producto de las columnas "px" (precio) y "qty" (cantidad).

     El df se ordena por la columna "valor" y las variables "valor_menor" y "valor_mayor" se 
     establecen como primer y último valor de la columna "valor", respectivamente. 
     La variable "valor_medio" se establece como la media de la columna "valor" utilizando numpy.

     Por último, la función calcula el precio y la cantidad totales de todos los "asks" y 
     los almacena en las variables "total_px" y "total_qty", respectivamente. 
     Estas estadísticas se devuelven en formato JSON como diccionario bajo la clave "asks".
    """

    if CURRENCY is None:
        raise InvalidCurrencyException(message = "Currency symbol is not set")
    else:
        response = requests.get('https://api.blockchain.com/v3/exchange/l3/{}'.format(CURRENCY))
        response = response.json()

        print(response)
        df = pd.DataFrame.from_dict(pd.json_normalize(response['asks']), orient='columns')
        df['value'] = df['px'] * df['qty']
        df = df.sort_values(by=['value'])

        lesser_value = df['value'].iloc[0]
        greater_value = df['value'].iloc[-1]
        average_value = np.mean(df['value'], axis=0)

        total_px = sum(map(lambda x: int(x['px']), response['asks']))
        total_qty = sum(map(lambda x: int(x['qty']), response['asks']))

        response_json = {
            "asks": {
                "average_value": average_value,
                "greater_value": greater_value,
                "lesser_value": lesser_value,
                "total_qty": total_qty,
                "total_px": total_px
                }
            }
        return response_json

@app.route('/general_statistics')
def general_statistics():
    """
    Endpoint que devuelve estadísticas generales sobre pujas y peticiones de compra de la API, 
    basadas en el símbolo de moneda especificado en la variable CURRENCY.  
    El código calcula cantidad total y el valor de ofertas y demandas directamente sobre el json,
    y devuelve los calculos en el mismo formato. Si la variable CURRENCY no está definida, 
    se producirá una InvalidCurrencyException.
    """
    if CURRENCY is None:
        raise InvalidCurrencyException(message = "Currency symbol is not set")
    else:
        response = requests.get('https://api.blockchain.com/v3/exchange/l3/{}'.format(CURRENCY))
        response = response.json()
        
        bids_count = len(response['bids'])
        asks_count = len(response['asks'])

        total_asks_px = sum(map(lambda x: int(x['px']), response['asks']))
        total_asks_qty = sum(map(lambda x: int(x['qty']), response['asks']))

        total_bids_px = sum(map(lambda x: int(x['px']), response['bids']))
        total_bids_qty = sum(map(lambda x: int(x['qty']), response['bids']))

        response_json = {
            CURRENCY: {
            "bids": {
                "count": bids_count,
                "qty": total_bids_qty,
                "value": total_bids_px*total_bids_qty
            },
            "asks": {
                "count": asks_count,
                "qty": total_asks_qty,
                "value": total_asks_px*total_asks_qty
            }
            }
        }

        return response_json

if __name__ == '__main__':
    app.run(debug=True) 