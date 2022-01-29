# Blockchain-Implementation

Use Python 3.9.7   
  
required modules to be installed:  
flask, requests  
(Features of a mempool etc have not been implemented).  
Run The three nodes in python(node_5000.py, node_5001.py, node_5002.py) more can be made and configured  
The Three nodes run in different ports in the same computer, through this implementation decentralization is achieved  
  
1. First go to connect nodes and enter the two addresses of the nodes in there(local host with diff ports) can add multiple of them seperated by a ','.  
Then connect repeat this process for all the three flask servers running -> node_5000.py, node_5001.py, node_5002.py  
for example we connect server addresses of node_5001.py and node_5002.py to node_5000.py etc.  
2. Add New Transactions  
3. Then Mine a block in any one node  
4. update the chain in the other blocks and can also check the validity of your chain(the blockchain the server is running).  
5. see the results in the other blocks using Get Blockchain button in the Home page.  
