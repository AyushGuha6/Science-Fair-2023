import random

t = random.randint(45,90)
if random.randint(0,1):
    print("Ice for " + t +" seconds")
else: 
    print("Count for " + t + " seconds")
    print(random.randint(0,25))