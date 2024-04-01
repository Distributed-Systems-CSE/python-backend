import requests
import pickle

# Define the URL of the Flask application
url = 'http://localhost:5002/getNode'

# Send a GET request to the /get_node endpoint
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Read the content of the response (pickled node object)
    node_bytes = response.content
    # Deserialize the pickled data into a Node object
    node = pickle.loads(node_bytes)
    # Print the data of the Node object
    print("Localchain valid?:", node.blockchain.is_chain_valid())
    print("Localchain length:", len(node.blockchain.chain))
else:
    print("Error:", response.status_code)
