import json
import hashlib
from time import time

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

    def new_trx(self,sendor,recipient,amount):
        #add a new trx to the mempool
        self.current_trxs.append({'sender':sendor,'recipient':recipient,'amount':amount})

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        #hash a block
        block_string = json.dumps(block,sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        #return the last block
        pass