from collections import Counter
import json

# beginning
with open("msg_counter.json", 'r') as f:
    msg_counter = Counter(json.load(f))
phone_number = '123456789'
if msg_counter[phone_number] % 5 == 0:
    msg_counter[phone_number] += 1
    # send message
else:
    # don't send message but increment counter
    msg_counter[phone_number] += 1

# end
with open("msg_counter.json", 'w') as f:
    json.dump(msg_counter, f)


if __name__ == "__main__":
    pass