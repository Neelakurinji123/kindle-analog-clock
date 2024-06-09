from codecs import encode 

text = '''LoCura Mamá 08 Oscar D'León - Lloraras'''

#output = encode(text, encoding='latin_1', errors='strict')
#output = encode(text, encoding='latin_1', errors='backslashreplace')
output = encode(text, encoding='latin_1', errors='replace')


print('orig: ', text)
print('new: b', output)
print('new: ', output.decode('latin_1'))

