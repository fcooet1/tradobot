# tradobot
Hola chotis. hay dos files en el repositorio, getmarket y getauth.
La api de Bittrex ofrece dos tipos de REST requests, public y authenticated.
getmarket es una rutina que hace un request publico: le pide a la APP informacion publica del mercado, en este caso el tipo de cambio de ethereum a bitcoin ('ETH-BTC')
getauth hace un request provado, que requiere authenticacion. en este caso pide el balance de mi cuenta, que obviamente no es publico.
Ambas rutinas se pueden modificar para hacer cualquiera de las operaciones necesarias para hacer una maquinita infernal del dinero.

Lo que tengo hecho hasta ahora en getmarket, es:

una funcion gnGetSTXData(a,b) que va Bittrex y le pide los valores de cambio de la moneda 'a' a moneda 'b'. te devuelve un vector que tiene: (fecha del request, bidrate, ask rate)
la fecha del request queda en formato unix epoch. los valores Ask y Bid son los valores de venta y compra del mercado. Bid es el menor, al que vendes y ask es el mayor, al que pagas.

una funcion fnDetectCue(a), donde 'a' es una lista con los valores del Awesome Oscilator. Esta usa los ultimos 3 valores de la lista AO para detectar pistas y decidir cuando comprar o vender, segun la estrategia de momentum del Bill Williams, que es la que he estado usando manualmente desde febrero con buenos resultados.

las siguientes dos funciones son para probar como anda la estregia y comprar o vender localmente con plata falsa definida localmente.

Despues el programa inicia. define las variables, imprime un verso y hace un loop de 34 iteraciones usando fnGetSTXData, donde recive datos de mercado del servidor de Bittrex, que es lo minimo que necesitas para empezar a armar tu Awesome Oscilator.

en el main, usa los 34 datos para armar el primer valor del AO y despues usa fnDetectCues para cachar cuando comprar o vender + condiciones obvias como no vender mas barato de lo que compraste. y ahi se queda, recibiendo datos, armando el oscilador, detectando cues y tratando de hacer transacciones cuando es convenite.

Tiene una funcion para cortar el ciclo con Ctrl+C, donde liquida todo lo que tienes y calcula el profit de la sesion.
