import time, requests, hashlib, hmac

URL = 'https://api.bittrex.com/v3/balances'
APIKEY = '' #api key here as str
APISECRET = ''#api secret here as str
method='GET'#GET, POST, HEADER, DEL depending on URL function
timestamp = str(int(time.time()*1000))
requestbody = ''#parameters to make a POST or HEAD requests, can be blank if no params required
ach = hashlib.sha512(requestbody.encode()).hexdigest()
presignature=timestamp+URL+method+ach
signature=hmac.new(APISECRET.encode(),presignature.encode(),digestmod=hashlib.sha512).hexdigest()

rauth=requests.get(URL,headers={'Api-Key': str(APIKEY), 'Api-Timestamp': timestamp, 'Api-Content-Hash': ach, 'Api-Signature': signature})
print(str(rauth.json()))
