from flask import Flask, abort, request, logging, requests
import logging
import json

from azurewebhook_functions import *

app = Flask(__name__)

@app.route('/')
def home_screen():
    return 'Hmmmm!'

@app.route('/getProducts', methods = ['POST'])
def get_product_object():
    """
    End point to return the products associated with a phone number
    """
    json_data = request.get_json()
    tf = Transferto() 
    tf.read_credentials_file("transfertocredentials.json") 
    tf.initiate_rapidpro_json(json_data)
    products = tf.get_msisdn_products()
    return(json.dumps(products))

@app.route('/addData', methods = ['POST'])
def add_data_object():
    """
    End point to actually load data onto a phone number
    """
    json_data = request.get_json()
    tf = Transferto()  
    tf.read_credentials_file("transfertocredentials.json") 
    tf.initiate_rapidpro_json(json_data)
    tf.get_msisdn_products()
    tf.get_product_id()
    tf.payload_generation()
    services = tf.post_transferto_goods('https://api.transferto.com/v1.1/transactions/fixed_value_recharges')
    return(services.text)

@app.route('/rapidpro', methods = ['POST'])
def add_rapidpro_object():
    """
    End point to actually load data onto a phone number
    """
    json_data = request.get_json()
    tf = Transferto() 
    tf.read_credentials_file('credentials.json') 
    print(json_data['contact']['urn'])
    #tf = Transferto()  
    #tf.initiate_rapidpro_json(json_data)
    return(json.dumps(json_data['flow']))

if __name__ == '__main__': 
    app.run(host= '0.0.0.0')
