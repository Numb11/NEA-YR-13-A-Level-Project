import MySQLdb,socket,threading,mysql.connector
from PIL import Image

def receive_message(port,meta,IP):
    if connect(IP,port):
        data = s.recv(port)
        data = data.decode(data)
        if data[1] == meta:
            send_message(True,"#9",IP,port)
            return decompress(data[0][0],data[0][1],data[0][1][0],[0][1][1])
        
def decompress(data,technique,image,file):
    if technique == 'lossless':
        if image:
            return RLD(data)
        else:
            return dict_decode(data,file)
    elif technique == "lossy":
        return data

def RLD (metadata):
    rgbs = []
    new = Image.new(metadata[1], metadata[0], "white")
    for row in range(new.size[0]):
        for col in range(new.size[1]):
            new.putpixel((row,col),int(rgbs[counter]))
            counter = counter + 1
    new.save('temp.png')
    
def dict_decode(data,file):
    dict = data[0]
    text = data[1]
    counter = 0
    if file:
        text = dict_decode(data,False)
        f = open("temp1.txt","a")
        f.writelines(text)
        f.close()
    else:
        for i in text:
            for x in list(dict.keys()):
                if i == dict[x]:
                    text[text.index(i)] = x
            return " ".join(text)
    
def send_message(data,meta,IP,port):
    timeout = 0
    if connect() and timeout<5:
        data.encode()
        meta.encode()
        s.sendto([data,meta],(IP,port))

def connect(IP,port):
    s.connect((IP,port))
    s.sendall("#3")
    return receive_message(8081,"#3",IP,port)

def hash(value):
    hash_val = 0
    hashed = []
    for i in value[::-1]:
        hashed.append((ord(i)) + 10)
    for i in hashed:
        hash_val = i + hash_val-66
    return hash_val

class ThreadC(threading.Thread):
    def __init__(self,clientsocket,clientaddress,clientID):
        threading.Thread.__init__(self)
        self.client_socket = clientsocket
        self.client_address = clientaddress
        self.UID = clientID
    
    def send_message(self,recipient,message):
        cursor = db.cursor()
        cursor.execute(f"UPDATE users SET inbox = {message} WHERE uid ={recipient}")
        db.commit()
    
    def client_info(self):
        return [self.client_socket,self.client_address,self.UID]
        
    def update(self):
        cursor = db.cursor()
        cursor.execute(f"SELECT {self.UID} FROM users")
        data = cursor.fetchall()
        return send_message(data,"#1",self.client_address)
    
    
#Constants
PORT = 8081
IP = "192.168.1.122"

#Databse creation
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
)

mycursor = db.cursor()
mycursor.execute("CREATE DATABASE cheese")
mycursor.execute("SHOW DATABASES")
for i in mycursor:
    print(i)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
