import math
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

def get_file_as_byte_stream(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def partition_stream(byte_stream, chunk_size=16 * 1024):
    partitions = []
    while byte_stream:
        chunk = byte_stream[:chunk_size]
        partitions.append({
            'hash': sha256(chunk).hexdigest(),
            'data': chunk
        })
        byte_stream = byte_stream[chunk_size:]
    return partitions


def padding_size(byte_stream, chunk_size=16 * 1024):
    """
	:param byte_stream:
	:return: size of padding need to be added.
	"""
    chunk_count = math.ceil(len(byte_stream) / chunk_size)
    # Find the next highest power of 2
    power_of_2 = 2 ** math.ceil(math.log(chunk_count, 2))
    padded_size = power_of_2 * chunk_size
    return padded_size - len(byte_stream)

def write_partition(file_path, chunk):
    with open(file_path, 'wb') as f:
        f.write(chunk)