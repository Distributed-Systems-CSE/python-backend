import base64
import os
import pickle
from localchain import Node, Blockchain
from hashlib import sha256

def initialize_node():
    node_id = os.environ.get('NODE_ID')
    pickle_file = f'{node_id}.pkl'

    if os.path.exists(pickle_file):
        # Load Node object from pickle file
        with open(pickle_file, 'rb') as f:
            node = pickle.load(f)
        print("Node object loaded from pickle file.")
    else:
        # Initialize a new Node object
        node = Node(node_id)
        print("New Node object initialized.")

        # Save Node object to pickle file
        with open(pickle_file, 'wb') as f:
            pickle.dump(node, f)
        print("Node object saved to pickle file.")

    return node

def merge_chains(blockchain, peer_chain):
    if len(peer_chain) < len(blockchain.chain):
        print("No need to merge if the peer's chain is shorter to our chain")
        return  # No need to merge if the peer's chain is shorter or equal to our chain

    common_index = 0
    for i, (peer_block, local_block) in enumerate(zip(peer_chain, blockchain.chain)):
        if peer_block.hash != local_block.hash:
            break
        common_index = i + 1
    print("common_index: ", common_index)

    if common_index == len(blockchain.chain):
        print("Fast forward local chain merge")
        blockchain.chain = peer_chain
    elif common_index < len(blockchain.chain) and common_index < len(peer_chain):
        # Fork found, merge divergent branches
        # Replace the current chain with a new chain that incorporates transactions from both branches
        print("Peer chain divergent from our local chain")
        merged_chain = Blockchain()
        merged_chain.chain = blockchain.chain[:common_index]
        # Add peer updates
        for block in peer_chain[common_index:]:
            merged_chain.add_block(block.data)
        # Add rest
        for block in blockchain.chain[common_index:]:
            merged_chain.add_block(block.data)
        blockchain = merged_chain

def partition_file(file_path, chunk_size=16 * 1024):
    partitions = []
    with open(file_path, 'rb') as f:
        chunk = f.read(chunk_size)
        chunk_number = 0
        while chunk:

            partitions.append({
                'hash': sha256(chunk).hexdigest(),
                'data': chunk
            })
            chunk_number += 1
            chunk = f.read(chunk_size)

    return partitions