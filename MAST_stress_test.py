import random

t = random.randint(45,90)
if random.randint(0,1):
    print("Ice for " +  str(t) +" seconds")
else: 
    print("Count for " + str(t) + " seconds")
    print(random.randint(3,25))