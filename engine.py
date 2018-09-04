## Profitfy Exchange - Market Maker Bot
# @author intrd - http://dann.com.br/ 
# @license Creative Commons Attribution-ShareAlike 4.0 International License - http://creativecommons.org/licenses/by-sa/4.0/

import base64, hashlib, hmac, random, time, urllib, json, requests, time, os.path

def action(id1, key, url1, method, endpoint, jsonstr = None):
  function = endpoint
  urlFinal = ''.join([url1, function])
  amxtoken = amx_authorization_header(id1, key, urlFinal, method, jsonstr)
  req = exchange(str(urlFinal), amxtoken, method, jsonstr)
  return req

def getStatus():
  r = action(id1, key, url1, 'GET', 'private/userinfo')
  print "\n------- Profitfy mkt makerbot status ----------"
  print "logged: "+r["email"]
  print "feeLevel: "+str(r["feeLevel"])
  print "makerFee: "+str(r["makerFee"])
  print "makerFee: "+str(r["takerFee"])
  print r["balances"][0]
  print r["balances"][1]
  return r

def amx_authorization_header(id, key, url, method, body): ## original: https://www.tembtc.com.br/documentacao-tradeapi
   encoded_url = urllib.quote_plus(url).lower()
   method = method.upper()
   m = hashlib.md5()
   m.update(str(body))
   content = '' if body == None else base64.b64encode(m.digest())
   timestamp = str(int(time.time()))
   nonce = "3606341d00a5418faa006605"+random.choice("abcdef0123456789")+random.choice("abcdef0123456789")+random.choice("abcdef0123456789")+random.choice("abcdef0123456789")+random.choice("abcdef0123456789")+random.choice("abcdef0123456789")+random.choice("abcdef0123456789")+random.choice("abcdef0123456789")
   data = ''.join([id, method, encoded_url, timestamp, nonce, content]).encode()  
   secret = base64.b64decode(key)
   kkk=hmac.new(secret,msg=data, digestmod=hashlib.sha256).digest()
   signature = str(base64.b64encode(kkk))
   header = 'amx %s' % ':'.join([id, signature, nonce, timestamp])
   return header
               
def exchange(url, header, metodo, jsondata=False):
  try:
    if(metodo=='GET'):
      webpage = requests.get(url, headers={'Authorization': header, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0'})    
    elif(metodo=='POST'):
      webpage = requests.post(url, data=jsondata, headers={'Authorization': header, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0', 'Content-Type': 'application/json'})
    elif(metodo=='DELETE'):
      print "deleting.."
      webpage = requests.delete(url, headers={'Authorization': header, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0', 'accept': 'application/json'})
      print webpage.content
    return webpage.json()
  except Exception as e:
    print "\n ** error while requesting.. "
    print(e)
    pass

def getTicker(pair):
  r = action(id1, key, url1, 'GET', 'ticker/'+pair)
  last_price=r[0]["last"]
  print "\n** last_price(pfy):"
  print last_price
  return r

def getMyActiveOrders(pair):
  my_orders={}
  my_orders["sell"]=[]
  my_orders["buy"]=[]
  r = action(id1, key, url1, 'GET', 'orderbook/'+pair)
  for o in r[0]["sell"]:
    if o["nickName"] == nickName:
      my_orders["sell"].append(o)
  for o in r[0]["buy"]:
    if o["nickName"] == nickName:
      my_orders["buy"].append(o)
  orders = {}
  orders["all"]=[]
  orders["my"]=[]
  orders["all"].append(r)
  orders["my"].append(my_orders)
  return orders

def checkTopOrder(orders,typee,nickName,my_orders):
  toporder = orders[0][0][typee][0]
  if len(my_orders[0][typee])!=0 and toporder["nickName"] !=nickName:
    topp = {}
    topp["myorderid"]=str(my_orders[0][typee][0]["orderId"])
    return topp

def openOrder(typee, coinFrom, coinTo, amount, price):
  jsons = '''{"coinFrom" : "'''+coinFrom+'''", "coinTo":"'''+coinTo+'''", "amount":"'''+amount+'''", "price": '''+price+'''}'''
  print jsons
  r = action(id1, key, url1, 'POST', 'private/orders/'+typee, jsons)
  return r

def delOrder(typee, orderid):
  print 'private/orders/'+typee+'/'+orderid
  r = action(id1, key, url1, "DELETE", 'private/orders/'+typee+'/'+orderid)
  #print r
  return r

def checkSafePrice(checkprice,diffs,typee):
  ff = "lastorder"+typee+".txt"
  if os.path.isfile(ff):
    with open(ff,"r") as f:
      mylastprice=f.readlines()[0]
  else:
    with open(ff,"w") as f:
      f.write(str(myprice)) ## create new file 1st run 
      return False

  difff = abs(float(mylastprice)-float(checkprice))
  checkTrue = difff>float(diffs)
  if not checkTrue:
    return True
  else:
    print "\n** WARNING! Not a safe price for this new order.. \n** "+str(mylastprice)+"-"+str(checkprice)+"="+str(float(mylastprice)-float(checkprice))+", diff: "+str(diffs)

## config
# BOOTCAMP
# id1 = '1xxx-xxx-xxx-xxx-xxxxxx'
# key = 'XxXXXxXXX/8MXxxXXxxG08='
# url1 = 'https://bootcamp.profitfy.trade/api/v1/'
# nickName = "Account Nickname_1629"
# timesleep = 15
# pair = "BRL/BTC"
# opprice = 1
# amount = "0.01"
# safediff = "100.0"

# PROD
id1 = 'XXxxXX-XXXxx-XXXxx-Xxxxx-Xxxea'
key = 'XxxXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx='
url1 = 'https://profitfy.trade/api/v1/'
nickName = "Account NickName_1111"
timesleep = 15
pair = "BRL/BTC"
opprice = 1
amount = "0.001"
safediff = "3000.0"

## main loop
getStatus()

ticker = getTicker(pair)
last_price=ticker[0]["last"] 

orders = getMyActiveOrders(pair)
my_orders = orders["my"]
orders = orders["all"]
print "\n** my orders:"
print my_orders

## always on top
p = ["buy","sell"]
for typee in p:

  toporder = orders[0][0][typee][0]
  if typee=="buy":
    myprice = str(toporder["price"]+opprice)
  else:
    myprice = str(toporder["price"]-opprice)

  if len(my_orders[0][typee])==0:
    if checkSafePrice(myprice,safediff,typee):
      if typee == "sell":
        o = openOrder(typee, "BTC", "BRL", amount, myprice)
      if typee == "buy":
        o = openOrder(typee, "BRL", "BTC", amount, myprice)
      try: 
        if o["orderId"]:
          print "\n** "+typee+" order opened!:"
          print o
          #print o["price"]
          ff = "lastorder"+typee+".txt"
          with open(ff,"w") as f:
            f.write(str(o["price"]))
          token="bot111111681:XxxxX_mxLh_1-XN1Ws8s-XmX" ## your telegram api token
          chatid="-1001111117111" ## your chatid
          msg = typee+" - "+str(myprice)
          print msg
          url="https://api.telegram.org/"+token+"/sendmessage?chat_id="+chatid+"&text="+msg
          r = requests.get(url)
      except Exception as e:
        print (e)
        pass

  notontop = checkTopOrder(orders,typee,nickName,my_orders)
  if notontop:
    print "\n** detected best "+typee+" order.. cancelling my active orderid: "+notontop["myorderid"]+", and reopening another w/ price: "+myprice+"on next run.."
    d = delOrder(typee, notontop["myorderid"])

time.sleep(timesleep)
