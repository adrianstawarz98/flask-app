from collections import Counter
from app import OrderedCounter

lista = ["nello", "no", "no"]
print(list(OrderedCounter(lista).values()))