import socket, urllib.request, os, time
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

print("Welcome to the DogeRock Duino-Coin cmd line wallet\n")

def registerprompt():
  register = input("Would you like to register? (yes/no)\n>")
  return register

registerInput = registerprompt()

if (registerInput == "yes" or registerInput == "y"):
  username = input("What would you like your username to be?\n>")
  password = input("What would you like your password to be?\n>")
  email = input("What is your email address?\n>")
  while True:
    soc.send(bytes("REGI," + str(username) + "," + str(password) + "," + str(email), encoding="utf8"))
    regiFeedback = soc.recv(256).decode().split(",")

    if regiFeedback[0] == "OK":
      print("Successfully registered new account!")
      break
    elif regiFeedback[0] == "NO":
      print("Cannot make account! Reason: " + str(regiFeedback[1]) + "\nExiting in 10s")
      time.sleep(10)
      os._exit(1)

username = input("\nPlease enter your username:\n>")
password = input("\nPlease enter your password:\n>")

soc.send(bytes("LOGI," + username + "," + password, encoding="utf8"))
response = soc.recv(2).decode()           
if response != "OK":
  print("Invalid password! Exiting in 10s\n")
  time.sleep(10)
  os._exit(1)
else:
  print("\nSuccessfully logged in!")
  soc.send(bytes("FROM,DogeRockWallet,"+str(username), encoding="utf8")) 

print("\nWelcome " + username)

print("\nFor a list of commands type: help\n")

def command():
  command1 = input(">")
  if command1 == "help":
    print("Help command: help\nBalance command: balance\nSend command: send")
    command()
  elif command1 == "balance":
    soc.send(bytes("BALA", encoding="utf8"))
    balance = soc.recv(1024).decode()

    print("Duino balance: " + balance)
    command()
  elif command1 == "send":
    recipient = input("Enter recipients' username: ")
    amount = input("Enter amount to transfer: ")
    soc.send(bytes("SEND,deprecated,"+str(recipient)+","+str(amount), encoding="utf8"))
    while True:
      message = soc.recv(1024).decode()
      print("Server message: " + str(message))
      command()
      break
  else:
    print("Unknown command!")
    time.sleep(2)
    command()

command()
