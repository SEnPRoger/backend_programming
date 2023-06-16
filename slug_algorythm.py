import datetime
import random

# define an alphabet
alfa = "abcdefghijklmnopqrstuvwxyz"
current_date = datetime.datetime.now()
digit_pairs = []
output_slug = ""
id = 3

def generate_slug(current_date, id):
    global output_slug
    number = round(current_date.timestamp() // 1)
    number_str = str(number)
    
    for i in range(0, len(number_str)-1, 2):
        pair = int(number_str[i:i+2])
        digit_pairs.append(pair)

    for i in range(len(digit_pairs)):
        while(digit_pairs[i] > 26):
            digit_pairs[i] -= 26
        output_slug += alfa[digit_pairs[i]]

    while(id > 26):
        id -= 26
    output_slug += alfa[id]

    out_list = list(output_slug)
    random.shuffle(out_list)
    output_slug = ''.join(out_list)

    print(number)
    print(digit_pairs)
    print(output_slug)

    repeating_indices = [i for i, char in enumerate(output_slug) if output_slug.count(char) > 1]
    print(repeating_indices)
    print(output_slug)
    print(repeating_indices[1].upper())

generate_slug(current_date=current_date, id=id)