import time
import hashlib
import json


class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0, timestamp=None, miner=None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = timestamp or time.time()
        self.miner = miner
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "miner": self.miner,
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.transaction_pool = []

    def create_genesis_block(self):
        return Block(0, [], "Genesis")

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, tx):
        if self.is_valid_transaction(tx):
            self.transaction_pool.append(tx)
            return True
        return False

    def is_valid_transaction(self, tx):
        if tx["sender"] == "A":
            return self.get_balance("A") >= tx["amount"]
        return True

    def get_balance(self, address):
        balance = 100 if address == "A" else 0
        for block in self.chain:
            for tx in block.transactions:
                if tx["sender"] == address:
                    balance -= tx["amount"]
                if tx["receiver"] == address:
                    balance += tx["amount"]
        return balance

    def proof_of_work(self, block):
        while not block.hash.startswith("00"):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block

    def mine_pending_transactions(self, miner):
        if not self.transaction_pool:
            return None
        new_block = Block(
            index=len(self.chain),
            transactions=self.transaction_pool.copy(),
            previous_hash=self.get_last_block().hash,
            miner=miner
        )
        mined_block = self.proof_of_work(new_block)
        self.chain.append(mined_block)
        self.transaction_pool = []
        return mined_block

    def is_valid_chain(self, chain):
        for i in range(1, len(chain)):
            current = chain[i]
            prev = chain[i - 1]
            if current.previous_hash != prev.hash or current.hash != current.compute_hash():
                return False
        return True

    def resolve_chain(self, new_chain):
        if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
            self.chain = new_chain
            self.transaction_pool = []
            return True
        return False
