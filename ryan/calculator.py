final_ans = 0
first_round = True   
numbers = []
operators = []

while True:
    if first_round: 
        ask_num1 = input("Enter number: ")
        if not ask_num1.isdigit():
            print("Unknown number entered, stopping code...")
            break
        numbers.append(int(ask_num1))


    
    ask_symbol = input("What symbol, example is +, -, *, / : ")
    if ask_symbol not in ['+', '-', '*', '/']:
        print("Unknown symbol entered, stopping code...")
        break
    operators.append(ask_symbol)


    ask_num2 = input("Enter number: ")
    if not ask_num2.isdigit():
        print("Unknown number entered, stopping code...")
        break
    numbers.append(int(ask_num2))



   
    # if ask_symbol == '+':
    #     final_ans = num1 + num2
    # elif ask_symbol == '-':
    #     final_ans = num1 - num2
    # elif ask_symbol == '*':
    #     final_ans = num1 * num2
    # elif ask_symbol == '/':
    #     final_ans = num1 / num2




    ask_repeat = input("Is that all? Type 'done' or 'no': ")

    if ask_repeat == "done":
        len_operator  = len(operators)
        # print(numbers)
        # print(operators)

        temp_op_index = -1
        for index in range(len_operator):
            if operators[index] == "/":
              if len(numbers) > 2:
                div_1 = (numbers[index])
                div_2 = (numbers[index + 1])
                div_ans = int(div_1 / div_2)
                numbers.pop(index)
                numbers.pop(index)
              else:
                div_1 = (numbers[index - 1])
                div_2 = (numbers[index])
                div_ans = int(div_1 / div_2)
                numbers.pop(index)
              numbers.insert(index, div_ans)
              temp_op_index = index  

        if temp_op_index >= 0 :
            operators.pop(temp_op_index)
        temp_op_index = -1

        len_operator  = len(operators)
        for index in range(len_operator):
            print("numbers: ", numbers)
            print("operators: ", operators)
            print("index: ", index)
            if operators[index] == "*":
              if len(numbers) > 2:
                mul_1 = (numbers[index])
                mul_2 = (numbers[index + 1])
                mul_ans = int(mul_1 * mul_2)
                numbers.pop(index)
                numbers.pop(index)
                print("After Popping: ", numbers)
              else:
                print("numbers: ", numbers)
                print("operators: ", operators)
                print("index: ", index)
                mul_1 = (numbers[0])
                mul_2 = (numbers[1])
                mul_ans = int(mul_1 * mul_2)
                numbers.pop(0)
                numbers.pop(0)
              numbers.insert(index, mul_ans)
              temp_op_index = index

        if temp_op_index >= 0 :
            operators.pop(temp_op_index)
        temp_op_index = -1

        break
    elif ask_repeat == "no":
        first_round = False
        continue
    else:
        print("Unknown choice, stopping code...")
        break

print(numbers)



 
