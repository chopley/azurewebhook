import time
import hashlib
import ast
import json

        

class Transferto:
    def __init__(self):
        print("A transferTo object is created.")
        
    def initiate_rapidpro_json(self,json_data):
        self.json_data = json_data
        self.phone = self.json_data['phone']
        self.value = self.json_data['products_val']
        self.simulate = self.json_data['simulate']
        print(json_data)
    
    def read_credentials_file(self,filename):
        with open(filename, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
        self.apikey = data['transferto_apikey']
        self.apisecret = data['transferto_apisecret']
        self.login = data['transferto_login']
        self.url_login = data['transferto_url_login']
        self.token = data['transferto_token']
        self.airtime_url = data['transferto_airtime_url']  
        self.products_url = data['transferto_products_url']
        print(self.products_url)
    
    def initiate_test_json(self,json_data):
        self.json_data = json_data
        #self.apikey = json_data['apikey']
        #self.apisecret = json_data['apisecret']
        #self.login = json_data['login']
        #self.url_login = json_data['url_login']
        #self.token = json_data['token']
        self.phone = json_data['phone']
        self.value = json_data['products_val']
        self.simulate = json_data['simulate']
        #self.airtime_url = json_data['airtime_url']  
        #self.products_url = json_data['products_url']
            
    def payload_generation(self) :
        external_id = str(int(1000 * time.time())) 

        # now create the json object that will be used
        fixed_recharge = {
            "account_number":self.phone,
            "product_id" : self.product_id,
            "external_id":external_id,
            "simulation":self.simulate,
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
                "mobile":self.phone
                }
            }
        self.fixed_recharge = fixed_recharge
        return(fixed_recharge)
  
    def get_transferto_goods(self,url):
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
        message = bytes((self.apikey + str(nonce)).encode('utf-8'))
        secret = bytes(self.apisecret.encode('utf-8'))
        hmac = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
        headers = {}
        headers['X-TransferTo-apikey'] = self.apikey
        headers['X-TransferTo-nonce'] = str(nonce)
        headers['x-transferto-hmac'] = hmac
        response = requests.get(url, headers=headers)
        return(response)        


    def post_transferto_goods(self,url):
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
        message = bytes((self.apikey + str(nonce)).encode('utf-8'))
        secret = bytes(self.apisecret.encode('utf-8'))
        hmac = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
        headers = {}
        headers['X-TransferTo-apikey'] = self.apikey
        headers['X-TransferTo-nonce'] = str(nonce)
        headers['x-transferto-hmac'] = hmac
        response = requests.post(url, headers=headers, json=self.fixed_recharge)
        return(response)


    def request_airtime_api(self,url):
        """
        This function forms the basis of using the transferTo airtime API
        """
        payload_action = self.payload_action
        key = str(int(1000 * time.time()))
        md5 = hashlib.md5()
        md5.update(payload_action['login'].encode("UTF-8"))
        md5.update(payload_action['token'].encode("UTF-8"))
        md5.update(key.encode("UTF-8"))
        payload_action.update({'key':key,
                                         'md5':md5.hexdigest()})
        response = requests.post(url,
                            data=payload_action)
        return(response)
    
    
    def get_msisdn_products(self):
        """
        This function will 
        1. Find the network provider of an MSISDN
        2. Return available products associated with that MSISDN
        3. Update the object with these products
        """
        self.payload_action = {
            'login': self.login,
            'token' : self.token,
            'action':'msisdn_info',
            'destination_msisdn' : self.phone
            }
               
        msisdn_info = self.request_airtime_api(self.airtime_url)
        msisdn_info_json = self.jsonify_airtime_api_response(msisdn_info.content)
        operator_id = msisdn_info_json['operatorid']
        country_id = msisdn_info_json['countryid']
        url = self.products_url + '/countries/' + country_id + '/services'
        services = self.get_transferto_goods(url)
        url = self.products_url + '/operators/' + operator_id + '/products'
        products = self.get_transferto_goods(url)
        # return a dictionary using json.loads
        # products_json = json.loads(products.content.decode('utf8')) 
        type_of_recharge = 'fixed_value_recharges'
        self.products = products.json()
        return(products.json())
    
    
    def get_product_id(self):
        """
        This function will 
        1. Iterate over a dictionary of possible products
        2. Return a product that contains a specific string defined in
        recharge_val
        """
        product_dict = self.products
        recharge_val = self.value
        for product in product_dict["fixed_value_recharges"]:
            product_name = product['product_name']
            if recharge_val in product_name:
                break        
        self.product_id = product['product_id'] 
        return(product['product_id'])
                
    
    def jsonify_airtime_api_response(self,transferto_content):
        """
        This function will return a json string of the airtime API
        It isn't pretty but it works.
        """
        stt = transferto_content.decode('utf8').replace("\r\n", "\" , \"").replace("=", "\" : \"")
        stt2 = "\"" + stt
        stt3 = "{" + stt2.rstrip(", ,\"") + "\"" + "}"
        return(ast.literal_eval(stt3))
    
    
    def ping(self):
        """
        Implementation of the ping functionality to check that the API
        is actually up.
        """
        key = str(int(1000 * time.time()))
        md5 = hashlib.md5()
        md5.update(self.login.encode("UTF-8"))
        md5.update(self.token.encode("UTF-8"))
        md5.update(key.encode("UTF-8"))
        string = self.url_login + '=' + self.login + '&key=' + key + "&md5=" + md5.hexdigest() + "&action=ping"
        response = requests.get(string)
        return(response)

