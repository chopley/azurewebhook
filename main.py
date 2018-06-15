from flask import Flask, abort, request, logging 
import logging
import json
import time
import hashlib
import requests
import ast


def return_transferto_goods_vals(apikey,apisecret,url,payload):
    import requests
    import time
    import hashlib
    import hmac
    import base64
    nonce = int(time.time())
    message = bytes((apikey + str(nonce)).encode('utf-8'))
    secret = bytes(apisecret.encode('utf-8'))
    hmac = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
    headers = {}
    headers['X-TransferTo-apikey'] = apikey
    headers['X-TransferTo-nonce'] = str(nonce)
    headers['x-transferto-hmac'] = hmac
    response = requests.get(url, headers=headers)
    return(response)

def return_transferto_goods_vals_post(apikey,apisecret,url,payload):
    import requests
    import time
    import hashlib
    import hmac
    import base64
    nonce = int(time.time())
    message = bytes((apikey + str(nonce)).encode('utf-8'))
    secret = bytes(apisecret.encode('utf-8'))
    hmac = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
    headers = {}
    headers['X-TransferTo-apikey'] = apikey
    headers['X-TransferTo-nonce'] = str(nonce)
    headers['x-transferto-hmac'] = hmac
    response = requests.post(url, headers=headers, json=payload)
    return(response)

def request_airtime_api(url,payload_action):
    key = str(int(1000*time.time()))
    md5 = hashlib.md5()
    md5.update(payload_action['login'].encode("UTF-8"))
    md5.update(payload_action['token'].encode("UTF-8"))
    md5.update(key.encode("UTF-8"))
    payload_action.update({'key':key,
                                     'md5':md5.hexdigest()})
    response = requests.post(url,
                        data=payload_action)
    return(response)

def get_msisdn_products(msisdn,json_data,apikey,apisecret):
    payload = {'login': json_data['login'],
           'token' : json_data['token'],
           'action':'msisdn_info',
           'destination_msisdn' : msisdn}
    airtime_url = json_data['airtime_url']
    products_url = json_data['products_url']
    msisdn_info = request_airtime_api(airtime_url,
             payload)
    msisdn_info_json = jsonify(msisdn_info.content)
    operator_id = msisdn_info_json['operatorid']
    country_id = msisdn_info_json['countryid']
    url = products_url +'/countries/'+country_id+'/services'
    services = return_transferto_goods_vals(apikey,apisecret,url,'')
    url = products_url + '/operators/' + operator_id + '/products'
    products = return_transferto_goods_vals(apikey,apisecret,url,'')
    product_ids = json.loads(products.content)
    type_of_recharge = 'fixed_value_recharges'
    return(product_ids)

def jsonify(transferto_content):
    stt = transferto_content.decode('utf8').replace("\r\n", "\" , \"").replace("=", "\" : \"")
    stt2 = "\""+stt
    stt3 = "{" + stt2.rstrip(", ,\"")+"\"" + "}"
    return(ast.literal_eval(stt3))

def ping(login,url_login,token):
    key = str(int(1000*time.time()))
    md5 = hashlib.md5()
    md5.update(login.encode("UTF-8"))
    md5.update(token.encode("UTF-8"))
    md5.update(key.encode("UTF-8"))
    string = url_login + '=' + login + '&key=' + key + "&md5=" + md5.hexdigest() + "&action=ping"
    response = requests.get(string)
    return(response)

app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/resource', methods = ['POST'])
def update_text():
  logging.basicConfig(filename='myapp.log', level=logging.INFO)
  logging.info('Started')
  json_data = request.get_json()
  apikey = json_data['apikey']
  logging.info('%s ', apikey)
  apisecret = json_data['apisecret']
  login = json_data['login']
  url_login = json_data['url_login']
  token = json_data['token']
  phone = json_data['phone']
  #products = get_msisdn_products(phone,json_data,apikey,apisecret)
  ping(login,url_login,token)
  logging.info('Finished')
  return json.dumps(json_date)

if __name__ == '__main__': 
  app.run()
