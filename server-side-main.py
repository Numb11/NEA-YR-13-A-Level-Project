import MySQLdb,socket,threading,mysql.connector
from PIL import Image
import ast

#Encryption Functions ------------

def caesur(plaintext,shift):
  encrypted = []
  while True:      
   for i in plaintext:
      encrypted.append(chr(ord(chr(ord(i)+shift))+shift))
      
   encrypted = "".join(encrypted)
   return encrypted

def key_A_PUB(data):
    data = (list(map(lambda x: caesur(x,5),data)))
    return data

def key_D_PRIV(data):
    data = (list(map(lambda x: caesur(x,-2),data)))
    return data

def hash(value):
    hash_val = 0
    hashed = []
    for i in value[::-1]:
        hashed.append((ord(i)) + 10)
        
    for i in hashed:
        hash_val = i + hash_val-66
        
    return hash_val




#Message Functions ------------

def receive_message(meta):
    global nextm_buffer
    buffer = nextm_buffer       #Adding previous received data to buffer
    data = ""
    terminator_pos = -1         #By default no terminator in transmission
    
    while terminator_pos == -1: #If equal to -1 ///n must exist
        
        buffer = buffer + (clientsock.recv(1024).decode())
        terminator_pos = buffer.find("///n")
        if terminator_pos != -1:
            
            nextm_buffer = buffer[terminator_pos + 4:]
            
        data = buffer[:terminator_pos]
        buffer = buffer[terminator_pos + 1:]
        
        #Temporarily store any data received after terminator
        
    data = data.split("##,##")                        #Split message into parts
    print(data,"received")
    if data[-2] == "True" or data[-2] == True:        #Check if image received
        
       image_info = data[0].split(";#;")              #Split image section
       image_meta = image_info[1]                     #Store corresponding image data
       image_data = image_info[0]                     #Store corresponding image data
       image_data = ast.literal_eval(image_data)      #Convert Data into correct form
       image_meta = ast.literal_eval(image_meta)      #Convert Data into correct form
       image_data = key_D_PRIV(key_A_PUB(image_data)) #Decrypt
       image_data = "".join(image_data)
       act_data = f"{image_data};#;{image_meta}"      #Store formatted data
       
    else:
       act_data = key_D_PRIV(key_A_PUB(data[0].split()))[0]
    print(act_data,"actual data")
    if data[1] == meta:
       return decompress(act_data,data[2],data[3],data[4])
   
    elif data[1] == "#8":
       return act_data,data[1],data[2],data[3],data[4]
   
    elif meta == None:
       return decompress(act_data,data[2],data[3],data[4]),data[1]
   
      
  
def decompress(data,technique,image,file):
    
    if image == True or image=="True":            #Images always RLE even if it has been lossy compressed before
            decoded = dict_decode(data[0],False)
            metadata = [decoded[2],decoded[1]]
            return RLD(decoded,metadata)
        
    if technique != None and technique != "None": #Apply the correct decompression method, text will always be dict_encoded
        return dict_decode(data,file)
    
    else:
        return data
    
    
    
def RLD(rgbs,metadata): 
    counter = 0
    new = Image.new(metadata[1],metadata[0],"white") #metadata[1] = im.mode and metadata[2] = im.size
    
    for row in range(new.size[0]):                   #Loop Collumns
        for col in range(new.size[1]):               #Loop Rows
            
            new.putpixel((row,col),(rgbs[counter]))
            counter = counter + 1
            
    new.save("temp.png")
    
    
    
def dict_decode(data,file):
    
    data = data.split("/,/")
    dict = ast.literal_eval(data[0])
    text = ast.literal_eval(data[1])
    
    if file == True:
        text = dict_decode(data,False)
        f = open("temp1.txt","a")
        f.writelines(text)
        f.close()
        
    else:
        for i in text:
            for x in list(dict.keys()):
                if i == dict[x]:
                    text[text.index(i)] = x
        return text



def dict_encode(data,file,image):
    dict = {}
    text = []
    counter = 0
    
    if file:        
        
        data = open(data)
        for line in data:
            text.append("/n")
            for x in (line).split():
                text.append(x)
        return dict_encode(" ".join(text),False)
    
    else:
        
        if not image:
           data = data.split()         
           data = list(map(lambda x: x.replace("/n","\n"),data))
           
        for i in data:
                        
            if not(i in dict.keys()):                
                dict[i] = counter
                data[data.index(i)] = dict.get(i)
                counter = counter + 1
                
            else:
                
                data[data.index(i)] = dict.get(i)
                
        return f"{dict}/,/{data}"   
    
    
    
def send_message(data,meta,image,file,comp_technique):
  print("Sending",data)
  if image == True or image == "True":
    data = data.split(";#;")
    image_meta = data[1]
    image_data = data[0]
    image_data = (key_D_PRIV(key_A_PUB(image_data)))
    to_be_sent = (f"{image_data};#;{image_meta}##,##{meta}##,##{comp_technique}##,##{image}##,##{file}///n").encode()
    clientsock.sendto(to_be_sent,(clientaddress[0],1024))
  else:
    print(data)
    data = "##,##".join((key_D_PRIV(key_A_PUB(data.split("##,##")))))
    to_be_sent = (f"{data}##,##{meta}##,##{comp_technique}##,##{image}##,##{file}///n").encode()
    clientsock.sendto(to_be_sent, (clientaddress[0],1024))
           
           
           
           
#Creating Client Thread ------------          

class ThreadC(threading.Thread):
    def __init__(self,clientsocket,clientaddress,clientID):
        threading.Thread.__init__(self)
        self.client_socket = clientsocket
        self.client_address = clientaddress
        self.UID = clientID
        self.recipient = ""
        print(f"{self.UID} has connected!")
        
        
        
    def run(self):
        global queryresult,db,address_book
        print("running")
        while True:
          address_book = []
          data = receive_message(None)
          if data[1] == "#1":                   #Update address 
              self.update()
              
          elif data[1] == "#1A":                #Update messages
              print(data)
              self.update_messages(data)
            
          elif data[1] =="#10":                 #Report
            self.report(data)
            
          elif data[1] == "#8":                 #Forward message
             self.forward_message(data)
        
          elif data[1] == "#11":                #Exit
              clientsock.close()
              break
          
          
          
          
    def update(self):    
        global address_book   
        mycursor.execute("""SELECT UID FROM main_database.user""")
        queryresult = (list(filter(lambda x: x[0] != self.UID, mycursor.fetchall())))
        
        for i in queryresult:
            address_book.append(i[0])
            
        send_message(dict_encode(" ".join(address_book),False,False),"#1",False,False,"lossless")
        
        
        
    def update_messages(self,data):
       global queryresult,messages
       
       query = """SELECT messages FROM main_database.messages WHERE UID = %s AND recipient = %s"""
       mycursor.execute(query,(self.UID,data[0][0]))
       queryresult = mycursor.fetchall()
       self.recipient = data[0][0]
       
       if queryresult[0][0] != None:    
                 
              print(queryresult)
              messages = queryresult[0][0].split("#,#,#")             
              send_message(str(len(messages)),"#1A",False,False,None)                 #Allow client to receive all messages
              print(messages,"253")  
              for i in messages:                                                      #Looping through inbox for recipient
                 message = i.split("#*#")                                             #split messages into parts
                 print(message)
                 print(message[0],message[1],message[3],message[4],message[2])
                 send_message(message[0],message[1],message[3],message[4],message[2]) #Send message as received
      
       else:
              send_message(" ","#8",None,False,False)
              queryresult = [(None,)]
       
       
       
    def forward_message(self,data):
        print("Forwarding Message")
        print(data)
        global queryresult
        comp_data = []
        
        for i in data: 
          comp_data.append(i)
          
        comp_data = "#*#".join(comp_data)
        print(comp_data)
        query = "UPDATE main_database.messages SET messages = %s WHERE (UID = %s and recipient = %s)"
        print(queryresult,"277")
        
        if queryresult[0][0] == None:
           queryresult = comp_data
           
        else:
           print(queryresult,"line 281")
           print(queryresult[0][0],comp_data)
           queryresult = (queryresult[0][0]+"#,#,#"+comp_data)
           
        print(queryresult,self.UID,self.recipient)
        mycursor.execute(query,(queryresult,self.UID,self.recipient))
        query = "UPDATE main_database.messages SET messages = %s WHERE (UID = %s and recipient = %s)"
        mycursor.execute(query,(queryresult,self.recipient,self.UID))
        db.commit()
        
        
          
    def report(self,data):
        reports = open("report.txt", "a")
        reports.write(f"{data[0][0]}, recipient:{data[0][1]},    Author:{self.UID}\n")
        reports.close()
       
       
       
           
#Key Global Variables ------------

nextm_buffer = ""
    
#Constants ------------

SPORT = 8081
SIP = "0.0.0.0"
BUFF_SIZE = 4096



#Database, Server Connection ------------

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="main_database"
)

mycursor = db.cursor()
#Creating client conneciton
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((SIP,SPORT))
print("Server Started, waiting for client connection...")


#Client Connection ------------



while True:
    
     s.listen(5)
     clientsock, clientaddress = s.accept()
     print(receive_message("#3"))
     send_message("True","#3",False,False,None)
     #Client now conencted Now needs to be authenticated
     data = receive_message("#2")
     data = data.split()
     query = """SELECT username,password FROM main_database.user WHERE UID = %s"""
     mycursor.execute(query,tuple(map(str, data[1].split())))
     queryresult = mycursor.fetchall()
     
     if (queryresult[0][0] + queryresult[0][1]) == int(data[0]): #Check if username nad password right
          send_message("True","#2",False,False,None) #User is now logged in and authenticated
          new_thread = ThreadC(clientsock,clientaddress,data[1])
          new_thread.start()
