import mysql.connector

try:
	connection = mysql.connector.connect(
		host='localhost',
		user='baidu_da',
		password='1!Asdfghjkl',
		auth_plugin='caching_sha2_password'
	)
	if connection.is_connected():
		print(f'Success! Connected to {connection.server_info}')
except mysql.connector.Error as e:
	print(f'error:{e}')
finally:
	if 'connection' in locals() and connection.is_connected():
		connection.close()
