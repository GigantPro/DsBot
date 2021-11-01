# import sqlite3
# import string
# 
# base2 = '''کص, گاییدم, جنده, کونی, هرزه, کص کش, لاشی, نعشه, کیر, کوص, کس, کص, گایه'''
# base_convert = base.split(', ')
# base_convert2 = base.split(', ')
# print(base_convert)
# base = sqlite3.connect('baseff.bd')
# cur = base.cursor()
# for i in base_convert:
#     try:
#         cur.execute('INSERT INTO bads VALUES(?, ?)', (str(i), 0))
#         base.commit()
#         pass
#     except:
#         print('error')
# for i in base_convert2:
#     try:
#         cur.execute('INSERT INTO bads VALUES(?, ?)', (str(i), 0))
#         base.commit()
#         pass
#     except:
#         print('error')
global i 
i = 2
def test():
    while i < 3:
        i += 1
test()
print(i)