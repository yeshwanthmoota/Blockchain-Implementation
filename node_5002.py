# Creation of a General Blockchain


# Importing the libraries
import datetime
from unicodedata import category
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import json # to use json dumps to encode the blocks before hashing them
import hashlib
import time
import pdb
import requests
from urllib.parse import urlparse

# Part 1 -> Building a Blockchain

class Blockchain():

    def __init__(self):
        self.chain = [] # initialize an empty Blockchain
        self.transactions = []
        self.nodes = set()
        self.prefix_zeros = 4
        """prefix zeros represents mining difficulty """
        print("Hello World!")

        ### Mining the first Block
        nonce = 1
        self.add_transaction(sender = "Coinbase", reciever = "Rajavardhan", amount=50)
        block = {
            'index': len(self.chain) + 1,
            'proof': nonce,
            'previous_hash': "0",
            "transactions": self.transactions
        }
        self.transactions = []
        condition = True
        while(condition):
            block["proof"] = nonce
            hash_operation = self.hasher(block)
            if hash_operation[:self.prefix_zeros] != self.prefix_zeros*"0":
                nonce +=1
            else:
                condition = False
        block["timestamp"] = str(datetime.datetime.now())
        block["hash"] = self.hasher(block)
        self.chain.append(block)

        


    def create_block(self, proof):
        """ Here the proof is the 'nonce' value associated with each block in the blockchain which change the value of the block's hash
        so that the block's hash is less than or equal to the target hash."""
        # index of the block, timestamp of creation of the block, proof found when mining the block, previous hash
        temp = self.get_previous_block()
        block = {
            'index': temp["index"] + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': temp["hash"],
            'transactions': self.transactions
        }
        current_block_hash = self.hasher(block)
        self.transactions = []
        block["hash"] = current_block_hash
        self.chain.append(block)
        return block # we want to display the information(the keys here) about this block in postman


        
    def get_previous_block(self):
        return self.chain[-1]



    def proof_of_work(self, previous_block):

        """This function creates the PROBLEM that the miners need to solve"""

        # if (len(self.chain)) % 3 == 0: # increasing the difficulty of the network every 3 blocks(3 is just for testing in bitcoin it is 2016 blocks)
        #     self.prefix_zeros += 1

        nonce = 1
        check_proof = False
        checker = self.prefix_zeros * "0"

        while(check_proof is False):
            # The more leading zeroes we impose the harder it will be for the miners to mine the block
            hash_operation = hashlib.sha256( ( str(previous_block["index"] + 1) + str(previous_block["hash"]) + str(self.transactions) + str(nonce) ).encode() ).hexdigest() # The order here is super important
            if hash_operation[:self.prefix_zeros] != checker: # four leading zeroes
                nonce += 1
            else:
                check_proof = True
        return nonce
        
    
    def hasher(self, block): 
        return hashlib.sha256( ( str(block["index"]) + str(block["previous_hash"]) + str(block["transactions"]) + str(block["proof"]) ).encode() ).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0] # Genesis Block
        block_index = 2 # Block next to the Genesis Block Since the Block index of the Genesis Block is '1'
        checker = self.prefix_zeros * "0"
        while block_index <= len(chain):
            block = chain[block_index - 1]
            if block["previous_hash"] != previous_block["hash"]:
                print("Test1 failed")
                return False
            # hash_operation = self.hasher(block)
            hash_operation = block["hash"]
            if hash_operation[:self.prefix_zeros] != checker:
                print("Test2 failed")
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, reciever, amount):
        self.transactions.append({
            "sender": sender, 
            "reciever": reciever,
            "amount" : amount
        })
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def update_chain(self):
        longest_chain = self.chain
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f"http://{node}/get_blockchain")
            if response.status_code == 200:
                dict1 = response.json()
                length = dict1["length"]
                chain = dict1["chain"]
                if (length > max_length) and self.is_chain_valid(chain): # Also checking if the chain of the node we got using get request is a valid chain
                    print("HERE INSIDE" + "------------------5--------------") ### 5
                    print("\n")
                    max_length = length
                    longest_chain = chain
        self.chain = longest_chain # Updating the chain

# Part 2 -> Mining our Blockchain

# Creating a Web app

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

node_address = "Rajavardhan"

# Creating a Blockchain
blockchain = Blockchain()



# Get the Full Blockchain
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")
@app.route("/get_blockchain", methods = ["GET"])
def get_blockchain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response), 200 # 200 is the http code for success.



# Mining a new Block

@app.route("/mine_block", methods = ["GET"])
def mine_block():
    # previous_proof = previous_block["proof"]
    start_time = time.time()    
    # proof = blockchain.proof_of_work(previous_proof=previous_proof)
    blockchain.add_transaction(sender = "Coinbase", reciever = node_address, amount=50)
    proof = blockchain.proof_of_work(previous_block=blockchain.get_previous_block())
    end_time = time.time()
    time_taken = end_time - start_time
    previous_block = blockchain.get_previous_block()
    block = blockchain.create_block(proof = proof)
    response = {
            'message': 'Congratulations! You just mined a block!',
            'index': block['index'],
            'timestamp': block['timestamp'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'hash': block['hash'],
            'time taken to mine the block(in seconds)': time_taken,
            "transactions": block["transactions"]
        }
    return jsonify(response), 200 # 200 is the http code for success.



# Checking if the chain is valid
@app.route("/is_valid", methods = ["GET"])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        return "<h1>The Chain is VALID All good to go</h1>"
    else:
        return "<h1>The Chain is NOT VALID</h1>"


# Adding a new transaction
@app.route("/add_new_transaction", methods = ["GET", "POST"])
def add_new_transaction():
    if request.method == "GET":
        return render_template("new_transaction.html")
    else: # request.method is "POST"
        sender = request.form["sender"]
        reciever = request.form["reciever"]
        amount = request.form["amount"]
        blockchain.add_transaction(sender = sender, reciever =  reciever, amount = amount)
        if sender == "" or reciever == "" or amount == 0:
            flash("Required Fields not filled", category="danger")
            return redirect(url_for("add_new_transaction"))
        else:
            return redirect(url_for("get_blockchain"))




# Part - 3 Decentralizing the Blockchain

# connecting new nodes to the network
@app.route("/connect_node", methods = ["GET", "POST"])
def connect_node():
    if request.method == "GET":
        return render_template("new_node.html")
    else:
        nodes = request.form["node_addresses"]
        nodes = nodes.split(",")
        if nodes is None:
            return "No nodes to connect", 400
        else:
            for node in nodes:
                blockchain.add_node(node)
            response = {
                "message": "All the nodes are successfully connected to the network. The following nodes are present in the Bitcoin Blockchain Network:",
                "nodes": list(blockchain.nodes)
                }
            return jsonify(response), 200

# Updating the chain by the longest chain if necessary
@app.route("/update_chain", methods = ["GET"])
def update_chain():
    blockchain.update_chain()
    return "<h1>The Chain is Updated, All good to go!</h1>"
    


# Running the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)


