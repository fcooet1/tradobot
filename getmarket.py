#!/usr/bin/env python3
#Import Stuff
import requests,json,time,datetime,sys

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
		if a[-1]>0 and a[-2]>0 and a[-3]>0 and a[-1]>a[-2] and a[-3]>a[-2] and a[-3]<a[-4]:
			#Saucer Cue: Buy
			return 0 
		if a[-1]<0 and a[-2]<0 and a[-3]<0 and a[-1]<a[-2] and a[-3]<a[-2] and a[-3]>a[-4]:
			#Saucer Cue: Sell
			return 1
	else:
		return 2

def fnBuyETH(m, p):
	#m=money used p=price of good g=good recieved
	g=m/p
	print('*****************************************************')
	print("ETH"+str(g)+" bought for $"+str(p))
	return g

def fnSellETH(g,p):
	#m=money recieved p=price of good g=good to sell
	m=g*p
	print('*****************************************************')
	print("ETH"+str(g)+" sold for $"+str(p))
	return m

##################################################
#######       Program Inizialization       #######
##################################################

btc_eth=[]
mid=[]
SMA5=[]
SMA34=[]
AO=[]
print('TRADOBOT v0.1 - Automatic ETH-BTC trading on Bittrex Market by FO')
print('This bot uses Bill Williams AO Momentum strategy to trade automatically')
print('Input BTC amount to start trading')
BTCcash=float(input())
startingpoint=BTCcash
ETHcash=0.0
LastPrice=0.0
print('Press Ctrl+C to stop the bot and recover your BTC at current market price')


while len(btc_eth)<34:
		btc_eth.append(fnGetSTXData('ETH', 'BTC'))
		sys.stdout.write("\rInitializing %" +str(round(100*len(btc_eth)/34)))
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
		btc_eth.append(fnGetSTXData('ETH', 'BTC'))
		mid.append((btc_eth[-1][2]+btc_eth[-1][1]/2))
		if len(btc_eth)>=5:
			SMA5.append(sum(mid[-5:])/5)
			
		if len(btc_eth)>=34:
			SMA34.append(sum(mid[-34:])/34)
			AO.append(SMA5[-1]-SMA34[-1])
		aux=fnDetectCue(AO)
	
		if aux==1:
			#print('Price: L$'+str(btc_eth[-1][1])+' Price: H$'+str(btc_eth[-1][2]))#Sellprice
			#print()
			if LastPrice<btc_eth[-1][1] and ETHcash>0:
				BTCcash=fnSellETH(ETHcash,btc_eth[-1][1])
				ETHcash=0.0
				LastPrice=999999999999.9
				print("Current BTC balance is $"+str(BTCcash))
				print()
				
		if aux==0:
			#print('Price: L$'+str(btc_eth[-1][1])+' Price: H$'+str(btc_eth[-1][2]))#Buyprice
			#print()
			if BTCcash>0:
				ETHcash=fnBuyETH(BTCcash,btc_eth[-1][2])
				BTCcash=0.0
				LastPrice=btc_eth[-1][2]
				print("Current BTC balance is $"+str(BTCcash))
				print()

		time.sleep(0.5)
except KeyboardInterrupt:
	print('The bot has stoped')
	print()
	if ETHcash>0:
		BTCcash=fnSellETH(ETHcash,btc_eth[-1][1])
		LastPrice=999999999999.9
		print("Current BTC balance is $"+str(BTCcash))
		ETHcash=0.0
		print()
	else:
		print("Current BTC balance is $"+str(BTCcash))
	print("This session's profit was: BTC"+str(BTCcash-startingpoint))
