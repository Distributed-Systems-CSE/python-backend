from flask import Flask, jsonify, request, send_file
import requests
import os
import json
import socket
import pickle
import threading
from utils import initialize_node, merge_chains

app = Flask(__name__)

os.environ['NODE_ID'] = '1' # Remove later
PEER_NODES = ['flask_app2']
node = initialize_node()

@app.route('/addBlock', methods=['POST'])
def add_block():
    data = request.json
    node.blockchain.add_block(data)

    # for peer in PEER_NODES:
    #     requests.post(
    #         f'http://{peer}:5001/gossip', 
    #         data={
    #         "origin": socket.gethostname()
    #         }, 
    #         files={'node.pkl': pickle.dumps(node)}
    #     )

    return jsonify({
        "message": "Data received successfully",
        "length": len(node.blockchain.chain)
        }), 200

@app.route('/gossip', methods=['POST'])
def get_gossip():
    data = request.json
    origin = data['origin']

    if 'node.pkl' in request.files:
        # Read the pickle file from the request
        node_bytes = request.files['node.pkl'].read()
        peer_node = pickle.loads(node_bytes)

        # Merge the peer's chain with our chain
        threading.Thread(target=merge_chains, args=(node.blockchain, peer_node.blockchain.chain)).start()
        # merge_chains(node.blockchain, peer_node.blockchain.chain)

    return jsonify({
        "message": "Gossip received successfully"
        }), 200

@app.route('/getNode', methods=['GET'])
def get_node():
    return send_file(
        io.BytesIO(pickle.dumps(node)),
        as_attachment=True,
        attachment_filename='node.pkl',
        mimetype='application/octet-stream'
    )

@app.route('/host', methods=['GET'])
def get_host():
    hostname = socket.gethostname()
    result = requests.get(
            f'http://flask-app2:5001/hello'
        )
    print(result.json())
    return jsonify({
        "message": hostname,
        "result": result.json()
        }), 200

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({
        "message": "Hello World"
        }), 200