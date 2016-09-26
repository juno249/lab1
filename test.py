import re
query = "id>2 AND name=Tung OR name=Tra".replace(' ', '')
operations = re.split('AND|OR', query)
print(operations)
for operation in operations:
    print(re.findall(r"(?:\w+=\w+)+|(?:\w+|=|>|<|<>\w+)+", operation))