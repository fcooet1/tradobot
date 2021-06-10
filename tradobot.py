#!/usr/bin/python
#fcooet1 jun 2021

import requests,json,time,sys,hashlib,hmac,uuid

class Inv:
	def __init__(self,mkt,qty,bdate,batt,bfee):
		self.mkt=mkt
		self.qty=qty
		self.bdate=bdate
		self.batt=batt
		self.bfee=bfee
		self.bcost=0
		self.satt=0
		self.sdate=0
		self.sfee=0
		self.profit=0
	def buy(self):
		self.bcost=self.qty*self.batt*(1+self.bfee)
		print("%.8f%s bought at %.2f, %.6f%s fee paid." %(self.qty,self.mkt[:self.mkt.index("-")],self.batt,self.bfee*self.qty*self.batt,self.mkt[-(len(self.mkt)-self.mkt.index("-"))+1:]))
		print("Transaction cost was %.5f%s." %(self.bcost,self.mkt[-(len(self.mkt)-self.mkt.index("-"))+1:]))
		print()
	def sell(self):
		self.profit=self.qty*(self.satt*(1-self.sfee)-self.batt*(1+self.bfee))
		print("%.8f%s sold at %.2f, %.5f%s fee paid." %(self.qty,self.mkt[:self.mkt.index("-")],self.satt,self.sfee*self.qty*self.satt,self.mkt[-(len(self.mkt)-self.mkt.index("-"))+1:]))
		print("Transaction profit was %.5f%s." %(self.profit,self.mkt[-(len(self.mkt)-self.mkt.index("-"))+1:]))
		print()

def fnSavetoLog(entry,startdate):
	with open('log_'+str(startdate)+'.txt','a') as filehandle:
		filehandle.write('%s\n' %entry)
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
		#if a[-1]>0 and a[-2]>0 and a[-3]>0 and a[-1]>a[-2] and a[-3]>a[-2] and a[-4]>a[-3]:
			#Saucer Cue: Buy
			#return 0 
		if a[-1]<0 and a[-2]<0 and a[-3]<0 and a[-1]<a[-2] and a[-3]<a[-2] and a[-4]<a[-3]:
			#Saucer Cue: Sell
			return 1

def fnBuy(m, p):
	print('**********************BUY ORDER**********************')      
	g=m/((1+gfee)*p)
	answer='<Response [201]>'#fnPlaceOrder('BUY',g,p)  ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		return g
	else:
		print("Server returned error %s. Transaction failed."%answer)
		print()
		return 0
	
def fnSell(g, p):
	print('**********************SELL ORDER**********************')
	answer='<Response [201]>'#fnPlaceOrder('SELL',g,p) ####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
	if answer=='<Response [201]>':
		return 1
	else:
		print("Server returned error %s. Transaction failed."%answer)
		print()
		return 0
def main():
	try:
		global pricelist
		pricelist=[]
		mid=[]
		SMA5=[]
		SMA34=[]
		AO=[]
		assets=[]
		returns=[]
		
		global coina
		global coinb
		global APIKEY
		global APISECRET
		global gfee
		responce=-1
		
		coina='' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
		coinb='' 
				
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
			print("Market doesn't exist. ("+str(rauth)+'). The progream will close.')
			input()
			exit()
		rj=r.json()
		print('Current market is at %.6f %s for 1%s.' %(float(rj[-1]['high']),coinb,coina))
		print('Current available balance is:')
		print('%s%.6f'%(coinb,float(fnGetBalance(coinb)[-1][1])))
		print('%s%.6f'%(coina,float(fnGetBalance(coina)[-1][1])))
		if float(fnGetBalance(coina)[-1][1])>0.0:
			print('Use available %s? Y/N' %coina)
			auxqstn=''
			while auxqstn!=('y') and auxqstn!=('Y') and auxqstn!=('n') and auxqstn!=('N'):
				auxqstn=str(input())
				if auxqstn==('y' or 'Y'):
					print('Minimum price to sell your %s' %coina)
					assets.append(Inv(coina+"-"+coinb,fnGetBalance(coina)[-1][1],int(time.time()),float(input()),0.0075))
					assets[-1].buy()

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
		print('Check README to understand ledger data.')
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

			for a in assets: #STOP-LOSS
				if (1-stoploss)*a.batt>=pricelist[-1][1] and a.satt==0 and AO[-1]<0:
					gfee=fnFee()
					counter=0
					print('**********************STOP--LOSS**********************')
					P=fnGetSTXData()[1]
					responce=fnSell(a.qty,pricelist[-1][1])
					while responce==0 and counter<10:
						print("Attempting to place order again.[%d]" %(counter+1))
						P=fnGetSTXData()[1]
						responce=fnSell(a.qty,P)
						time.sleep(1)
						opp='SL-failed'
						counter+=1
					if responce>0 and counter!=10:
						a.satt=P
						a.sdate=currenttime
						a.sfee=gfee
						a.sell()
						returns.append(a)
						coinbcash+=a.qty*a.satt*(1-a.sfee)
						opp='SL'
						ledgerentry=[time.strftime('%d/%m/%y %H:%M',time.localtime(int(currenttime))),opp,coinbcash,assets[-1].qty,assets[-1].satt,assets[-1].sfee,assets[-1].profit]
						fnSavetoLedger(str(ledgerentry).replace("'","").replace("[","").replace("]",""),startdate)
					responce=-1					
			if aux==1:#SELL
				gfee=fnFee()
				for a in assets:
					if a.batt/((1-a.bfee)*(1-gfee))<pricelist[-1][1] and a.satt==0:
						counter=0
						P=fnGetSTXData()[1]
						responce=fnSell(a.qty,P)
						while responce==0 and counter<10:
							print("Attempting to place order again.[%d]" %(counter+1))
							P=fnGetSTXData()[1]
							responce=fnSell(a.qty,P)
							time.sleep(1)
							opp='sell-failed'
							counter+=1
						if responce>0 and counter!=10:
							a.satt=P
							a.sdate=currenttime
							a.sfee=gfee
							a.sell()
							returns.append(a)
							coinbcash+=a.qty*a.satt*(1-a.sfee)
							opp='sell'
							ledgerentry=[time.strftime('%d/%m/%y %H:%M',time.localtime(int(currenttime))),opp,coinbcash,assets[-1].qty,assets[-1].satt,assets[-1].sfee,assets[-1].profit]
							fnSavetoLedger(str(ledgerentry).replace("'","").replace("[","").replace("]",""),startdate)
						responce=-1
			if aux==0:#BUY
				gfee=fnFee()
				if coinbcash>0:
					coinbcash=min(coinbcash,maxtrad)
					responce=fnBuy(coinbcash,pricelist[-1][2])
					if responce==0:
						coinbcash=min(coinbcash,maxtrad)
						opp='buy-failed'
					if responce>0 and opp!='buy-failed':
						assets.append(Inv(coina+"-"+coinb,responce,currenttime,pricelist[-1][2],gfee))
						assets[-1].buy()
						opp='buy'
						coinbcash=0.0
						ledgerentry=[time.strftime('%d/%m/%y %H:%M',time.localtime(int(currenttime))),opp,coinbcash,assets[-1].qty,assets[-1].batt,assets[-1].bfee,assets[-1].bcost]
						fnSavetoLedger(str(ledgerentry).replace("'","").replace("[","").replace("]",""),startdate)
					responce=-1

			logentry=[time.strftime('%d/%m/%y %H:%M',time.localtime(int(currenttime))),pricelist[-1][1],pricelist[-1][2],AO[-1],aux,opp,gfee]
			fnSavetoLog(str(logentry).replace("'","").replace("[","").replace("]",""),startdate)
			
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
		if len(returns)-len(assets)<0:
			print("Active assets will be listed bellow:")
		for a in assets:
			if a.satt!=0:
				a.buy()
			prof=0+a.profit
			fees=0+a.qty*(a.satt*a.sfee+a.batt*a.bfee)
		print("%d transactions were made and %s%.6f was paid for fees" %(len(assets)+len(returns),coinb,fees))
		print("This session's profit was: %s%.8f" %(coinb,prof))
		print()
		print('End of session available balance is:')
		print('%s%.6f'%(coinb,float(fnGetBalance(coinb)[-1][1])))
		print('%s%.6f'%(coina,float(fnGetBalance(coina)[-1][1])))
		print()
		ledgerentry=[time.strftime('%d/%m/%y %H:%M',time.localtime(int(currenttime))),"end",prof]
		fnSavetoLedger(str(ledgerentry).replace("'","").replace("[","").replace("]",""),startdate)

if __name__=="__main__":
	main()
