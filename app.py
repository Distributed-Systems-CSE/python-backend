from random import randint

from flask import Flask, jsonify, request, send_file
import requests
import os
import io
import json
import pickle
import threading

import utils
from utils import initialize_node, merge_chains

app = Flask(__name__)
app.logger.setLevel('INFO')
app.config['UPLOAD_FOLDER'] = 'uploads'

PEER_NODES = os.environ['PEER_NODES'].split()
SELF = os.environ.get('SELF')
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


@app.route('/getPeers', methods=['GET'])
def get_peers():
	return jsonify({
		"peers": PEER_NODES
	}), 200


@app.route('/getSelf', methods=['GET'])
def get_self():
	return jsonify({
		"self": SELF
	}), 200


@app.route('/getChain', methods=['GET'])
def get_chain():
	blockchain_data = []

	for block in node.blockchain.chain:
		# Convert Block object to dictionary
		block_data = {
			'index': block.index,
			'data': block.data,
			'previous_hash': block.previous_hash,
			'nonce': block.nonce,
			'hash': block.hash
		}
		blockchain_data.append(block_data)

	return jsonify({
		'chain': blockchain_data
	}), 200


@app.route('/upload', methods=['POST'])
def upload():
	if 'file' not in request.files:
		return "No file uploaded!", 400
	file = request.files['file']
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
	partitions = utils.partition_file(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
	os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

	fileinfo = {
		'filename': file.filename,
		'content-type': file.content_type,
		'chunks-info': []
	}
	i = 0
	for partition in partitions:
		selected_node = PEER_NODES[randint(0, len(PEER_NODES) - 1)]
		fileinfo['chunks-info'].append({
			'index': i,
			'hash': partition['hash'],
			'node': selected_node
		})
		app.logger.info(f'Sending chunk to Node: {selected_node}')
		if selected_node == SELF:
			utils.write_partition(os.path.join(app.config['UPLOAD_FOLDER'], partition['hash']), partition['data'])
		else:
			requests.post(f'http://{selected_node}:5001/uploadChunk', files={partition['hash']: partition['data']})
		i += 1

	requests.post(f'http://{SELF}:5001/addBlock', json=fileinfo)
	return "OK", 200


@app.route('/uploadChunk', methods=['POST'])
def uploadChunk():
	app.logger.info('UploadChunk')
	if len(request.files) != 1:
		return "No file uploaded!", 400
	file = list(request.files.values())[0]
	app.logger.info(file.filename)
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
	return "OK", 200

@app.route('/getChunk', methods=['GET'])
def get_chunk():
	chunk_hash = request.args.get('hash')
	if (os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], chunk_hash))):
		return send_file(
			os.path.join(app.config['UPLOAD_FOLDER'], chunk_hash),
			as_attachment=True,
			download_name=chunk_hash,
			mimetype='application/octet-stream'
		)
	else:
		return "Chunk not found", 404