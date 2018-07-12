from flask import Flask, abort, request, logging, jsonify
import logging
import json
import requests
from urllib.parse import parse_qs
import urllib
from threading import Thread,active_count
import datetime
import math
import random
from queue import Queue

from azurewebhook_functions import *

# Define a function for the long running transferto thread
def process_wait(q):
    print('starting process')
    while True:
        try:
            json_data = q.get()
            tf = Transferto() 
            tf.read_transferto_credentials_file('transfertocredentials.json')
            tf.read_rapidpro_credentials_file('rapidprocredentials.json')
            tf.initiate_rapidpro_json(json_data)
            wait_time = math.floor(random.uniform(10,25))
            print(tf.get_rapidpro_fields()['transferto_status'])
            print(wait_time)
            time.sleep(wait_time)
            transferto_update = {'transferto_status' : "Success",
                                 'transferto_timestamp' : datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
            tf.write_rapidpro_fields(transferto_update)
            print("%s %s %s" %(transferto_update,
                               json_data['phone'],
                               tf.get_rapidpro_fields()['transferto_status'])
                               )
        except:
            print('bad thread')

# Define a function for the long running transferto thread
def process_transferto(q):
    while True:
        try:
            json_data = q.get()
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
            transferto_update = {'transferto_status' : dict_vals['status_message'],
                                 'transferto_timestamp' : datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}
            print(transferto_update)
            tf.write_rapidpro_fields(transferto_update)
            print("%s %s %s" %(transferto_update,
                       json_data['phone'],
                       tf.get_rapidpro_fields()['transferto_status']))
            print(json.dumps(services.json())) 
        except:
            print("bad thread didn't load %s" %(json_data['phone'])) 

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
    q.put(json_data)
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
    q.put(json_data)
    return jsonify(
        transferto_status='Starting',
        transferto_timestamp=datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    )


if __name__ == '__main__': 
    q = Queue(maxsize=0)
    num_threads = 1
    for i in range(num_threads):
        worker = Thread(target=process_transferto, args=(q,))
        worker.setDaemon(True)
        worker.start()
    print('active threads = ')
    print(active_count())
    app.run(host= '0.0.0.0')
