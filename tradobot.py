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
			print('Authentication failed while getting order info ('+str(rauth)+'). The progream will close.')
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
		print('Authentication failed while getting account balances ('+str(rauth)+'). The progream will close.')
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
	if str(rauth)=='<Response [201]>' or str(rauth)=='<Response [409]>':
		return(str(rauth))
	else:
		print('Authentication failed while placing order ('+str(rauth)+'). The progream will close.')
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
		print('Authentication failed while accesing account info ('+str(rauth)+'). The progream will close.')
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

def fnGetSTXData():
	r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/ticker')
	if str(r)!='<Response [200]>':
		print('Server not responding ('+str(r)+'). The progream will close.')
		input()
		exit()
	return([int(time.time()), float(r.json()['bidRate']), float(r.json()['askRate'])])

def fnDetectCue(a):
	#Positive Peak
	if len(a)>4:
		if a[-1]>0 and a[-2]>0 and a[-3]>0 and a[-4]>0 and a[-1]<a[-2] and a[-2]<a[-3] and a[-3]>a[-4]:
			#PP Cue: Sell
			return 1
	#Nough cross
	if len(a)>1:
		if a[-1]>0 and a[-2]>0 and a[-3]<=0 and a[-4]<=0 and a[-5]<=0 and a[-6]<=0 and a[-7]<=0:    
			#NX Cue: Buy
			return 0
		if a[-1]<0 and a[-2]>=0:
			#NX Cue: Sell
			return 1
	#Saucers
	if len(a)>4:
		#if a[-1]>0 and a[-2]>0 and a[-3]>0 and a[-1]>a[-2] and a[-3]>a[-2] and a[-4]>a[-3]:###Delete Comments to activate this Cue. Strategy will turn less conservative.
			#Saucer Cue: Buy
		#	return 0 
		if a[-1]<0 and a[-2]<0 and a[-3]<0 and a[-1]<a[-2] and a[-3]<a[-2] and a[-4]<a[-3]:
			#Saucer Cue: Sell
			return 1

def fnBuy(m, p):
	print('**********************BUY ORDER**********************')      
	g=m/((1+gfee)*p)
	answer='<Response [201]>'#fnPlaceOrder('BUY',g,p)  ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		print("%s%.6f bought at $%.6f"%(coina,g, p))
		print("Amount spent on transaction was %s%.6f + a %s%.6f fee." %(coinb,g*p,coinb,g*p*gfee))
		return g
	else:
		print("Server returned error %s. Transaction failed."%answer)
		return 0
	
def fnSell(g, p):
	print('**********************SELL ORDER**********************')
	answer='<Response [201]>'#fnPlaceOrder('SELL',g,p) ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		print("%s%.6f sold at $%.6f"%(coina,g, p))
		m=g*p*(1-gfee)
		print("Transaction profit was %s%.6f (%s%.6f fee was paid)." %(coinb,g*(p*(1-gfee)-LP*(1+gfee)),coinb,g*p*gfee))
		return m
	else:
		print("Server returned error %s. Transaction failed."%answer)
		return 0
def main():
	try:
		global pricelist
		pricelist=[]
		mid=[]
		SMA5=[]
		SMA34=[]
		AO=[]
		sessionfees=[]
		sessionprofit=0.0
		
		global coina
		global coinb
		global APIKEY
		global APISECRET
		global gfee
		global LP
		
		coina='' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
		coinb='' 
		
		LP=float(0) #enter here the minimum price at which you want to sell available BTC. If you decide to not use available BTC leave it at 0.
		
		APIKEY= ''####YOUR APIKEY HERE####
		APISECRET= ''####YOUR APISECRET HERE####
		
		print()
		print('TRADOBOT v0.1 - Automatic trading on Bittrex Market by fcooet1.')
		print('This bot uses Bill Williams Momentum strategy to trade automatically.')
		print()
		if APIKEY=='' or APISECRET=='':
			print("APIKEY or APISECRET are missing. The program will end.")
			input()
			exit()
		if coina=='' or coinb=='':
			print("Coin Market definitions are missing. The program will end.")
			input()
			exit()
		r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/candles/TRADE/MINUTE_1/recent')
		if str(r)!='<Response [200]>':
			print("Selected market unavailable. ("+str(rauth)+'). The progream will close.')
			input()
			exit()
		rj=r.json()
		print('Current market is at %.6f%s for 1%s.' %(float(rj[-1]['high']),coinb,coina))
		print('Available account balance is:')
		print('%s%.6f'%(coinb,float(fnGetBalance(coinb)[-1][1])))
		print('%s%.6f'%(coina,float(fnGetBalance(coina)[-1][1])))
		if float(fnGetBalance(coina)[-1][1])>0.0:
			print('Use available %s? Y/N' %coina)
			auxqstn=''
			while auxqstn!=('y' and 'Y' and 'n' and 'N'):
				auxqstn=str(input())
				if auxqstn==('y' or 'Y'):
					coinacash=float(fnGetBalance(coina)[-1][1])
					maxcoina=0.0
				if auxqstn==('n' or 'N'):
					coinacash=0.0
					maxcoina=float(fnGetBalance(coina)[-1][1])
		else:
			coinacash=0.0
			maxcoina=0.0
		gfee=fnFee()
		print('At this moment your commision rate is '+str(gfee*100)+"%")
		
		stoploss = 0.15
		print("A stop-loss is set at "+str(stoploss*100)+"% of buy price.")
		      
		print('Input maximum %s amount to take from your account when trading.' %coinb)
		maxtrad=float(input())
		print('Input %s amount to start trading with.' %coinb)
		auxcash=float(input())
		while auxcash>=float(fnGetBalance(coinb)[-1][1]):
			print('Insuficient funds.')
			auxcash=float(input())
			maxtrad=auxcash
		coinbcash=auxcash
		startdate=int(time.time())
		print()
		r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/candles/TRADE/MINUTE_1/recent')
		rj=r.json()
		for tik in rj:
			rjt=[int(time.time()),float(tik['low']),float(tik['high'])]
			pricelist.append(rjt)
			mid.append(((pricelist[-1][2]+pricelist[-1][1])/2))
			if len(mid)>=5:
				SMA5.append(sum(mid[-5:])/5)
			if len(mid)>=34:
				SMA34.append(sum(mid[-34:])/34)
				AO.append(SMA5[-1]-SMA34[-1])
			sys.stdout.write("\rInitializing " +str(round(100*len(pricelist)/len(rj)))+'%')
			sys.stdout.flush()
		print()
		
		print()
		print("Tradobot will now wait for market Cues each passing minute.")
		print("Transactions will be displayed when made.")
		print('Press Ctrl+C anytime to stop the bot.')
		print('A ledger file will be saved containing all session info.')
		print()

		while True:
			currenttime=time.time()
			pricelist.append(fnGetSTXData())
			print(str(pricelist[-1]))
			mid.append((pricelist[-1][2]+pricelist[-1][1])/2)
			SMA5.append(sum(mid[-5:])/5)
			SMA34.append(sum(mid[-34:])/34)
			AO.append(SMA5[-1]-SMA34[-1])
			aux=fnDetectCue(AO)
			opp='none'
			if (1-stoploss)*LP>=pricelist[-1][1] and coinacash>0 and AO[-1]<0:#STOP-LOSS
				gfee=fnFee()
				coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
				auxsell=coinbcash
				counter=0
				print('**********************STOP--LOSS**********************')
				coinbcash=fnSell(coinacash,pricelist[-1][1])
				while coinbcash==0 and counter<10:
					opp='SL-failed'
					coinbcash=auxsell
					print("Attempting to place order again.[%d]" %(counter+1))
					coinbcash=fnSell(coinacash,fnGetSTXData()[1])
					time.sleep(1)
					counter+=1
				if coinbcash>0 and counter!=10:
					sessionfees.append(coinacash*pricelist[-1][1]*gfee)
					sessionprofit+=(coinbcash-coinacash*LP-sessionfees[-1])
					LP=0.0
					opp='SL'
					coinbcash=min(maxtrad,float(fnGetBalance(coinb)[-1][1]))
				coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
				print()	
			if aux==1:#Sell
				gfee=fnFee()
				coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
				if LP/(1-gfee)**2<pricelist[-1][1] and coinacash>0 and LP!=0:
					auxsell=coinbcash
					counter=0
					coinbcash=fnSell(coinacash,pricelist[-1][1])
					while coinbcash==0 and counter<10:
						opp='sell-failed'
						coinbcash=auxsell
						print("Attempting to place order again.[%d]" %(counter+1))
						coinbcash=fnSell(coinacash,fnGetSTXData()[1])
						time.sleep(1)
						counter+=1
					if coinbcash>0 and counter!=10:
						sessionfees.append(coinacash*pricelist[-1][1]*gfee)
						sessionprofit+=(coinbcash-coinacash*LP-sessionfees[-1])
						LP=0.0
						opp='sell'
						coinbcash=min(maxtrad,float(fnGetBalance(coinb)[-1][1]))
					coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
					print()	
			if aux==0:#Buy
				gfee=fnFee()
				if coinbcash>0 and pricelist[-1][2]>pricelist[-2][2]:
					auxbuy=coinacash
					coinacash=fnBuy(coinbcash,pricelist[-1][2])
					if coinacash==0:
						coinacash=auxbuy
						coinbcash=min(fnGetBalance(coina)[-1][1],maxtrad)
						opp='buy-failed'
					if coinacash>0 and opp!='buy-failed':
						sessionfees.append((coinbcash*gfee)/(1+gfee))
						LP=pricelist[-1][2]
						opp='buy'
						coinacash=float(fnGetBalance(coina)[-1][1])-maxcoina
						coinbcash=0.0
					print()
			entry=[time.strftime('%d/%m/%y %H:%M',time.localtime(int(currenttime))),pricelist[-1][1],pricelist[-1][2],AO[-1],aux,opp,LP,gfee]
			fnSavetoLedger(str(entry).replace("'","").replace("[","").replace("]",""),startdate)
			
			if currenttime+60>time.time():
				time.sleep(currenttime+60-time.time())
			else:
				r=requests.get('https://api.bittrex.com/v3/markets/'+coina+'-'+coinb+'/candles/TRADE/MINUTE_1/recent')
				rj=r.json()
				for tik in rj:
					sys.stdout.write("\rRebuilding oscilator " +str(round(100*rj.index(tik)/len(rj)))+'%')
					rjt=[int(time.time()),float(tik['low']),float(tik['high'])]
					pricelist.append(rjt)
					mid.append(((pricelist[-1][2]+pricelist[-1][1])/2))
					if len(mid)>=5:
						SMA5.append(sum(mid[-5:])/5)
					if len(mid)>=34:
						SMA34.append(sum(mid[-34:])/34)
						AO.append(SMA5[-1]-SMA34[-1])
					sys.stdout.flush()
				print()
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
