@app.route("/community", methods=["POST", "GET"])
def community():
    UserDataF = open('storage\\userData.txt','r')
    UsersData = eval(UserDataF.read())
    myUser = session['username']
    existsClient1 = False
    selectedChat = []
    currentChatName = request.form.get('chatName')
    memberName = request.form.get('memberName')
    if len(UsersData)>0:
        for ClientUser in UsersData:
            if ClientUser['user'] == myUser:
                existsClient1 = True
                break
            for ChatSpace in ClientUser['chat_spaces']:
                if ChatSpace['chat_name'] == currentChatName:
                    selectedChat = open(os.join('storage\\chats',currentChatName+ChatSpace['chat_members'][0]))
                    selectedChat = eval(selectedChat.read())
    
    #Adding the new member when accessed:
    #Now you can use the chat_name variable in your Flask route logic
    #Adding the new member when accessed

    if request.method == "POST":
        chat_name = request.form.get('newChatName')
        chat_code = request.form.get('newChatCode')
        currentChatName = request.form.get('chatName')
        memberName = request.form.get('memberName')
        print(memberName,currentChatName)
        Saved = None
        if len(UsersData)>0:
            existsClient = False
            for ClientUser in UsersData:
                existsChat = False
                if ClientUser['user'] == myUser:
                    existsClient = True
                    if len(ClientUser['chat_spaces'])>0:
                        for ChatSpaceOfUser in ClientUser['chat_spaces']:
                            if memberName!=None:
                                print(ChatSpaceOfUser, ClientUser)
                                if ChatSpaceOfUser['chat_name'] == currentChatName and memberName not in ChatSpaceOfUser['chat_members']:
                                    ChatSpaceOfUser['chat_members'].append(memberName)
                                    doesExist = False
                                    Saved = ChatSpaceOfUser
                                    if len(ChatSpaceOfUser['chat_members'])>1:
                                        for ClientUserX in UsersData:
                                            if ClientUserX['user'] == memberName:
                                                if Saved != None:
                                                    ClientUserX['chat_spaces'].append(Saved)
                                            with open('storage\\userData.txt','w') as file:
                                                file.write(str(UsersData))
                                                file.close()
                                            if ClientUserX['user'] != myUser and ClientUserX['user']!=memberName and ClientUserX['user'] in ChatSpaceOfUser['chat_members']:
                                                for ChatSpaceOfUserX in ClientUserX['chat_spaces']:
                                                    if ChatSpaceOfUserX['chat_name'] == currentChatName:
                                                        ChatSpaceOfUserX['chat_members'] = ChatSpaceOfUser['chat_members']
                                                        

                                            if ClientUserX['user']==memberName:
                                                doesExist = True

                                    if doesExist == False:
                                        ClientUserNew = {'user':memberName,'chat_spaces':[]}
                                        if Saved != None:
                                            ClientUserNew['chat_spaces'].append(Saved)
                                        UsersData.append(ClientUserNew)
                                    with open('storage\\userData.txt','w') as file:
                                        file.write(str(UsersData))
                                        file.close()
                                    chat_save_name = chat_name+ChatSpaceOfUser['chat_members'][0]+'.txt'
                                    with open(os.path.join('storage\\chats',chat_save_name),'w') as chat:
                                        file.close()

                            if ChatSpaceOfUser['chat_name'] == chat_name:
                                existsChat = True
                    
                    #We check if the chat exists for a particular user and if it doesnt exist, we make a new chat.            
                    if existsChat != True and chat_name != None and chat_code != None:
                        ChatSpaceOfUser = {'chat_name':chat_name,'chat_code':chat_code,'chat_members':[myUser]}
                        ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                        with open('storage\\userData.txt','w') as file:
                            file.write(str(UsersData))
                            file.close()
                        chat_save_name = chat_name+ChatSpaceOfUser['chat_members'][0]+'.txt'
                        with open(os.path.join('storage\\chats',chat_save_name),'w') as chat:
                            file.close()
                        
                        # Pass UserData to the frontend
                        return render_template("chat.html", existingChats=existingChats, userData=ClientUser['chat_spaces'],chatContents = selectedChat)
                        
                    else:
                        return render_template("chat.html",userData = ClientUser['chat_spaces'],chatContents = selectedChat)

            #We check if a particular user exists and if they dont exist, we create a new user
            if existsClient == False and chat_name!=None and chat_code !=None:
                ClientUser = {'user':myUser,'chat_spaces':[]}
                ChatSpaceOfUser = {'chat_name':chat_name,'chat_code':chat_code,'chat_members':[myUser]}
                ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                UsersData.append(ClientUser)
                with open('storage\\userData.txt','w') as file:
                    file.write(str(UsersData))
                    file.close()
                chat_save_name = chat_name+ChatSpaceOfUser['chat_members'][0]+'.txt'
                with open(os.path.join('storage\\chats',chat_save_name),'w') as chat:
                    file.close()
                # If the request method is GET, simply render the chat.html template
                return render_template("chat.html", existingChats=existingChats, userData=ClientUser['chat_spaces'],chatContents = selectedChat)
            
        #We check if ANY user exists in the database or if the new user is the FIRST user to join.
        else:
            if chat_name != None and chat_code != None:
                ClientUser = {'user':myUser,'chat_spaces':[]}
                ChatSpaceOfUser = {'chat_name':chat_name,'chat_code':chat_code,'chat_members':[myUser]}
                ClientUser['chat_spaces'].append(ChatSpaceOfUser)
                UsersData.append(ClientUser)
                with open('storage\\userData.txt','w') as file:
                    file.write(str(UsersData))
                    file.close()
                chat_save_name = chat_name+ChatSpaceOfUser['chat_members'][0]+'.txt'
                with open(os.path.join('storage\\chats',chat_save_name),'w') as chat:
                    file.close()
                # If the request method is GET, simply render the chat.html template
                return render_template("chat.html", existingChats=existingChats, userData=ClientUser['chat_spaces'],chatContents = selectedChat)
            else:
                if len(UsersData)>0 and existsClient1 == True:
                    return render_template("chat.html",userData=ClientUser['chat_spaces'],chatContents = selectedChat)
                else:
                    return render_template("chat.html")
                
    #If there are no chat spaces in the user and or to be changed later.    
    else:
        if len(UsersData)>0 and existsClient1 == True:
            return render_template("chat.html",userData=ClientUser['chat_spaces'],chatContents = selectedChat)
        else:
            return render_template("chat.html")
