from functools import reduce
import hashlib as hl
from collections import OrderedDict
import json
import pickle

from hash_util import has_string_256, hash_block
from block import Block

# The reward we give to miners (for creating a new block)
MINING_REWARD = 10
# Initializing our (empty) blockchain list
blockchain = []
# Unhandled transactions
open_transactions = []
owner = "Sender name"
participants = {"Sender name"}


def load_data():
    global blockchain
    global open_transactions
    try:
        with open("blockchain.txt", mode="r") as f:
            # file_content = pickle.loads(f.read())
            file_content = f.readlines()

            # blockchain = file_content['chain']
            # open_transactions = file_content['ot']
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [
                    OrderedDict(
                        [
                            ("sender", tx["sender"]),
                            ("recipient", tx["recipient"]),
                            ("amount", tx["amount"]),
                        ]
                    )
                    for tx in block["transactions"]
                ]
                updated_block = Block(
                    block["index"],
                    block["previous_hash"],
                    converted_tx,
                    block["proof"],
                    block["timestamp"],
                )
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = OrderedDict(
                    [
                        ("sender", tx["sender"]),
                        ("recipient", tx["recipient"]),
                        ("amount", tx["amount"]),
                    ]
                )
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    except (IOError, IndexError):
        # Our starting block for the blockchain
        genesis_block = Block(0, "", [], 100, 0)
        # Initializing our (empty) blockchain list
        blockchain = [genesis_block]
        # Unhandled transactions
        open_transactions = []
    finally:
        print("Cleanup!")


load_data()


def save_data():
    try:
        with open("blockchain.txt", mode="w") as f:
            saveable_chain = [block.__dict__ for block in blockchain]
            f.write(json.dumps(saveable_chain))
            f.write("\n")
            f.write(json.dumps(open_transactions))
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transactions
            # }
            # f.write(pickle.dumps(save_data))
    except IOError:
        print("Saving failed!")


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()

    guess_hash = has_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == "00"


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    tx_sender = [
        [tx["amount"] for tx in block.transactions if tx["sender"] == participant]
        for block in blockchain
    ]
    open_tx_sender = [
        tx["amount"] for tx in open_transactions if tx["sender"] == participant
    ]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
        tx_sender,
        0,
    )
    tx_recipient = [
        [tx["amount"] for tx in block.transactions if tx["recipient"] == participant]
        for block in blockchain
    ]
    amount_received = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
        tx_recipient,
        0,
    )
    return amount_received - amount_sent


def get_last_blockchain_value():
    """Returns the last value of the current blockchain."""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction["sender"])
    return sender_balance >= transaction["amount"]


# This function accepts two arguments.
# One required one (transaction_amount) and one optional one (last_transaction)
# The optional one is optional because it has a default value => [1]
def add_transaction(recipient, sender=owner, amount=1.0):
    """Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
      :sender: The sender of the coins.
      :recipient: The recipient of the coins.
      :amount: The amount of coins sent with the transaction (default = 1.0)
    """
    # transaction = {"sender": sender, "recipient": recipient, "amount": amount}
    transaction = OrderedDict(
        [("sender", sender), ("recipient", recipient), ("amount", amount)]
    )
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    # hashed_block = str([last_block[key] for key in last_block])
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # reward_transaction = {
    #     "sender": "MINING",
    #     "recipient": owner,
    #     "amount": MINING_REWARD,
    # }
    reward_transaction = OrderedDict(
        [("sender", "MINING"), ("recipient", owner), ("amount", MINING_REWARD)]
    )
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = Block(len(blockchain), hashed_block, copied_transactions, proof)
    blockchain.append(block)
    return True


def get_transaction_value():
    """Returns the input of the user (a new transaction amount) as a float"""
    # Get the use input, transform it from a string to a float and store it
    tx_recipient = input("Enter the recipient of the transaction: ")
    tx_amount = float(input("Your transaction amount please: "))
    return tx_recipient, tx_amount


def get_user_choice():
    return input("Your choice: ")


def print_blockchain_elements():
    # Output the blckchain list to the console
    for block in blockchain:
        print("Outputing Block")
        print(block)
    else:
        print("-" * 20)


def verify_chain():
    for index, block in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(
            block.transactions[:-1], block.previous_hash, block.proof
        ):
            print("Proof of work is invalid")
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])
    # is_valid = true
    # for tx in open_transactions:
    #     if verify_transaction(tx):
    #         is_valid = True
    #     else:
    #         is_valid = False
    # return is_valid


waiting_for_input = True

while waiting_for_input:
    print("Please choose")
    print("1: Add a new transaction value")
    print("2: Mine a new block")
    print("3: Output the blockchain blocks")
    print("4: Output participants")
    print("5: Check transaction validity")
    print("q: Quit")
    user_choice = get_user_choice()
    if user_choice == "1":
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print("Added transaction!")
        else:
            print("Transaction failed!")
        print(open_transactions)
    elif user_choice == "2":
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == "3":
        print_blockchain_elements()
    elif user_choice == "4":
        print(participants)
    elif user_choice == "5":
        if verify_transactions():
            print("All transactions are valid")
        else:
            print("There are invalid transactions")
    elif user_choice == "q":
        waiting_for_input = False
    else:
        print("Input was invalid, please pick a value from the list!")
    if not verify_chain():
        print_blockchain_elements()
        print("Invalid blockchain!")
        # Break out of the loop
        break
    print("Balance of {}: {:6.2f}".format("Sender name", get_balance("Sender name")))
else:
    print("User left!")


print("Done!")
