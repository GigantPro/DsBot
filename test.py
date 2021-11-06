# import pymysql
# host = "127.0.0.1"
# user = "root"
# password = "Rtrtph74"
# db_name = "testBD"


# create_tabel = "CREATE TABLE IF NOT EXISTS '{tabel}'({args});"

# print('Connecting to data base...', end='')
# try:
#     connection = pymysql.connect(
#         host=host,
#         port=3306,
#         user=user,
#         password=password,
#         database=db_name,
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     print('Ok')
# except Exception as ex:
#     print('ERROR')
#     print(ex)
#     exit()
# else:
#     cur = connection.cursor()
#     try:
#         cur.execute(create_tabel.format(tabel='servers', args='id int AUTO_INCREMENT, ServerName varchar(32), ServerID int, AdminRoleName varchar(32), AdminRoleId int, CounterMembers int, CounterMaxWARNS int, WelcomeChatName varchar(32), WelcomeChatId int, WelcomeServerMessage varchar(32), WelcomeMessagePivate varchar(32), PRIMARY KEY (ServerID)'))
#     except Exception as ex:
#         print(create_tabel.format(tabel='servers', args='id int AUTO_INCREMENT, ServerName varchar(32), ServerID int, AdminRoleName varchar(32), AdminRoleId int, CounterMembers int, CounterMaxWARNS int, WelcomeChatName varchar(32), WelcomeChatId int, WelcomeServerMessage varchar(32), WelcomeMessagePivate varchar(32), PRIMARY KEY (ServerID)'))
#         print('ERROR', ex)
d = int(input())
m = int(input())
e = int(input()) 
c = int(e / 100)
y = ((e - c) % 100) 

r = d + ((13 * m - 1) // 5) + y + (y // 4 + c // 4 - 2 * c + 777)
r %= 7
print(r)