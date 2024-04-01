from flask import Flask, jsonify, request, send_file
import requests
import os
import io
import json
import pickle
import threading
from utils import initialize_node, merge_chains

app = Flask(__name__)

os.environ['NODE_ID'] = '1' # Remove later
PEER_NODES = ['flask-app2']
SELF = 'flask-app1'
node = initialize_node()

@app.route('/addBlock', methods=['POST'])
def add_block():
    data = request.json
    node.blockchain.add_block(data)

    for peer in PEER_NODES:
        requests.post(
            f'http://{peer}:5001/gossip', 
            data={
            "origin": SELF
            }, 
            files={'node.pkl': pickle.dumps(node)}
        )

    return jsonify({
        "message": "Data received successfully",
        "length": len(node.blockchain.chain)
        }), 200

@app.route('/gossip', methods=['POST'])
def get_gossip():
    if 'node.pkl' in request.files:
        file = request.files['node.pkl']
        file_content = file.read()
        peer_node = pickle.loads(file_content)
        origin = request.form.get('origin')

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
        download_name='node.pkl',
        mimetype='application/octet-stream'
    )

@app.route('/file', methods=['GET'])
def file():
    requests.post(
        'http://localhost:5001/send', 
        files={'node.pkl': pickle.dumps(node)}, 
        data={
            "origin": SELF
            }
        )
    return jsonify({
        "message": "Test successful"
        }), 200

@app.route('/send', methods=['POST'])
def send():
    file = request.files['node.pkl']
    # Read the file content
    file_content = file.read()

    # Deserialize the pickled data
    node = pickle.loads(file_content)

    # Get the origin from the request data
    origin = request.form.get('origin')

    # Do something with the file and origin
    print("Received file:", node)
    print("Origin:", origin)
    return jsonify({
        "message": "Test successful"
        }), 200