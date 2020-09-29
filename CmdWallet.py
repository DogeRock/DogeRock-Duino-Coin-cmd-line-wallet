"""
MIT License

Copyright (c) [2020] [DogeRock]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import socket, urllib.request, os, time, requests, json
from signal import signal, SIGINT

serverip = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" 
with urllib.request.urlopen(serverip) as content:
  content = content.read().decode().splitlines() 
  pool_address = content[0] 
  pool_port = content[1] 

soc = socket.socket()
soc.connect((str(pool_address), int(pool_port)))
soc.recv(3).decode()

def handler(signal_received, frame):
	print("\nExiting...")
	try:
		soc.send(bytes("CLOSE", encoding="utf8"))
	except:
		pass
	os._exit(0)

signal(SIGINT, handler)

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

print(color.YELLOW + "Welcome to the DogeRock Duino-Coin cmd line wallet\n" + color.END)

def registerprompt():
  register = input(color.BLUE + "Would you like to register? (yes/no)\n>" + color.END)
  return register

registerInput = registerprompt()

if (registerInput == "yes" or registerInput == "y"):
  username = input(color.BLUE + "What would you like your username to be?\n>" + color.END)
  password = input(color.BLUE + "What would you like your password to be?\n>" + color.END)
  email = input(color.BLUE + "What is your email address?\n>" + color.END)
  while True:
    soc.send(bytes("REGI," + str(username) + "," + str(password) + "," + str(email), encoding="utf8"))
    regiFeedback = soc.recv(256).decode().split(",")

    if regiFeedback[0] == "OK":
      print(color.CYAN + "Successfully registered new account!" + color.END)
      break
    elif regiFeedback[0] == "NO":
      print(color.RED + "Cannot make account! Reason: " + str(regiFeedback[1]) + "\nExiting in 10s" + color.END)
      time.sleep(10)
      os._exit(1)

def login():
  username = input(color.GREEN + "\nPlease enter your username:\n>" + color.END)
  password = input(color.GREEN + "\nPlease enter your password:\n>" + color.END)

  soc.send(bytes("LOGI," + username + "," + password, encoding="utf8"))
  response = soc.recv(2).decode()           
  if response != "OK":
    print(color.RED + "Invalid password! Exiting in 10s\n" + color.END)
    time.sleep(10)
    os._exit(1)
  else:
    print(color.CYAN + "\nSuccessfully logged in!" + color.END)
    soc.send(bytes("FROM,DogeRockWallet,"+str(username), encoding="utf8"))
  print(color.CYAN + "\nWelcome " + username + color.END)
  print(color.CYAN + "\nFor a list of commands type: help\n" + color.END)

login()

def command():
  global color
  command1 = input(color.DARKCYAN + ">" + color.END)
  if command1 == "help":
    print(color.DARKCYAN + "Help command: help\nBalance command: balance\nSend command: send\nChange password: changepassword\nDuino price: price\nExit: exit" + color.END)
    command()
  elif command1 == "balance":
    soc.send(bytes("BALA", encoding="utf8"))
    balance = soc.recv(1024).decode()

    print(color.BLUE + "Duino balance: " + balance + color.END)

    command()
  elif command1 == "send":
    recipient = input(color.YELLOW + "Enter recipients' username: " + color.END)
    amount = input(color.YELLOW + "Enter amount to transfer: " + color.END)
    confirm = input(color.YELLOW + "Type" + color.BOLD + " confirm " + color.END + color.YELLOW + "to confirm\n>" + color.END)
    if confirm == "confirm":
      soc.send(bytes("SEND,deprecated,"+str(recipient)+","+str(amount), encoding="utf8"))
      while True:
        message = soc.recv(1024).decode()
        print(color.YELLOW + str(message) + color.END)
        command()
        break
    else:
      print(color.RED + "Command cancled" + color.END)
      command()
  elif command1 == "exit":
    soc.close()
    os._exit(1)
  elif command1 == "changepassword":
    oldpassword = input(color.GREEN + "Enter your current password\n>" + color.END)
    newpassword = input(color.GREEN + "Enter new password\n>" + color.END)
    soc.send(bytes("CHGP,"+  str(oldpassword) + "," + str(newpassword), encoding="utf8"))
    while True:
      message = soc.recv(1024).decode()
      print(color.GREEN + str(message) + color.END)
      command()
      break
  elif command1 == "price":
    api = "https://raw.githubusercontent.com/revoxhere/duco-statistics/master/api.json"
    apiFeedback = requests.get(api, data = None)
    rate = 1
    if apiFeedback.status_code == 200:
      content = apiFeedback.content.decode()
      contentjson = json.loads(content)
      ducofiat = float(contentjson["Duco price"]) * float(rate)
      print(color.YELLOW + "Duino price: " + color.END)
      print(ducofiat)
      command()
    else:
      print(color.RED + "Error: Cannot send request to api, Please try again later" + color.END)
      command()
  else:
    print(color.RED + "Unknown command!" + color.END)
    command()

command()
