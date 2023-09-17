import MySQLdb,socket
from guizero import App, Text, TextBox, PushButton, Window, Box, ListBox, Combo
from PIL import Image
import ast


#Encryption Functions ------------



def hash(value):
    hash_val = 0
    hashed = []
    
    for i in value[::-1]:
        hashed.append((ord(i)) + 10)
        
    for i in hashed:
        hash_val = i + hash_val-66
        
    return hash_val



def key_B_PRIV(data):
    data = (list(map(lambda x: caesur(x,-5),data)))
    return data

 
 
def key_C_PUB(data):
  data = (list(map(lambda x: caesur(x,2),data)))
  return data



def caesur(plaintext,shift):
  encrypted = []
  
  while True:
   encrypted = []
   
   for i in plaintext:
      encrypted.append(chr(ord(chr(ord(i)+shift))+shift))
      
   encrypted = "".join(encrypted)
   
   return encrypted



#Message Functions ------------



def receive_message(meta):
    print("RECEIVING MESSAGES")
    global nextm_buffer
    buffer = nextm_buffer                          #Add data received to buffer
    data = ""
    terminator_pos = -1                            #Is a terminator in the buffer
    print(terminator_pos)
    
    while terminator_pos == -1:                    #If equal to -1 ///n must exist #Add the other data in transmission
        
        buffer = buffer + (s.recv(1024).decode())
        print(buffer)
        terminator_pos = buffer.find("///n")
        if terminator_pos != -1:
            nextm_buffer = buffer[terminator_pos + 4:]
        data = buffer[:terminator_pos]
        buffer = buffer[terminator_pos + 1:]
              
    data = data.split("##,##")                        #Split message into parts
    
    if data[-2] == "True" or data[-2] == True:        #Check if image received
        
       image_info = data[0].split(";#;")              #Split image section
       image_meta = image_info[1]                     #Store correpsonding image data
       image_data = image_info[0]                     #Store correpsonding image data
       image_data = ast.literal_eval(image_data)      #Convert Data into correct form
       image_meta = ast.literal_eval(image_meta)      #Convert Data into correct form
       image_data = key_B_PRIV(key_C_PUB(image_data)) #Decrypt
       image_data = "".join(image_data)
       act_data = image_data,image_meta
       
    else:
        
       act_data = key_B_PRIV(key_C_PUB(data[0].split()))[0]
       
       
    print(act_data,"Actual Data")

    if data[1] == meta:
        
       return decompress(act_data,data[2],data[3],data[4])
   
    elif meta == None:
        
       return decompress(act_data,data[2],data[3],data[4])



def decompress(data,technique,image,file):
    if image == True or image=="True":             #Images always RLE even if it has been lossy compressed before
                    
            decoded = dict_decode(data[0],False)
            metadata = data[1]
            print(metadata)            
            return RLD(decoded,metadata)
    
    
    if technique != None and technique != "None":  #Apply the correct decompression method, text will always be dict_encoded
    
        print(data,technique)
        return dict_decode(data,file)
    
    else:
        return data



def RLD(rgbs,metadata):
    
    counter = 0
    print(metadata[1],metadata[0])
    new = Image.new(metadata[1],metadata[0],"white") #metadata[1] = im.mode and metadata[2] = im.size
    
    for row in range(new.size[0]): #Loop through each collumn
        for col in range(new.size[1]): #Every Row
            
            new.putpixel((row,col),(rgbs[counter]))
            counter = counter + 1
            
    new.save("Ctemp.png")
    new.show()



def dict_decode(data,file):
    
    counter = 0
    print("being decoded",data,file)
    
    if file == True or file == "True":
        
        text = dict_decode(data,False)
        print(text)
        text = list(map(lambda x: x+" " ,text))
        print(text)
        f = open("temp1.txt","w")
        f.writelines(text)
        f.close()
        
    else:
        
        data = data.split("/,/")
        dict = ast.literal_eval(data[0])
        text = ast.literal_eval(data[1])
        
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
        return dict_encode(" ".join(text),False,False)
    
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
    
        if image:
            imagedata = data[1]
            data = (key_B_PRIV(key_C_PUB(data[0])))
            print(data,"RLE")
            s.sendto((f"{data};#;{imagedata}##,##{meta}##,##{comp_technique}##,##{image}##,##{file}///n").encode(),(SIP,SPORT))
            
        else:
           data = "##,##".join((key_B_PRIV(key_C_PUB(data.split("##,##")))))
           s.sendto((f"{data}##,##{meta}##,##{comp_technique}##,##{image}##,##{file}///n").encode(),(SIP,SPORT))



def compress(data,technique,image,file):
    
    if technique == "lossless":
        if image:
            return RLE(data)
        else:
            return dict_encode(data,file,image)
        
    elif technique == "lossy":
        
        if image:
          return loss_comp(data)
      
        else:
           return dict_encode(data,file,image)



def RLE(image_path):
    
    rgbs = []
    im = Image.open(image_path)
    
    for row in range(im.size[0]):
        for col in range(im.size[1]):
            
            rgbs.append((im.getpixel((row,col))))
            
    return dict_encode(rgbs,False,True),[im.size,im.mode] 



def send_message(data,meta,image,file,comp_technique):
    
        if image:
            
            imagedata = data[1]
            data = (key_B_PRIV(key_C_PUB(data[0])))
            print(data,"RLE")
            s.sendto((f"{data};#;{imagedata}##,##{meta}##,##{comp_technique}##,##{image}##,##{file}///n").encode(),(SIP,SPORT))
            
        else:
            
           data = "##,##".join((key_B_PRIV(key_C_PUB(data.split("##,##")))))
           s.sendto((f"{data}##,##{meta}##,##{comp_technique}##,##{image}##,##{file}///n").encode(),(SIP,SPORT))



def loss_comp(image_path):
    im = Image.open(image_path)
    rgbs = []
    
    for row in range(im.size[0]):
        for col in range(im.size[1]):
            
            rgbs.append(im.getpixel((row-1,col)))
    
    return dict_encode(rgbs,False,True),[im.size,im.mode]


#Connection/Authentication ------------



def login(username,password):
    send_message((f"{hash(username)+hash(password)} {UID}"),"#2",False,False,None) #Update databse to have added username na dpassword stuff
    return receive_message("#2")



def connect():
    s.connect((SIP,8081))
    s.sendall(("None##,###3##,##None##,##False##,##False##,##None##,##///n").encode())
    return (receive_message("#3"))
   

#Graphical User Interface



def report(): 
  global username_recip,reportt
  reportwin = Window(app, title="report")
  reportt = TextBox(reportwin)
  username_recip = Combo(reportwin, options = address_book)
  PushButton(reportwin,command= rbutton, text="Report")



def rbutton():
    send_message(compress(f"{reportt.value} {username_recip.value}",comp_technique,False,False),"#10",False,False,comp_technique)
    mainwin.focus()
    
    
    
def lbuttoncommand():
    global mainwin,messages
    
    if connect() == "True":
        if login(username.value,password.value) == "True":
          global address_list_gui,address_book,messages_gui
          global messages,message
          heading.value = "Authenticated" 
          
          #GUI main window design
          
          mainwin = Window(app,title = "Chat Application")
          
          address_box = Box(mainwin,align="left",height = "fill")
          address_list_gui = ListBox(address_box, items=address_book,command = updatemessages)
          
          buttons_box = Box(address_box, width="fill",height ="150")
          PushButton(buttons_box, text="Settings", width="fill", align= "top", command = settings)        
          PushButton(buttons_box, text="Report",width="fill", align="bottom", command=report)              
          PushButton(buttons_box, text="File",width="fill", align="bottom",command = uploadfile)
          message_box = Box(mainwin, width="fill", align="bottom",height="30", border=True)
          PushButton(message_box, text="Send", align="right",command=send_butcommand)
          message = TextBox(message_box,width = "fill", height="fill", align="left")
          
          recipient_box = Box(mainwin, width="fill", height ="150", align="top")
          recipient = Text(recipient_box,text="Recipient:",align="left")
          
          messages_box = Box(mainwin,width = "fill", height="150",align="top")
          messages_gui = ListBox(messages_box,items = messages,width = "fill",height="fill",scrollbar=True)
          
          #Updating  address book
    
          send_message((f"None "),"#1",False,False,None)
          address_book = receive_message("#1")
          address_list_gui.clear()
          
          for i in address_book:
              
            address_list_gui.append(i)
            messages[i] = []
         
def lossless():
    global comp_technique
    comp_technique = "lossless"
    
def lossy():
    global comp_technique    
    comp_technique = "lossy"
    
def settings():
    
    global password,username
    settingswin = App(title="Settings",bg = "#3A3F47")
    settingswin.text_color = "white"
    settingswin.font = "Verdana"
    settingsbox = Box(settingswin , align = "left", height = "fill")
    Text(settingsbox,text = "Compression Technique:",size = 15)
    padding = Box(settingsbox , align = "top", height = 80,width = "fill")
    padding2 = Box(padding , align = "top", height = 10,width = "fill")
    Text(padding,align = "top", text = "The compresison technique will \n determine how files will be \n reduced in size before transmission.",size = 10)
    PushButton(settingsbox,width= "fill",text = "Lossless", command = lossless)
    padding = Box(settingsbox , align = "top", height = 20,width = "fill")
    PushButton(settingsbox,width="fill",text = "Lossy", command = lossy)


    compbox = Box(settingsbox,align = "right",height = "fill")
    Text(settingswin,text = "Account:",align = "top",size = 15)
    padding = Box(settingswin , align = "top", height = 10,width = "fill")
    Text(settingswin,text = f"Username: {username.value}")
    padding = Box(settingswin , align = "top", height = 10,width = "fill")
    Text(settingswin,text = f"Password: {password.value[0:2]}....")
    padding = Box(settingswin , align = "top", height = 20,width = "fill")
    
    
    
def exit():
    try:
     send_message((f"None "),"#11",False,False,None)
    except:
        pass
    app.destroy()


def updatemessages():
    
    global messages,address_book,recipient
    recipient = address_list_gui.value
    messages_gui.clear()
    #Updating messages corresponding with server and updating item list
    send_message(compress(recipient,comp_technique,False,False),"#1A",False,False,comp_technique)
    message_number = receive_message("#1A")
    
    if message_number != None: #error handling, what if no messages to be sent??
        
      for i in range(int(message_number)):
        message = receive_message(None) #Message data received
        message_history = messages[recipient]
        message_history.append(message)
        messages[recipient] = message_history
        messages_gui.append(message)
        
        
        
def send_butcommand():
    
    global address_book
    global messages
    send_message(compress(message.value,comp_technique,False,False),"#8",False,False,comp_technique)
    messages_gui.append(message.value)
    message_history = messages[recipient]
    #Compile stuck again ffs
    message_history.append(message.value)
    #dawdaw
    messages[recipient] = message_history
    message.clear()
   
    
    
def uploadfile():
    
    filepath = app.select_file(filetypes=[["Pictures","*.png"],["Pictures","*.jpg"],["Text documents","*.txt"]])
    if filepath.find("*.txt") < 0:
     img = Image.open(filepath)
     img = img.save('Ctemp.png')
     filepath = 'Ctemp.png'
     send_message(compress(filepath,comp_technique,True,False),"#8",True,False,comp_technique)
    else:
     send_message(compress(filepath,comp_technique,False,True),"#8",False,True,comp_technique)
    
    
    
#Constants ------------



SIP = "127.0.0.1"
SPORT = 8081
UID = "Harry@Taylor456"



#Key Variables ------------



nextm_buffer = "" #Store data after temrinator
comp_technique = "lossy"
address_book = ["Jude@Easton342","Nat@Gray111"]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
messages = {
    "Jude@Easton342":["Please can I have some  help with this work","temp.png","Yes!"],
    "Nat@Gray111":["When is the HWK due for maths?","03/11/22 I think"]
}



#Window Creation ------------



app = App(title="Chat Application")
app.when_closed = exit
heading = Text(app, text="Log-in")
username = TextBox(app)
password = TextBox(app, hide_text=True)
login_button = PushButton(app,command=lbuttoncommand, text="Log-in")
app.display()
