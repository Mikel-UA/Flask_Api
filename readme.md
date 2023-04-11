# Flask API con Pandas y Numpy

Note: The purpose of the project is to use the Pandas and numpy libraries, which are unnecessary and in no case represent an improvement over the base python functions that we would apply in this case.

## Índice

- [Flask API con Pandas y Numpy](#Flask_API_con_Pandas_y_Numpy)
  - [Índice](#Índice)
  - [Instalación](#Instalación)
  - [Uso](#Uso)
  - [Excepciones](#Excepciones)
  - [Tests](#Tests)

## Instalación

Dado que se trata de una aplicación Flask basada en Uvicorn, basta con lanzar el comando siguiente:

``` flask --app app run ```

## Uso

Uvicorn permite que la app se actualice automáticamente en cuanto detecta cambios gracias a Watchfiles, por lo que no es necesario su reinicio una vez está levantada.  

Por defecto la URL a la que se accede es Localhost:
``` http://127.0.0.1:5000/{endpoint} ```

La primera petición, **symbol**,  que se debe realizar es la encargada de almacenar los datos en una variable global, para que el resto de la aplicación tenga contexto sobre la ```currency``` a utilizar.
```http://127.0.0.1:5000/symbol/BTC-USD```

Una vez la currency ha sido almacenada, se puede acceder al resto de endpoints indistintamente

El endpoint **bid_statistics** devolverá distintos datos calculados relacionados con las "pujas" de la currency solicitada. 
```http://127.0.0.1:5000/bid_statistics```

El endpoint **ask_statistics** devolverá distintos datos calculados relacionados con las "peticiones de compra" de la currency solicitada. 
```http://127.0.0.1:5000/ask_statistics```

Por último, **general_statistics** devolverá cálculos referentes al contenido de los dos endpoints anteriores.
```http://127.0.0.1:5000/general_statistics```

## Excepciones

Para controlar posibles errores y funcionamientos erráticos se ha implementado una excepción genérica llamada ```InvalidCurrencyException```, la cual devuelve un mensaje informando del fallo ocurrido.

## Tests

Se ha incluido una batería de tests unitarios basados en Pytest, ejecutable mediante el comando:
```Pytest testapp.py```

No se llega al 100% de cobertura dado que las funciones ```bid_statistics, ask_statistics y general_statistics``` no pueden ser comprobadas correctamente.
Dado que no se ha indicado nada referente a la base de datos se ha guardado todo en memoria, por lo que se ha utilizado la variable global ```CURRENCY``` lo cual
impide su ejecución como test, es por ello que se ha optado por una "programación defensiva".

