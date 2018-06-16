def payload_generation(phone,prod_id,simulate) :
    """
    Generate the data payload that is used to trigger a bundle
    recharge.
    """
    #generate a unique external id
    external_id = str(int(1000*time.time())) 
    #now create the json object that will be used
    fixed_recharge = {
        "account_number":phone,
        "product_id" : prod_id,
        "external_id":external_id,
        "simulation":simulate,
        "sender_sms_notification":"1",
        "sender_sms_text":"Sender message",
        "recipient_sms_notification":"1",
        "recipient_sms_text":"",
        "sender":{
            "last_name":"",
            "middle_name":" ",
            "first_name":"",
            "email":"",
            "mobile":"08443011"
    },
        "recipient":{
            "last_name":"",
            "middle_name":"",
            "first_name":"",
            "email":"",
            "mobile":phone
            }
        }
    return(fixed_recharge)
  
def get_transferto_goods(apikey,apisecret,url):
    """
    This function provides the GET functionality to the 
    TransferTo API for Goods and Services
    """
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

def post_transferto_goods(apikey,apisecret,url,payload):
    """
    This function provides the POST functionality to the 
    TransferTo API for Goods and Services
    This function generates the header files for the TransferTo product
    API.
    It uses the APIKEY, APISECRET and URL endpoint.
    It feeds the payload to the API endpoint using a POST
    """
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
    """
    This function forms the basis of using the transferTo airtime API
    """
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
    """
    This function will 
    1. Find the network provider of an MSISDN
    2. Return available products associated with that MSISDN
    """
    payload = {
        'login': json_data['login'],
        'token' : json_data['token'],
        'action':'msisdn_info',
        'destination_msisdn' : msisdn
        }
    airtime_url = json_data['airtime_url']
    products_url = json_data['products_url']
    msisdn_info = request_airtime_api(airtime_url,
                                      payload)
    msisdn_info_json = jsonify_airtime_api_response(msisdn_info.content)
    operator_id = msisdn_info_json['operatorid']
    country_id = msisdn_info_json['countryid']
    url = products_url +'/countries/'+country_id+'/services'
    services = get_transferto_goods(apikey,apisecret,url)
    url = products_url + '/operators/' + operator_id + '/products'
    products = get_transferto_goods(apikey,apisecret,url)
    #return a dictionary using json.loads
    #products_json = json.loads(products.content.decode('utf8')) 
    type_of_recharge = 'fixed_value_recharges'
    return(products.json())

def get_product_id(product_dict,recharge_val):
    """
    This function will 
    1. Iterate over a dictionary of possible products
    2. Return a product that contains a specific string defined in
    recharge_val
    """
    for product in product_dict["fixed_value_recharges"]:
        product_name = product['product_name']
        if recharge_val in product_name:
            break        
    return(product['product_id'])
            

def jsonify_airtime_api_response(transferto_content):
    """
    This function will return a json string of the airtime API
    It isn't pretty but it works.
    """
    stt = transferto_content.decode('utf8').replace("\r\n", "\" , \"").replace("=", "\" : \"")
    stt2 = "\""+stt
    stt3 = "{" + stt2.rstrip(", ,\"")+"\"" + "}"
    return(ast.literal_eval(stt3))

def ping(login,url_login,token):
    """
    Implementation of the ping functionality to check that the API
    is actually up.
    """
    key = str(int(1000*time.time()))
    md5 = hashlib.md5()
    md5.update(login.encode("UTF-8"))
    md5.update(token.encode("UTF-8"))
    md5.update(key.encode("UTF-8"))
    string = url_login + '=' + login + '&key=' + key + "&md5=" + md5.hexdigest() + "&action=ping"
    response = requests.get(string)
    return(response)