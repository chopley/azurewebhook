from flask import Flask, abort, request, logging, jsonify
import logging
import json
import requests
from urllib.parse import parse_qs
import urllib
from threading import Thread
import datetime
import math
import random

from azurewebhook_functions import *

# Define a function for the long running transferto thread
def process_wait(json_data):
    tf = Transferto() 
    tf.read_transferto_credentials_file('transfertocredentials.json')
    tf.read_rapidpro_credentials_file('rapidprocredentials.json')
    tf.initiate_rapidpro_json(json_data)
    wait_time = math.floor(random.uniform(10,25))
    print(tf.get_rapidpro_fields())
    print(wait_time)
    time.sleep(wait_time)
    transferto_update = {'transferto_status' : "Success",
                         'transferto_timestamp' : datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
    print(transferto_update)
    tf.write_rapidpro_fields(transferto_update)
    print(tf.get_rapidpro_fields())
    

# Define a function for the long running transferto thread
def process_transferto(json_data):
    tf = Transferto() 
    tf.read_transferto_credentials_file('transfertocredentials.json')
    tf.read_rapidpro_credentials_file('rapidprocredentials.json')
    tf.initiate_rapidpro_json(json_data) 
    fields = tf.get_rapidpro_fields()
    tf.get_msisdn_products()
    tf.get_product_id()
    tf.payload_generation()
    services = tf.post_transferto_goods('https://api.transferto.com/v1.1/transactions/fixed_value_recharges')
    dict_vals = services.json()
    print(dict_vals['status_message'])
    transferto_update = {'transferto_status' : "dict_vals['status_message']",
                         'transferto_timestamp' : datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
    print(transferto_update)
    tf.write_rapidpro_fields(transferto_update)
    print(json.dumps(services.json()))

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
    tf.read_transferto_credentials_file("transfertocredentials.json") 
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
    tf.read_transferto_credentials_file("transfertocredentials.json") 
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
    json_data = request.form
    print('hehre')
    print(json_data['run'])
    print(json_data['phone'])
    tf = Transferto() 
    tf.read_transferto_credentials_file('transfertocredentials.json')
    tf.read_rapidpro_credentials_file('rapidprocredentials.json')
    tf.initiate_rapidpro_json(json_data) 
    fields = tf.get_rapidpro_fields()
    tf.get_msisdn_products()
    tf.get_product_id()
    tf.payload_generation()
    services = tf.post_transferto_goods('https://api.transferto.com/v1.1/transactions/fixed_value_recharges')
    #return(services.text)
    print(json.dumps(services.json()))
    return(json.dumps(services.json()))

@app.route('/rapidprothreaded', methods = ['POST'])
def add_rapidpro_thread():
    """
    End point to actually load data onto a phone number
    """
    json_data = request.form   
    t = Thread(target=process_transferto, args=(json_data, ))
    t.start()
    return jsonify(
        transferto_status='Starting',
        transferto_timestamp=datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    )
@app.route('/wait', methods = ['POST'])
def add_wait_thread():
    """
    Testing end point
    """
    json_data = request.form   
    t = Thread(target=process_wait, args=(json_data, ))
    t.start()
    return jsonify(
        transferto_status='Starting',
        transferto_timestamp=datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    )


if __name__ == '__main__': 
    app.run(host= '0.0.0.0')
