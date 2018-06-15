from flask import Flask, abort, request 
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/resource', methods = ['POST'])
def update_text():
  print(request.json)
  return json.dumps(request.json)

if __name__ == '__main__':
  app.run()
