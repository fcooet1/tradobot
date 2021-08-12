#!/usr/bin/env python3
#Import Stuff
import requests,json,time,datetime,sys
import argparse

parser = argparse.ArgumentParser(prog="getmarket")

parser.add_argument("--currA", type=str, default="ETH", help="Currency A")
parser.add_argument("--currB", type=str, default="USD", help="Currency B")

args = parser.parse_args()

#####################################
#######       Functions       #######
#####################################

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

def fnBuyETH(m, p):
	fee= m*.0075
	g=(m-fee)/p
	print('*****************************************************')
	print("ETH%.6f bought for $%.6f"%(g, p))
	print('$%.5f fee paid'%fee)
	return g

def fnSellETH(g,p):
	fee=g*.0075
	m=(g-fee)*p
	print('*****************************************************')
	print("ETH%.6f bought for $%.6f"%(g, p))
	print('$%.5f fee paid'%fee)
	return m

##################################################
#######       Program Inizialization       #######
##################################################

pricelist=[]
mid=[]
SMA5=[]
SMA34=[]
AO=[]
coina=args.currA
coinb=args.currB
print('TRADOBOT v0.1 - Automatic ETH-BTC trading on Bittrex Market by FO')
print('This bot uses Bill Williams AO Momentum strategy to trade automatically')
print('Input BTC amount to start trading')
BTCcash=float(input())
startingpoint=BTCcash
ETHcash=0.0
LastPrice=0.0
sessionfees=[]
print('Press Ctrl+C to stop the bot and recover your BTC at current market price')

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


print(btc_eth)

########################################
#######       Program Main       #######
########################################

try:
	while True:
		pricelist.append(fnGetSTXData(coina, coinb))
		mid.append((pricelist[-1][2]+pricelist[-1][1]/2))
		SMA5.append(sum(mid[-5:])/5)
		SMA34.append(sum(mid[-34:])/34)
		AO.append(SMA5[-1]-SMA34[-1])
		aux=fnDetectCue(AO)
	
		if aux==1:
			#Sell
			if LastPrice/(1-.0075)**2<pricelist[-1][1] and ETHcash>0:
				BTCcash=fnSellETH(ETHcash,pricelist[-1][1])
				sessionfees.append(0.0075*ETHcash)
				ETHcash=0.0
				LastPrice=999999999999.9
				print("Current BTC balance is $%.6f" %BTCcash)
				print()	
		if aux==0:
			#Buy
			if BTCcash>0:
				ETHcash=fnBuyETH(BTCcash,pricelist[-1][2])
				sessionfees.append(0.0075*ETHcash)
				BTCcash=0.0
				LastPrice=pricelist[-1][2]
				print("Current BTC balance is $%.6f" %BTCcash)
				print()
		time.sleep(60)
except KeyboardInterrupt:
	print('The bot has stoped')
	print()
	if ETHcash>0:
		BTCcash=fnSellETH(ETHcash,pricelist[-1][1])
		sessionfees.append(0.0075*ETHcash)
		LastPrice=999999999999.9
		print("Current BTC balance is $%.6f" %BTCcash)
		ETHcash=0.0
		print()
	else:
		print("Current BTC balance is $%.6f" %BTCcash)
	print("%d transactions were made and $%.6f was paid for fees" %(len(sessionfees), sum(sessionfees)))
	print("This session's profit was: BTC%.8f" %(BTCcash-startingpoint))
