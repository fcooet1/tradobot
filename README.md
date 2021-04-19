# tradobot
Hola chotis. hay dos files en el repositorio, getmarket y getauth.
La api de Bittrex ofrece dos tipos de REST requests, public y authenticated.
getmarket es una rutina que hace un request publico: le pide a la APP informacion publica del mercado, en este caso el tipo de cambio de ethereum a bitcoin ('ETH-BTC')
getauth hace un request privado, que requiere authenticacion. en este caso pide el balance de mi cuenta, que obviamente no es publico.
Ambas rutinas se pueden modificar para hacer cualquiera de las operaciones necesarias para hacer una maquinita infernal del dinero.

Lo que tengo hecho hasta ahora en getmarket, es:

una funcion gnGetSTXData(a,b) que va Bittrex y le pide los valores de cambio de la moneda 'a' a moneda 'b'. te devuelve un vector que tiene: (fecha del request, bidrate, ask rate). la fecha del request queda en formato unix epoch. los valores Ask y Bid son los valores de venta y compra del mercado. Bid es el menor, al que vendes y ask es el mayor, al que compras.

una funcion fnDetectCue(a), donde 'a' es una lista con los valores del Awesome Oscilator. Esta usa los ultimos 3 valores de la lista AO para detectar pistas y decidir cuando comprar o vender, segun la estrategia de momentum del Bill Williams, que es la que he estado usando manualmente desde febrero con buenos resultados (subi un excel con un simulador visual, apretas F9 y genera charts randomizados, mostrando el oscilador y donde ocurren los cues).

las siguientes dos funciones son para probar como anda la estregia y comprar o vender localmente con plata falsa definida localmente.

Despues el programa inicia. define las variables, imprime un verso y hace un loop usando fnGetSTXData, donde recive datos de mercado del servidor de Bittrex, hace 34 iteraciones que es lo minimo que necesitas para empezar a armar tu Awesome Oscilator.

en el main, usa los 34 datos para armar el primer valor del AO y despues usa fnDetectCues para cachar cuando comprar o vender + condiciones obvias como no vender mas barato de lo que compraste. y ahi se queda, recibiendo datos, armando el oscilador, detectando cues y tratando de hacer transacciones cuando es convenite.

Tiene una funcion para cortar el ciclo con Ctrl+C, donde liquida todo lo que tienes y calcula el profit de la sesion.


Despues getauth, es solo un ejemplo para cumplir con el protocolo de autenticacion de Bittrex para hacer requests privados. Te pide generar signatures formateados y encriptados de forma especifica y el codigo lo hace:
defines el url de donde vas a hacer el request (en este caso la base de datos de balances), le pones las keys que te dan en tu cuenta, el metodo que vas a usar en tu request (GET si vas a pedir informasion, PUT si vas a modificar alguna wea, etc), timestamp calcula la hora local en formato UNIX epoch milisegundos. request body es el pedaso de codigo que tenis que mandar para hacer un PUT request. en este caso es blank porque no necesitas mandar parametros para pedir un balance. El protocolo de bittrex te pide que lo encriptes en hash 512 y lo pases hexadecimal.  Despues para la autenticacion tienes que mandar una firma, que es una concatenacion de (timestamp+URL+method+request body encriptado), encriptada con hash512, usando la KEY que te pasan en tu cuenta y pasada a hexadecimal.
Finalmente, mandas el request a la URL de balances y le plantas los datos de autenticacion que son Tu API Key, el time stamp, el body content encriptado y la firma y te devuelve los datos de balance de tu cuenta.
