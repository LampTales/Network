a = [i for i in range(10)]
print(a)
a.sort(reverse=True)
a.append(1)
a.append(1)

a.remove(1)
print(a)