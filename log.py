data = open("design/log.txt",encoding='utf-8')
# line = data.readline()
# while line:
#     print(line)

s=data.read()
import re
d = re.findall("Spider error processing <GET (.*)>",s)
print(d)
print(len(d))