from flask import Flask, abort, request, logging 
import logging
import json

from azurewebhook_functions import *

app = Flask(__name__)

@app.route('/')
def home_screen():
    return 'Hmmmm!'

@app.route('/getProducts', methods = ['POST'])
def getProductObject():
    """
    End point to return the products associated with a phone number
    """
    json_data = request.get_json()
    tf = Transferto(json_data) 
    products = tf.get_msisdn_products()
    return(json.dumps(products))

@app.route('/addData', methods = ['POST'])
def addDataObject():
    """
    End point to actually load data onto a phone number
    """
    json_data = request.get_json()
    tf = Transferto(json_data)  
    tf.get_msisdn_products()
    tf.get_product_id()
    tf.payload_generation()
    services = tf.post_transferto_goods('https://api.transferto.com/v1.1/transactions/fixed_value_recharges')
    return(services.text)

if __name__ == '__main__': 
    app.run(host= '0.0.0.0')
