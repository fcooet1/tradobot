#!/usr/bin/python
#fcooet1 APR 2021
import requests,json,time,sys, hashlib,hmac
def fnSavetoLedger(entry):
	with open('ledgerREAL.txt','a') as filehandle:
		filehandle.write('%s\n' %entry)

def fnGetBalance(a):
	sym=str(a)
	URL = 'https://api.bittrex.com/v3/balances'
	method='GET'
	timestamp = str(int(time.time()*1000))
	requestbody = ''
	ach = hashlib.sha512(requestbody.encode()).hexdigest()
	presignature=timestamp+URL+method+ach
	signature=hmac.new(APISECRET.encode(),presignature.encode(),digestmod=hashlib.sha512).hexdigest()
	rauth=requests.get(URL,headers={'Api-Key': str(APIKEY), 'Api-Timestamp': timestamp, 'Api-Content-Hash': ach, 'Api-Signature': signature})
	if str(rauth)!='<Response [200]>':
		print('Authentication failed. The progream will close.')
		input()
		exit()
	rauth=rauth.json()
	cash=[]
	for cur in rauth:
		if str(cur['currencySymbol'])==a:
			cash.append([str(cur['currencySymbol']),float(cur['available'])])
	return cash

def fnPlaceOrder(direction,qty,price):
	URL = 'https://api.bittrex.com/v3/orders'
	method='POST'
	timestamp = str(int(time.time()*1000))
	requestbody = {
   	 "marketSymbol": str(coina)+"-"+str(coinb),
   	 "direction": str(direction),
    	"type":  "LIMIT",
    	"quantity": str(qty),
    	"limit": str(price),
   	 "timeInForce": "FILL_OR_KILL"
	}
	ach = hashlib.sha512(bytes(json.dumps(requestbody),"utf-8")).hexdigest()
	presignature=timestamp+URL+method+ach
	signature=hmac.new(APISECRET.encode(),presignature.encode(),digestmod=hashlib.sha512).hexdigest()
	rauth=requests.post(URL,json=requestbody,headers={'Api-Key': str(APIKEY), 'Api-Timestamp': timestamp, 'Api-Content-Hash': ach, 'Api-Signature': signature})
	return(str(rauth))

def fnFee():
	URL = 'https://api.bittrex.com/v3/account/volume'
	method='GET'
	timestamp = str(int(time.time()*1000))
	requestbody = ''
	ach = hashlib.sha512(requestbody.encode()).hexdigest()
	presignature=timestamp+URL+method+ach
	signature=hmac.new(APISECRET.encode(),presignature.encode(),digestmod=hashlib.sha512).hexdigest()
	rauth=requests.get(URL,headers={'Api-Key': str(APIKEY), 'Api-Timestamp': timestamp, 'Api-Content-Hash': ach, 'Api-Signature': signature})
	if str(rauth)!='<Response [200]>':
		print('Authentication failed. The progream will close.')
		input()
		exit()
	rauth=rauth.json()
	bittrexcommision=[[5000,0.0075,0.0075],[10000,0.005,0.005],[25000,0.0035,0.0035],
                  [50000,0.002,0.002],[1000000,0.0012,0.0018],[10000000,0.0005,0.0015],
                  [60000000,0.0002,0.001],[60000000,0.0,0.0008],[100000000,0.0,0.0005]]
	fee=0.0
	for i in reversed(range(len(bittrexcommision))):
		if float(rauth['volume30days'])<=bittrexcommision[i][0]:
			fee=float(bittrexcommision[i][1])
	return fee

def fnGetSTXData(a, b):
	r=requests.get('https://api.bittrex.com/v3/markets/'+a+'-'+b+'/ticker')
	l=float(r.json()['bidRate'])
	h=float(r.json()['askRate'])
	return([int(time.time()), l, h])

def fnDetectCue(a):
	#Nough cross
	if len(a)>1:
		if a[-1]>0 and a[-2]<=0:
			#NX Cue: Buy
			return 0
		if a[-1]<0 and a[-2]>=0:
			#NX Cue: Sell
			return 1
	#Saucers
	if len(a)>2:
		if a[-1]>0 and a[-2]>0 and a[-3]>0 and a[-1]>a[-2] and a[-3]>a[-2] and a[-4]>a[-3]:
			#Saucer Cue: Buy
			return 0 
		if a[-1]<0 and a[-2]<0 and a[-3]<0 and a[-1]<a[-2] and a[-3]<a[-2] and a[-4]<a[-3]:
			#Saucer Cue: Sell
			return 1
	else:
		return 2

def fnBuy(m, p, f):
	fee= m*f
	g=(m-fee)/p
	answer='<Response [201]>'#fnPlaceOrder('BUY',g,p)  ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		print('*****************************************************')
		print("%s%.6f bought at $%.6f"%(coina,g, p))
		print('$%.5f fee paid'%fee)
		return g
	else:
		print("Server returned error %s. Transaction failed."%answer)
		return 0
def fnSell(g,p,f):
	fee=g*f
	m=(g-fee)*p
	answer='<Response [201]>'#fnPlaceOrder('SELL',g,p) ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		print('*****************************************************')
		print("%s%.6f sold at $%.6f"%(coina,g, p))
		print('$%.5f fee paid'%fee)
		return m
	else:
		print("Server returned error %s. Transaction failed."%answer)
		return 0
def main():
	try:
		global pricelist
		pricelist=[]
		global mid
		mid=[]
		global SMA5
		SMA5=[]
		global SMA34
		SMA34=[]
		global AO
		AO=[]
		global coina
		coina='BTC' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
		global coinb
		coinb='USDT' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
		global sessionfees
		sessionfees=[]
		global APIKEY
		global APISECRET
		APIKEY= '50950ac95b6347aea4748e23e78decb6'####YOUR APIKEY HERE####
		APISECRET= '79d9ae8ef14a4220b4c0e3767ff7475f'####YOUR APISECRET HERE####
		print()
		print('TRADOBOT v0.1 - Automatic trading on Bittrex Market by fcooet1')
		print('This bot uses Bill Williams AO Momentum strategy to trade automatically')
		print()

		if APIKEY=='' or APISECRET=='':
			print("APIKEY or APISECRET are missing. the program will end.")
			input()
			exit()
		BTCcash=float(fnGetBalance(coina)[-1][1])
		USDTcash=min(100,float(fnGetBalance(coinb)[-1][1]))
		global gfee
		gfee=fnFee()
		global startingpoint
		startingpoint=USDTcash
		global LP
		LP=float(0)
		

		r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/candles/TRADE/MINUTE_1/recent')
		rj=r.json()
		print('Current price is %.6f %s for 1%s' %(float(rj[-1]['high']),coinb,coina))
		print('Current available balance is:')
		print('%s%.6f'%(coinb,USDTcash))
		print('%s%.6f'%(coina,BTCcash))
		print('Press enter to start trading. Close compiler otherwise')
		input()

		print('Press Ctrl+C to stop the bot and recover your BTC at current market price')
		print()
		r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/candles/TRADE/MINUTE_1/recent')
		rj=r.json()
		for tik in rj:
			rjt=[int(time.time()),float(tik['low']),float(tik['high'])]
			pricelist.append(rjt)
			mid.append((pricelist[-1][2]+pricelist[-1][1]/2))
			if len(mid)>=5:
				SMA5.append(sum(mid[-5:])/5)
			if len(mid)>=34:
				SMA34.append(sum(mid[-34:])/34)
				AO.append(SMA5[-1]-SMA34[-1])
			sys.stdout.write("\rInitializing " +str(round(100*len(pricelist)/len(rj)))+'%')
			sys.stdout.flush()
		print()
		print()
		print("Waiting for Cues")
		print()
		while True:
			currenttime=int(time.time())
			pricelist.append(fnGetSTXData(coina, coinb))
			print(str(pricelist[-1]))
			mid.append((pricelist[-1][2]+pricelist[-1][1]/2))
			SMA5.append(sum(mid[-5:])/5)
			SMA34.append(sum(mid[-34:])/34)
			AO.append(SMA5[-1]-SMA34[-1])
			aux=fnDetectCue(AO)
			opp='none'
			if aux==1:
				#Sell 
				if LP/(1-gfee)**2<pricelist[-1][1] and BTCcash>0.00002:
					USDTcash=fnSell(BTCcash,pricelist[-1][1],gfee)
					BTCcash=float(fnGetBalance(coina)[-1][1])
					if BTCcash>0:
        					sessionfees.append(gfee*BTCcash)
					LP=999999999999.9
					gfee=fnFee()
					opp='sell'
					print("Current balance is %s%.6f" %(coinb,USDTcash))
					print()	
			if aux==0:
				#Buy
				if USDTcash>1.0:
					BTCcash=fnBuy(USDTcash,pricelist[-1][2],gfee)
					if BTCcash>0:
		        			sessionfees.append(gfee*BTCcash)
					USDTcash=min(100,float(fnGetBalance(coinb)[-1][1]))
					LP=pricelist[-1][2]
					gfee=fnFee()
					opp='buy'
					print("Current balance is %s%.6f" %(coinb,USDTcash))
					print()
			entry=[currenttime,pricelist[-1][1],pricelist[-1][2],AO[-1],aux,opp]
			fnSavetoLedger(entry)
			time.sleep(60)
	except KeyboardInterrupt:
		print('TRADOBOT has stoped')
		print()
		if BTCcash>0:
			USDTcash=fnSell(BTCcash,pricelist[-1][1])
			sessionfees.append(fee*BTCcash)
			LP=999999999999.9
			print("Current balance is %s%.6f" %(coinb,USDTcash))
			BTCcash=float(fnGetBalance(coina)[-1][1])
			print()
	else:
		print("Current balance is %s%.6f" %(coinb,USDTcash))
		print("%d transactions were made and %s%.6f was paid for fees" %(len(sessionfees),coinb, sum(sessionfees)))
		print("This session's profit was: %s%.8f" %(coinb,USDTcash-startingpoint))
##################################################
#######       Program Inizialization       #######
##################################################

if __name__=="__main__":
	main()