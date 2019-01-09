import time
from web3 import Web3, HTTPProvider

contract_address = 'YOUR CONTRACT ADDRESS'
wallet_private_key = 'YOUR TEST WALLET PRIVATE KEY'
wallet_address = 'YOUR WALLET ADDRESS'

w3 = Web3(HTTPProvider('YOUR INFURA URL'))
w3.eth.enable_unaudited_features()


def send_ether_to_contract(amount_in_ether):
    amount_in_wei = w3.toWei(amount_in_ether, 'ether')
    nonce = w3.eth.getTransactionCount(wallet_address)
    txn_dict = {
            'to': contract_address,
            'value': amount_in_wei,
            'gas': 2000000,
            'gasPrice': w3.toWei('40', 'gwei'),
            'nonce': nonce,
            'chainId': 3
    }
    signed_txn = w3.eth.account.signTransaction(txn_dict, wallet_private_key)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
        print(txn_receipt)
        time.sleep(10)
    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}
    return {'status': 'added', 'txn_receipt': txn_receipt}