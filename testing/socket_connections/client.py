import socket 
  
  
def Main(): 
    host = '127.0.0.1'
    port = 5804
  
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    s.connect((host,port)) 

    message = "shaurya says geeksforgeeks"
    while True: 
        s.send(message.encode('ascii')) 
        data = s.recv(1024) 

        print('Received from the server :',str(data.decode('ascii'))) 
  
        ans = input('\nDo you want to continue(y/n) :') 
        if ans == 'y': 
        	message = input("Message: ")
        else: 
            break

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