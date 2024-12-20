# Initializing our blockchain list
blockchain = []


def get_last_blockchain_value():
    """Returns the last value of the current blockchain."""
    return blockchain[-1]


# This function accepts two arguments.
# One required one (transaction_amount) and one optional one (last_transaction)
# The optional one is optional because it has a default value => [1]
def add_value(transaction_amount, last_transaction=[1]):
    """Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
      :transaction_amount: The amount that should be added.
      :last_transaction: The last blockchain transaction (default [1])
    """
    blockchain.append([last_transaction, transaction_amount])


def get_transaction_value():
    """Returns the input of the user (a new transaction amount) as a float"""
    # Get the use input, transform it from a string to a float and store it
    return float(input("Your transaction amount please: "))


def get_user_choice():
    return input("Your choice: ")


def print_blockchain_elements():
    # Output the blckchain list to the console
    for block in blockchain:
        print("Outputing Block")
        print(block)


# Get the first transaction input and add the value to the blockchain
tx_amount = get_transaction_value()
add_value(tx_amount)

while True:
    print("Please choose")
    print("1: Add a new transaction value")
    print("2: Output the blockchain blocks")
    user_choice = get_user_choice()
    if user_choice == "1":
        tx_amount = get_transaction_value()
        add_value(tx_amount, get_last_blockchain_value())
    else:
        print_blockchain_elements()


print("Done!")
