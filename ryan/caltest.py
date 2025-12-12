numbers = [5, '-', 0]

error_count = 0

index = 0
len_num = len(numbers)
while index < len_num:
    # print("Index", index)
    # print("Length of Numbers", len(numbers))
    try:
        if len(numbers) == 1 :
            break
        if index == len(numbers): 
            break  
        if numbers[index] == '/':
            div_1 = int(numbers[index - 1])
            div_2 = int(numbers[index + 1])
            div_ans = div_1 / div_2

            del numbers[index-1:index+2]
            # print("Before Insert Division", numbers)

            numbers.insert(index-1, div_ans)
            # print("After Insert Division", numbers)

            index = 0   # 🔥 restart loop from beginning
        else:
            index += 1
    except ZeroDivisionError:
        error_count = 1
        print ("Division By Zero not Possible")
        break


len_num = len(numbers)

index = 0
len_num = len(numbers)
while index < len_num:
    # print("Index", index)
    # print("Length of Numbers", len(numbers))

    if len(numbers) == 1 :
        break
    if index == len(numbers): 
        break 

    if numbers[index] == '*':
        mul_1 = int(numbers[index - 1])
        mul_2 = int(numbers[index + 1])
        mul_ans = mul_1 * mul_2

        del numbers[index-1:index+2]
        # print("Before Insert Multiplication", numbers)

        numbers.insert(index-1, mul_ans)
        # print("After Insert Multiplication", numbers)

        index = 0   # 🔥 restart loop from beginning

    else:
        index += 1

index = 0
len_num = len(numbers)
while index < len_num:
    # print("Index", index)
    # print("Length of Numbers", len(numbers))

    if len(numbers) == 1 :
        break
    if index == len(numbers): 
        break  
    if numbers[index] == '+':
        add_1 = int(numbers[index - 1])
        add_2 = int(numbers[index + 1])
        add_ans = add_1 + add_2

        del numbers[index-1:index+2]
        # print("Before Insert Addition", numbers)

        numbers.insert(index-1, add_ans)
        # print("After Insert Addition", numbers)

        index = 0   # 🔥 restart loop from beginning
    else:
        index += 1

index = 0
len_num = len(numbers)
while index < len_num:
    # print("Index", index)
    # print("Length of Numbers", len(numbers))

    if len(numbers) == 1 :
        break
    if index == len(numbers): 
        break  

    if numbers[index] == '-':
        sub_1 = int(numbers[index - 1])
        sub_2 = int(numbers[index + 1])
        sub_ans = sub_1 - sub_2

        del numbers[index-1:index+2]
        # print("Before Insert Substraction", numbers)

        numbers.insert(index-1, sub_ans)
        # print("After Insert Substraction", numbers)

        index = 0   # 🔥 restart loop from beginning
    else:
        index += 1

if error_count == 0:
    print("Answer is :", numbers)
else :
    print("Please change the inputs to get the results")