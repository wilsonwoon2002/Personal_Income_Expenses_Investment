import uuid


def generate_transaction_id():
    transaction_id = uuid.uuid4()
    return str(transaction_id)


# Example usage
transactions_without_id = 7
transaction_ids = []

for _ in range(transactions_without_id):
    transaction_id = generate_transaction_id()
    transaction_ids.append(transaction_id)

# Print the generated transaction IDs
for transaction_id in transaction_ids:
    print(transaction_id)