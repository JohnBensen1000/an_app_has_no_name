import socket 
  
  
def Main(): 
	host = '127.0.0.1'
	port = 5809
  
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
	s.connect((host,port)) 

	message = input("UserID: ")
	try:
		s.send(message.encode('ascii')) 
		while True: 
			data = s.recv(1024) 

			print('Received from the server :',str(data.decode('ascii'))) 

	except KeyboardInterrupt:
		s.close()

if __name__ == '__main__': 
    Main() 

# import socket 
   
# # take the server name and port name 
   
# host = 'local host'
# port = 6000
   
# # create a socket at client side 
# # using TCP / IP protocol 
# s = socket.socket(socket.AF_INET, 
#                   socket.SOCK_STREAM) 
   
# # connect it to server and port  
# # number on local computer. 
# s.connect(('127.0.0.1', port)) 
   
# # receive message string from 
# # server, at a time 1024 B 
# msg = s.recv(1024) 
   
# # repeat as long as message 
# # string are not empty 
# while msg: 
#     print('Recived:' + msg.decode()) 
#     msg = s.recv(1024) 
  
# # disconnect the client 
# s.close() 