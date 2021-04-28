# tradobot

Tradobot uses [Bill Wiliams Momentum strategy](https://tradingstrategyguides.com/bill-williams-awesome-oscillator-strategy/#:~:text=The%20Bill%20Williams%20Awesome%20Oscillator,confirming%20the%20price%20action%20shift.) to continuously and automatically trade on Bittrex market platform through their API. It can handle multiple instances, so you can run it on different markets simultaneously, as long as the server responce limit is not reached.

## Setup

To get started you need to modify the following variables in the code:
Add you API Key and Secret inside the apostrophes.
```bash
APIKEY= ''####YOUR APIKEY HERE####
APISECRET= ''####YOUR APISECRET HERE####
```
Define which coins you want this session to trade (for example, for BTC-USDT, assign variables as follows).
```bash
coina='BTC' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
coinb='USDT' ####CHANGE coina AND coinb VALUES TO SELECT DESIRED MARKET.
```
If your coina balance is positive and you want to use it to trade during this session, you can define a minimum price for the bot to start selling at:
```bash
LP=float(0) #enter here the minimum price at which you want to sell available coina.
            #If you decide to not use available coina leave it at 0.
```
For safety reasons, fnBuy and fnSell, the functions in charge of placing orders on Bittrex system are not activated by default. To activate them modify the code within them as follows:
Within fnBuy:
```bash
answer='<Response [201]>'#fnPlaceOrder('BUY',g,p,i)
####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
```
Should look like:
```bash
answer=fnPlaceOrder('BUY',g,p,i)
```
and within fnSell:
```bash
answer='<Response [201]>'#fnPlaceOrder('SELL',g,p,i)
####DELETE '<Response [201]>'# RIGHT TO answer= TO ACTIVATE REAL TRADING####
```
Should look like:
```bash
answer=fnPlaceOrder('SELL',g,p,i)
```
## Getting Started
Now you should be ready to go. Run the code using your favourite compiler.
As you run the program, it will try to authenticate. If it fails you'll be noticed and the program will shut down. You'll need to check your APIKEY and APISECRET values. If they are correct, you should get information of the current buy price of the selected market and your available funds.
The program will ask if you want to use your available balance of coina. Input Y for Yes or N for No.
Then it will ask for the maximum amount of coinb you'll allow it to get from your account during this session. Input the value as int or float. This value cannot be larger than your current available balance.
Finally it'll ask you to input the amount you wish to start with. Input as int or float. This value, as well, cannot be larger than your current available balance.
Once you enter this input, the program will start runnung. It'll get market data from Bittrex each minute and diplay it in the console in this format:
```bash
[currentUNIXepoch,priceLow,priceHigh]
```
Whenever the transaction criteria are filled, the Buy or Sell function will be executed. Buy orders are filled using 100% of the asigned coinb value. Sell orders will be executed only when the price is above the last Buy price or the price asigned to the LP variable. This takes Bittrex comission into account, so Sell orders will always profit.
A summary of each transaction will be displayed in the console.
The program will run indefinitelly. It can be stoped by pressing Ctrl+C. A summary of the sesion will be displayed in the console before shutting down.
## Data Record
The program keeps a record of each minute's events in a text file called ledger_xxxxxxxxxx.txt, where xxxxxxxxxx is the UNIXepoch at which the session started. Data is stored in the following format:
```bash
[UNIXepoch, priceLow, priceHigh, AwesomeOscilatorValue, AwesomeOscilatorCue, transactionType, lastBuyPrice]
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

Feel free to use my Bittrex request code if you're creating a new account: GN5-2CC-ZK3

## License
[MIT](https://choosealicense.com/licenses/mit/)
