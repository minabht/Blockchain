import json
import hashlib
import requests
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_trxs = []
        self.nodes=set()
        self.new_block(proof=100,previous_hash=1)

    def new_block(self,proof,previous_hash=None):
        #create a new block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_trxs,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_trxs = []
        self.chain.append(block)

        return block

    def new_trx(self,sender,recipient,amount):
        #add a new trx to the mempool
        self.current_trxs.append({'sender':sender,'recipient':recipient,'amount':amount})

        return self.last_block['index'] + 1

    def register_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self,chain):
        last_block=chain[0]
        index=1
        while index < len(chain):
            block=chain[index]
            if block['previous_hash']!=self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'],block['proof']):
                return False

            index+=1
            last_block=block

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_len=len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_len and self.valid_chain(chain):
                    max_len = length
                    new_chain = chain

        if new_chain:
            self.chain=new_chain
            return True

        return False

    @staticmethod
    def hash(block):
        #hash a block
        block_string = json.dumps(block,sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        #return the last block
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof,proof):
        #checks the validation of a proof
        this = f'{last_proof}{proof}'.encode()
        this_hash = hashlib.sha256(this).hexdigest()
        return this_hash[:4] == "0000"

    def proof_of_work(self,last_proof):
        #shows that the work is done
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

#-------------------------------------------------------------

app = Flask(__name__)
node_id = str(uuid4())

blockchain = Blockchain()

@app.route('/mine')
def mine():
    #mine a new Block and will add it to the chain
    last_block=blockchain.last_block
    last_proof=last_block['proof']
    proof=blockchain.proof_of_work(last_proof)

    blockchain.new_trx(sender="0", recipient=node_id, amount=6.25)
    previous_hash=blockchain.hash(last_block)
    block=blockchain.new_block(proof,previous_hash)

    response = {
        'message': 'New block created',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

@app.route('/trxs/new',methods=['POST'])
def new_trx():
    #add a new trx
    values = request.get_json()
    this_block=blockchain.new_trx(values['sender'],values['recipient'],values['amount'])
    response= {'message' : f'will be added to block {this_block}'}
    return jsonify(response), 201

@app.route('/chain')
def full_chain():
    #return the full chain
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    print(values)
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve')
def consensus():
    replaced = blockchain.resolve_conflicts()
    response = {
        'message': 'New Chain replaced',
        'chain' : blockchain.chain
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=input('Enter a port number: '))