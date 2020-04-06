
import json
import matplotlib.pyplot as plt

with open('node_volt.json', 'r') as f:
    voltage = json.load(f)

sec = []
pri = []
for v in voltage:
    if v['Phase'] == 's1' or v['Phase'] == "s2":
        volt = v['PNV']
        sec.append(volt[0]/120)
    
    if v['Phase'] == 'A' or v['Phase'] == "B" or v['Phase'] == "C":
        volt = v['PNV']
        if volt[0] < 8000 and volt[0] > 6000:
            pri.append(volt[0]/7200)

count = 0
for v in sec:
    if v < 0.95:
        count += 1
print(count)
count = 0
for v in pri:
    if v < 0.95:
        count += 1
print(count)
plt.plot(sec)
plt.show()

plt.plot(pri)
plt.show()
