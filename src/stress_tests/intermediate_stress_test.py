import random
while True:
    o = random.randint(0,2)
    i1 = random.randint(-5,23)
    i2 = random.randint(-5,23)
    ans = ""
    cans = ""
    if o == 1:
        ans = input(str(i1)+"+"+str(i2)+"=")
        cans = i1+i2
    elif 0 == 2:
        ans = input(str(i1)+"-"+str(i2)+"=")
        cans = i1-i2
    else: 
        ans = input(str(i1)+"*"+str(i2-5)+"=")
        cans = i1*(i2-5)
    if cans!=int(ans):
        print("Incorrect Answer.")
    else:
        print("Correct answer. Waiting")

    
