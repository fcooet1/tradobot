#!/usr/bin/python
#fcooet1 APR 2021

import requests,json,time,sys,hashlib,hmac,uuid

def fnSavetoLedger(entry,startdate):
	with open('ledger_'+str(startdate)+'.txt','a') as filehandle:
		filehandle.write('%s\n' %entry)

def fnGetLastOrder(id):
	URL = 'https://api.bittrex.com/v3/orders/closed'
	method='GET'
	timestamp = str(int(time.time()*1000))
	requestbody = ''
	ach = hashlib.sha512(requestbody.encode()).hexdigest()
	presignature=timestamp+URL+method+ach
	signature=hmac.new(APISECRET.encode(),presignature.encode(),digestmod=hashlib.sha512).hexdigest()
	rauth=requests.get(URL,headers={'Api-Key': str(APIKEY), 'Api-Timestamp': timestamp, 'Api-Content-Hash': ach, 'Api-Signature': signature})
	if str(rauth)!='<Response [200]>':
		print('Authentication failed.'+str(rauth)+' The progream will close.')
		input()
		exit()
	while str(rauth.json()[0]['clientOrderId'])!=id:
		sleep(1)
		timestamp = str(int(time.time()*1000))
		presignature=timestamp+URL+method+ach
		signature=hmac.new(APISECRET.encode(),presignature.encode(),digestmod=hashlib.sha512).hexdigest()
		rauth=requests.get(URL,headers={'Api-Key': str(APIKEY), 'Api-Timestamp': timestamp, 'Api-Content-Hash': ach, 'Api-Signature': signature})
		if str(rauth)!='<Response [200]>':
			print('Authentication failed while getting order info.'+str(rauth)+' The progream will close.')
			input()
			exit()
	return [float(rauth.json()[0]['proceeds']),float(rauth.json()[0]['commission']),float(rauth.json()[0]['fillQuantity'])]		
		
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
		print('Authentication failed while getting account balances.'+str(rauth)+' The progream will close.')
		input()
		exit()
	rauth=rauth.json()
	cash=[]
	for cur in rauth:
		if str(cur['currencySymbol'])==sym:
			cash.append([str(cur['currencySymbol']),float(cur['available'])])
	if len(cash)!=0:
		return cash
	else:
		return [[a,0.0]]

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
   		"timeInForce": "FILL_OR_KILL",
		}
	ach = hashlib.sha512(bytes(json.dumps(requestbody),"utf-8")).hexdigest()
	presignature=timestamp+URL+method+ach
	signature=hmac.new(APISECRET.encode(),presignature.encode(),digestmod=hashlib.sha512).hexdigest()
	rauth=requests.post(URL,json=requestbody,headers={'Api-Key': str(APIKEY), 'Api-Timestamp': timestamp, 'Api-Content-Hash': ach, 'Api-Signature': signature})
	if str(rauth)==('<Response [201]>' or '<Response [409]>') :
		return(str(rauth))
	else:
		print('Authentication failed while placing order.'+str(rauth)+' The progream will close.')
		input()
		exit()
		
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
		print('Authentication failed while accesing account info.'+str(rauth)+' The progream will close.')
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
	if str(r)!='<Response [200]>':
		print('Server not responding.'+str(r)+'  The progream will close.')
		input()
		exit()
	l=float(r.json()['bidRate'])
	h=float(r.json()['askRate'])
	return([int(time.time()), l, h])

def fnDetectCue(a):
	#Positive Peak
	if len(a)>4:
		if a[-1]>0 and a[-2]>0 and a[-3]>0 and a[-4] and a[-1]<a[-2] and a[-2]<a[-3] and a[-3]>a[-4]:
			#PP Cue: Sell
			return 1
	#Nough cross
	if len(a)>1:
		if a[-1]>0 and a[-2]<=0:
			#NX Cue: Buy
			return 0
		if a[-1]<0 and a[-2]>=0:
			#NX Cue: Sell
			return 1
	#Saucers
	if len(a)>4:
		if a[-1]>0 and a[-2]>0 and a[-3]>0 and a[-1]>a[-2] and a[-3]>a[-2] and a[-4]>a[-3]:
			#Saucer Cue: Buy
			return 0 
		if a[-1]<0 and a[-2]<0 and a[-3]<0 and a[-1]<a[-2] and a[-3]<a[-2] and a[-4]<a[-3]:
			#Saucer Cue: Sell
			return 1

def fnBuy(m, p):
	g=m*(1-gfee)/p
	answer='<Response [201]>'#fnPlaceOrder('BUY',g,p)  ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		print('*****************************************************')
		print("%s%.6f bought at $%.6f"%(coina,g, p))
		print("Amount spent on transaction was %s%.6f + a %s%.6f fee" %(coinb,m,coinb,m*gfee))
		return g
	else:
		print("Server returned error %s. Transaction failed."%answer)
		return 0
	
def fnSell(g, p):
	answer='<Response [201]>'#fnPlaceOrder('SELL',g,p) ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		print('*****************************************************')
		print("%s%.6f sold at $%.6f"%(coina,g, p))
		m=g*p*(1-gfee)
		print("Transaction profit was %s%.6f (%.6f fee was paid)" %(coinb,m-g*LP,g*p*gfee))
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
		global coinb
		global sessionfees
		sessionfees=[]
		global sessionprofit
		sessionprofit=0.0
		global APIKEY
		global APISECRET
		global gfee
		global LP
		
		coina='' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
		coinb='' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
		LP=float(0) #enter here the minimum price at which you want to sell available BTC. If you decide to not use available BTC leave it at 0.
		
		APIKEY= ''####YOUR APIKEY HERE####
		APISECRET= ''####YOUR APISECRET HERE####
		
		print()
		print('TRADOBOT v0.1 - Automatic trading on Bittrex Market by fcooet1.')
		print('This bot uses Bill Williams Momentum strategy to trade automatically.')
		if APIKEY=='' or APISECRET=='':
			print("APIKEY or APISECRET are missing. The program will end.")
			input()
			exit()
		gfee=fnFee()
		r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/candles/TRADE/MINUTE_1/recent')
		rj=r.json()
		print('Current price is %.6f %s for 1%s.' %(float(rj[-1]['high']),coinb,coina))
		print('Current available balance is:')
		print('%s%.6f'%(coinb,float(fnGetBalance(coinb)[-1][1])))
		print('%s%.6f'%(coina,float(fnGetBalance(coina)[-1][1])))
		if float(fnGetBalance(coina)[-1][1])>0.0:
			print('Use available %s? Y/N' %coina)
			auxqstn=''
			while auxqstn!=('y' or 'Y' or 'n' or 'N'):
				auxqstn=str(input())
				if auxqstn==('y' or 'Y'):
					coinacash=float(fnGetBalance(coina)[-1][1])
					maxcoina=0.0
				if auxqstn==('n' or 'N'):
					coinacash=0.0
					maxcoina=float(fnGetBalance(coina)[-1][1])
		else:
			coinacash=0.0
		print('Input maximum %s amount to take from your account when trading.' %coinb)
		global maxtrad
		maxtrad=float(input())
		while maxtrad>=float(fnGetBalance(coinb)[-1][1]):
			print('Insuficient funds.')
			maxtrad=float(input())	
		print('Input %s amount to start trading with.' %coinb)
		auxcash=float(input())
		while auxcash>=float(fnGetBalance(coinb)[-1][1]):
			print('Insuficient funds.')
			auxcash=float(input())
		coinbcash=auxcash
		global startingpoint
		r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/candles/TRADE/MINUTE_1/recent')
		rj=r.json()
		startdate=int(time.time())
		print('Press Ctrl+C anytime to stop the bot.')
		print('A ledger file will be saved containing all session info. Check README to understand ledger data.')
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
		print("Tradobot will now wait for market Cues each passing minute. Transactions will be displayed when made.")
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
			if aux==1:#Sell
				if LP/(1-gfee)**2<pricelist[-1][1] and coinacash>0:
					auxsell=coinbcash
					coinbcash=fnSell(coinacash,pricelist[-1][1])
					if coinbcash==0:
						coinbcash=auxsell
					if coinbcash!=0:
						sessionfees.append(coinacash*pricelist[-1][1]*gfee)
						sessionprofit+=coinbcash-coinacash*LP
						LP=999999999999.9
						coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
						gfee=fnFee()
						opp='sell'
						coinbcash=maxtrad
					coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
					print()	
			if aux==0:#Buy
				if coinbcash>0:
					auxbuy=coinacash
					coinacash=fnBuy(coinbcash,pricelist[-1][2])
					if coincash==0:
						coinacash=auxbuy
						coinbcash=maxtrad
					if coinacash>0:
						sessionfees.append(coinbcash*gfee)
						LP=pricelist[-1][2]
						gfee=fnFee()
						opp='buy'
						coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
						coinbcash=0.0
					print()
			entry=[time.ctime(currenttime),pricelist[-1][1],pricelist[-1][2],AO[-1],aux,opp,LP]
			fnSavetoLedger(entry,startdate)
			time.sleep(currenttime+60-time.time())
	except KeyboardInterrupt:
		print()
		print('TRADOBOT has stoped')
		print()
		print("%d transactions were made and %s%.6f was paid for fees" %(len(sessionfees),coinb, sum(sessionfees)))
		print("This session's profit was: %s%.8f" %(coinb,sessionprofit))
		print()
		print('End of session available balance is:')
		print('%s%.6f'%(coinb,float(fnGetBalance(coinb)[-1][1])))
		print('%s%.6f'%(coina,float(fnGetBalance(coina)[-1][1])))
		print()

if __name__=="__main__":
	main()
