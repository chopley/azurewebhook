from azurewebhook_functions import *
from flask import Flask, abort, request, logging 
import logging
import json



tf = Transferto()
tf.read_credentials_file("transfertocredentials.json")
