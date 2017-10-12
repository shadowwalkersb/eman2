import xml.etree.ElementTree as ET
tree = ET.parse('merged.txt')
root = tree.getroot()

print root

# for child in root:
#     print(child.tag, child.attrib)
    
print root[0]

for i in range(len(root)):
    if root[i][4].text == "Inconsistent indentation: mix of tabs and spaces":
        # print i,
        for j in range(2):
            print root[i][j].text,
        print
