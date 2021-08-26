import json
import hashlib
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_trxs = []
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)