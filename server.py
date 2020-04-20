import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json
import requests
import random
import sys
from random import seed
from random import random
from random import randint

clients_lock = threading.Lock()
connected = 0

clients = {}

### Login Player ###
def loginPlayer(sock, loginInfo, fromAddress):
   URL = "https://ftg588de11.execute-api.us-east-1.amazonaws.com/default/HitBeasts_LoginPlayer"
   headers = {'Content-Type': "application/json", 'Accept': "application/json"}
   location = "toronto"
   PARAMS = {'address':location}

   data = {}
   data['user_id'] = loginInfo[0]
   data['password'] = loginInfo[1]

   r = requests.put(url = URL, json = data, headers = headers)
   returnData = r.json()
   
   
   pktID = 0
   GameState = {"cmd": 1, "pktID": pktID, "players": []}
   clients_lock.acquire()
   for c in clients:
      if (c != fromAddress):
         continue
      
      else:
         player = {}
         
         if (returnData == "Error: Password doesn't match or User doesn't exist!"):
            print(returnData)
            clients[c]['playerData'] = returnData
         else:
            #Send the player data from the database to the client
            clients[c]['playerData'] = {"user_id": returnData['user_id'], "game_id": returnData['game_id'], "loggedIn": returnData['loggedIn'], "attackLvl": returnData['attackLvl'], "defenceLvl": returnData['defenceLvl'], "healthLvl": returnData['healthLvl'], "specialLvl": returnData['specialLvl'], "luckLvl": returnData['luckLvl'], "skillPoints": returnData['skillPoints'], "address": str(fromAddress)}
         
         player['id'] = str(c)
         player['playerData'] = clients[c]['playerData']
         GameState['players'].append(player)
         
   s=json.dumps(GameState,separators=(",", ":"))
   for c in clients:
      if (c == fromAddress):
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
         break
      
   clients_lock.release()
    
      
### Logout Player ###
def logoutPlayer(sock, loginInfo, fromAddress):
   URL = "https://61wg5gfqnh.execute-api.us-east-1.amazonaws.com/default/HitBeasts_LogoutPlayer"
   headers = {'Content-Type': "application/json", 'Accept': "application/json"}
   location = "toronto"
   PARAMS = {'address':location}

   data = {}
   data['user_id'] = loginInfo[0]

   r = requests.put(url = URL, json = data, headers = headers)
   returnData = r.json()

 
### Get List of Players who are Logged In and not in a Game ###
def getReadyPlayers(sock, tempData, fromAddress):
   URL = "https://7sry1cuefi.execute-api.us-east-1.amazonaws.com/default/GetReadyPlayers"

   data = {}
   
   r = requests.get(url = URL)
   returnData = r.json()

   pktID = 0
   GameState = {"cmd": 4, "pktID": pktID, "players": []}
   
   clients_lock.acquire()
   for c in clients:
      if (str(c) == str(fromAddress)):
         continue
      
      for result in returnData:
         player = {}
         if (returnData is None):
            print("No Players available!")
            clients[c]['playerData'] = "No Players available!"
            
         else:
            #Send the player data from the database to the client
            clients[c]['playerData'] = result
            clients[c]['playerData']['address'] = str(c)
         
         player['id'] = str(c)
         player['playerData'] = clients[c]['playerData']
         
         GameState['players'].append(player)
         
   s=json.dumps(GameState,separators=(",", ":"))
   for c in clients:
      if (str(c) == str(fromAddress)):
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
         break
      
   clients_lock.release()


### Join Players ###
def joinPlayers(sock, toAddress, fromAddress):
   
   pktID = 0
   GameState = {"cmd": 5, "pktID": pktID, "players": []}
   clients_lock.acquire()
   for c in clients:
      player = {}
      #Send the player data from the database to the client
      clients[c]['playerData'] = {}
      clients[c]['playerData']['address'] = str(fromAddress)
      
      player['id'] = str(c)
      player['playerData'] = clients[c]['playerData']
      GameState['players'].append(player)
         
   s=json.dumps(GameState,separators=(",", ":"))
   for c in clients:
      if ((str(c) == str(toAddress)) or (str(c) == str(fromAddress))):
         print("from address: " + str(fromAddress))
         print("sent to " + str(toAddress))
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
   clients_lock.release()
  
  
### Start Betting ###
def startBetting(sock, toAddress, bet, fromAddress):

   pktID = 0
   GameState = {"cmd": 6, "pktID": pktID, "players": []}
   clients_lock.acquire()
   for c in clients:
      player = {}
      #Send the player data from the database to the client
      clients[c]['playerData'] = {}
      clients[c]['playerData']['address'] = str(fromAddress)
      clients[c]['playerData']['betPoints'] = bet
      
      player['id'] = str(c)
      player['playerData'] = clients[c]['playerData']
      GameState['players'].append(player)
         
   s=json.dumps(GameState,separators=(",", ":"))
   
   for c in clients:
      if (str(c) == str(toAddress)):
         print("from address: " + str(fromAddress))
         print("sent to " + str(toAddress))
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
         break
      
   clients_lock.release()
  
  
### Start Battle ###
def startBattle(sock, toAddress, gameData, fromAddress):
   URL = "https://abs2mx8h0g.execute-api.us-east-1.amazonaws.com/default/HitBeasts_SetGame_Ids"
   headers = {'Content-Type': "application/json", 'Accept': "application/json"}
   location = "toronto"
   PARAMS = {'address':location}

   splitData = gameData.split("/")
   
   for x in range(2):
      data = {}
      data['user_id'] = splitData[x]
      data['game_id'] = gameData
   
      r = requests.put(url = URL, json = data, headers = headers)
      returnData = r.json()
      print(returnData)
      
   pktID = 0
   GameState = {"cmd": 7, "pktID": pktID, "players": []}
   clients_lock.acquire()

   s=json.dumps(GameState,separators=(",", ":"))
   
   for c in clients:
      if (str(c) == str(toAddress)):
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
         break
      
   clients_lock.release()
   
   
### End Battle ###
def endBattle(sock, toAddress, gameData, fromAddress):
   URL = "https://kvnbmo377d.execute-api.us-east-1.amazonaws.com/default/HitBeasts_UpdatePlayerValues"
   headers = {'Content-Type': "application/json", 'Accept': "application/json"}
   location = "toronto"
   PARAMS = {'address':location}

   print(gameData)
   splitData = gameData.split("/")
   
   print("Starting Updating")
   
   data = {}
   data['user_id'] = splitData[0]
   data['game_id'] = 'none'
   data['attackLvl'] = splitData[1]
   data['defenceLvl'] = splitData[2]
   data['healthLvl'] = splitData[3]
   data['luckLvl'] = splitData[4]
   data['skillPoints'] = splitData[5]
   data['specialLvl'] = splitData[6]
   
   r = requests.put(url = URL, json = data, headers = headers)
   returnData = r.json()
   print(returnData)
   
   data = {}
   data['user_id'] = splitData[7]
   data['game_id'] = 'none'
   data['attackLvl'] = splitData[8]
   data['defenceLvl'] = splitData[9]
   data['healthLvl'] = splitData[10]
   data['luckLvl'] = splitData[11]
   data['skillPoints'] = splitData[12]
   data['specialLvl'] = splitData[13]
   
   r = requests.put(url = URL, json = data, headers = headers)
   returnData = r.json()
   print(returnData)
   
   print("Finished Updating")  
   pktID = 0
   GameState = {"cmd": 8, "pktID": pktID, "players": []}
   clients_lock.acquire()

   s=json.dumps(GameState,separators=(",", ":"))
   
   for c in clients:
      if ((str(c) == str(toAddress)) or (str(c) == str(fromAddress))):
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      
   clients_lock.release()
   
   
### Attack ###
def attack(sock, toAddress, attackData, fromAddress):

   splitData = attackData.split("/")
   player1AttackLow = int(splitData[0])
   player1AttackHigh = int(splitData[1])
   player1LuckVal  = int(splitData[2])
   
   player2DefenceLow = int(splitData[3])
   player2DefenceHigh = int(splitData[4])
   player2LuckVal  = int(splitData[5])
   player2Health  = int(splitData[6])
   
   
   seed(datetime.now().microsecond)
   
   attackVal = randint(player1AttackLow, player1AttackHigh)
   defenceVal = randint(player2DefenceLow, player2DefenceHigh)
   
   if (attackVal > defenceVal):
      healthVal = player2Health - (attackVal - defenceVal)
   
   else:
      healthVal = player2Health
   
   pktID = 0
   GameState = {"cmd": 9, "pktID": pktID, "players": []}
   clients_lock.acquire()
   for c in clients:
      player = {}
      #Send the player data from the database to the client
      clients[c]['playerData'] = {}
      clients[c]['playerData']['address'] = str(fromAddress)
      clients[c]['playerData']['currentHealth'] = healthVal
      
      player['id'] = str(c)
      player['playerData'] = clients[c]['playerData']
      GameState['players'].append(player)
         
   s=json.dumps(GameState,separators=(",", ":"))
   
   for c in clients:
      if ((str(c) == str(toAddress)) or (str(c) == str(fromAddress))):
         print("from address: " + str(fromAddress))
         print("sent to " + str(toAddress))
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
         
   clients_lock.release()


### Heal ###
def heal(sock, toAddress, attackData, fromAddress):

   splitData = attackData.split("/")
   player1HealLow = int(splitData[0])
   player1HealHigh = int(splitData[1])
   player1LuckVal  = int(splitData[2])
   player1Health  = int(splitData[3])
   player1MaxHealth = int(splitData[4])
   
   seed(datetime.now().microsecond)
   
   healVal = randint(player1HealLow, player1HealHigh)
   
   healthVal = player1Health + healVal
   
   if (healthVal > player1MaxHealth):
      healthVal = player1MaxHealth
   
   pktID = 0
   GameState = {"cmd": 10, "pktID": pktID, "players": []}
   clients_lock.acquire()
   for c in clients:
      player = {}
      #Send the player data from the database to the client
      clients[c]['playerData'] = {}
      clients[c]['playerData']['address'] = str(fromAddress)
      clients[c]['playerData']['currentHealth'] = healthVal
      
      player['id'] = str(c)
      player['playerData'] = clients[c]['playerData']
      GameState['players'].append(player)
         
   s=json.dumps(GameState,separators=(",", ":"))
   
   for c in clients:
      if ((str(c) == str(toAddress)) or (str(c) == str(fromAddress))):
         print("from address: " + str(fromAddress))
         print("sent to " + str(toAddress))
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
         
   clients_lock.release()
   
   
def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
         
         else:
            temp = data.split("'")[1].split(",")
            tempJoin = data.split(",")

            ### If Player is Logging In ###
            if (temp[0] == "login"):
               print("Logging In")
               temp.pop(0)
               loginPlayer(sock, temp, addr)
            
            
            ### If Player is Logging In ###
            elif (temp[0] == "logout"):
               print("Logging Out")
               temp.pop(0)
               logoutPlayer(sock, temp, addr)
               
               
            ### If player is asking for ready players ###
            elif (temp[0] == "list"):
               print("Getting Logged In Player List")
               temp.pop(0)
               getReadyPlayers(sock, temp, addr)
            
            
            ### If player is connecting with another player ###
            elif (tempJoin[0] == "b\"join"):
               print("Joining two players!")
               newTemp = tempJoin[2].split("\"")
               joinPlayers(sock, tempJoin[1] + "," + newTemp[0], addr)
               
               
            ### If player is connecting with another player ###
            elif (tempJoin[0] == "b\"bet"):
               print("Sent Bet!")
               newTemp = tempJoin[2].split("\"")
               betTemp = tempJoin[3].split("\"")
               startBetting(sock, tempJoin[1] + "," + newTemp[0], betTemp[0], addr)
               
            ### Start the Battle ###
            elif (tempJoin[0] == "b\"startbattle"):
               print("Started Battle!")
               newTemp = tempJoin[2].split("\"")
               gameTemp = tempJoin[3].split("\"")
               startBattle(sock, tempJoin[1] + "," + newTemp[0], gameTemp[0], addr)
             
            ### End the Battle ###
            elif (tempJoin[0] == "b\"endbattle"):
               print("Ended Battle!")
               newTemp = tempJoin[2].split("\"")
               gameTemp = tempJoin[3].split("\"")
               endBattle(sock, tempJoin[1] + "," + newTemp[0], gameTemp[0], addr)
              
            ### Attack ###
            elif (tempJoin[0] == "b\"attack"):
               print("attack!")
               newTemp = tempJoin[2].split("\"")
               attackTemp = tempJoin[3].split("\"")
               attack(sock, tempJoin[1] + "," + newTemp[0], attackTemp[0], addr)
               
            ### Special ###
            elif (tempJoin[0] == "b\"special"):
               print("special!")
               newTemp = tempJoin[2].split("\"")
               specialTemp = tempJoin[3].split("\"")
               attack(sock, tempJoin[1] + "," + newTemp[0], specialTemp[0], addr)  
               
            ### Heal ###
            elif (tempJoin[0] == "b\"heal"):
               print("heal!")
               newTemp = tempJoin[2].split("\"")
               healTemp = tempJoin[3].split("\"")
               heal(sock, tempJoin[1] + "," + newTemp[0], healTemp[0], addr)  
               
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['playerData'] = 0
            message = {"cmd": 0,"players":[]}

            p = {}
            p['id'] = str(addr)
            p['playerData'] = 0
            
            message['players'].append(p)

            GameState = {"cmd": 4, "players":[]}
            for c in clients:
               print("Connected client: " + str(c))
               if (c == addr):
                  message['cmd'] = 3
               else:
                  message['cmd'] = 0

               m = json.dumps(message,separators=(",", ":"))
               player = {}
               player['id'] = str(c)
               player['playerData']= clients[c]['playerData']
               GameState['players'].append(player)
               sock.sendto(bytes(m,'utf8'), (c[0],c[1]))

            m = json.dumps(GameState)
            sock.sendto(bytes(m,'utf8'), addr)

def cleanClients(sock):
   while True:
      droppedClients = []
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
            droppedClients.append(str(c))
      
      message = {"cmd": 2, "droppedPlayers":droppedClients}
      m = json.dumps(message,separators=(",", ":"))
      if (len(droppedClients) > 0):
         for c in clients:
            sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
      
      time.sleep(1)

def gameLoop(sock):
   pktID = 0
   while True:
      GameState = {"cmd": 1, "pktID": pktID, "players": []}
      clients_lock.acquire()
      for c in clients:
         player = {}
         clients[c]['playerData'] = "test123"
         player['id'] = str(c)
         player['playerData'] = clients[c]['playerData']
         GameState['players'].append(player)
      s=json.dumps(GameState,separators=(",", ":"))
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      if (len(clients)>0):
         pktID = pktID +1
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   #start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
