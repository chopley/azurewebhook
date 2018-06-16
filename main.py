from flask import Flask, abort, request, logging 
import logging
import json
import time
import hashlib
import requests
import ast
import azurewebhook_functions

app = Flask(__name__)

@app.route('/')
def home_screen():
    return 'Hmmmm!'

@app.route('/getProducts', methods = ['POST'])
def get_product():
    """
    End point to return the products associated with a phone number
    """
    json_data = request.get_json()
    apikey = json_data['apikey']
    apisecret = json_data['apisecret']
    login = json_data['login']
    url_login = json_data['url_login']
    token = json_data['token']
    phone = json_data['phone']
    value = json_data['products_val']
    simulate = json_data['simulate']
    products = get_msisdn_products(phone, 
                                   json_data, 
                                   apikey, 
                                   apisecret)
    print(products)
    return(json.dumps(products))

@app.route('/addData', methods = ['POST'])
def update_text():
    """
    End point to actually load data onto a phone number
    """
    logging.basicConfig(filename='myapp.log', 
                        level=logging.INFO)
    logging.info('Started')
    json_data = request.get_json()
    apikey = json_data['apikey']
    logging.info('%s ', apikey)
    apisecret = json_data['apisecret']
    login = json_data['login']
    url_login = json_data['url_login']
    token = json_data['token']
    phone = json_data['phone']
    value = json_data['products_val']
    simulate = json_data['simulate']
    products = get_msisdn_products(phone, 
                                   json_data, 
                                   apikey, 
                                   apisecret)
    product_id = get_product_id(products,
                                value)
    fixed_recharge = payload_generation(phone,
                                        str(product_id),
                                        simulate)
    services = post_transferto_goods(apikey,
                                    apisecret,
                                    'https://api.transferto.com/v1.1/transactions/fixed_value_recharges',
                                    fixed_recharge)
    print(services.text)
    ping(login,
         url_login,
         token)
    logging.info('Finished')
    return(services.text)

if __name__ == '__main__': 
    app.run(host= '0.0.0.0')
