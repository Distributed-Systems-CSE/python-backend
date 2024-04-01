import hashlib
from datetime import datetime

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(
            str(self.index).encode() +
            str(self.data).encode() +
            str(self.previous_hash).encode() +
            str(self.nonce).encode()
        ).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def add_block(self, data):
        index = len(self.chain)
        previous_hash = self.chain[-1].hash
        new_block = Block(index, data, previous_hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.blockchain = Blockchain()
        self.peers = []

    def add_peer(self, peer):
        self.peers.append(peer)

    def sync_ledger(self):
        for peer in self.peers:
            peer_chain = self.get_peer_chain(peer)
            self.merge_chains(peer_chain)

    def get_peer_chain(self, peer):
        # Implement logic to request blockchain from peer
        pass

    def send_self_chain(self):
        return self.blockchain.chain

    def merge_chains(self, peer_chain):
        if len(peer_chain) < len(self.blockchain.chain):
            print("No need to merge if the peer's chain is shorter to our chain")
            return  # No need to merge if the peer's chain is shorter or equal to our chain

        common_index = 0
        for i, (peer_block, local_block) in enumerate(zip(peer_chain, self.blockchain.chain)):
            if peer_block.hash != local_block.hash:
                break
            common_index = i + 1
        print("common_index: ", common_index)

        if common_index == len(self.blockchain.chain):
            print("Fast forward local chain merge")
            self.blockchain.chain = peer_chain
        elif common_index < len(self.blockchain.chain) and common_index < len(peer_chain):
            # Fork found, merge divergent branches
            # Replace the current chain with a new chain that incorporates transactions from both branches
            print("Peer chain divergent from our local chain")
            merged_chain = Blockchain()
            merged_chain.chain = self.blockchain.chain[:common_index]
            # Add peer updates
            for block in peer_chain[common_index:]:
                merged_chain.add_block(block.data)
            # Add self rest
            for block in self.blockchain.chain[common_index:]:
                merged_chain.add_block(block.data)
            self.blockchain = merged_chain
