import time
import web3
import smart_config


def smart(wallet, amount):
    # связываемся с тестовой нодой эфира через infura
    w3 = web3.Web3(web3.HTTPProvider(smart_config.web_address))
    # вводим адрес и abi смарт-контракта
    test = w3.eth.contract(address=smart_config.contract_address, abi=smart_config.contract_abi)
    # расчитываем количество транзакций кошелька
    # тут можно подставить свой адрес кошелька
    nonce = w3.eth.getTransactionCount(smart_config.botAccount)
    # составляем транзакцию, вызывающую функцию смарт-контракта
    test_txn = test.functions.mint(
        wallet, amount,
    ).buildTransaction({
        # id сети
        'chainId': 3,
        # количество газа, которое мы используем
        'gas': 70000,
        # цена за газ
        'gasPrice': w3.toWei('1', 'gwei'),
        # тут вводится тот самый рассчёт количества транзакций
        'nonce': nonce,
    })
    # приватный ключ кошелька
    private_key = '7666D6EB690D0F08473B3E4C975282CC1043F5F6AC343B5516683E8D7391F52A'
    # подписываем транзакцию
    signed_txn = w3.eth.account.signTransaction(test_txn, private_key=private_key)
    # отправляем подписанную транзакциюи получаем хэш
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    # конструкция ниже отвечает за получение информации об транзакции (добавлена в блокчейн или нет)
    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
        print(txn_receipt)
        time.sleep(10)
    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}
    return {'status': 'added', 'txn_receipt': txn_receipt}


# wallet = '0xF64C632A0A35454Bd31Ecb91692F25254DEd1594'
# amount = 1
# a = smart(wallet, amount)
# print(a)
