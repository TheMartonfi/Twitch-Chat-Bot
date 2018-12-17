import time
import random
import urllib.request
from urllib.request import urlopen
from json import loads
from Read import getUser, getMessage
from Socket import openSocket, sendMessage
from Initialize import joinRoom
from Settings import CHANNEL
from Settings import COOLDOWN

#Basic command for twitch chat.
def basicCommand(input, output):
    if input == message.strip():
        sendMessage(s, output)
        cooldown()

#Adds a basic command to commands.txt
def addCommand(input):
    if input in message and user == CHANNEL:
        deleteCommand = open("commands.txt", "r")
        commandList = deleteCommand.readlines()
        deleteCommand.close()
        writeCommand = open("commands.txt", "a")
        commandMessage = getMessage(line)
        command = commandMessage.split(input, 1)[-1].strip()
        try:
            if command[0] == "!" and ";" in command and command not in str(commandList):
                writeCommand.write("\n" + command)
                sendMessage(s, "Command succesfully added.")
                writeCommand.close()
                cooldown()
            else:
                sendMessage(s, "Error: Missing \"!\" or \";\" or duplicate command.")
                cooldown()
        except IndexError as err:
            sendMessage(s, "Error: Invalid syntax for adding commands.")
            cooldown()
    elif input in message:
        sendMessage(s, "Error: Only the channel owner can use this command.")
        cooldown()

#Delete commands from chat.
def deleteCommand(input):
    if input in message and user == CHANNEL:
        deleteCommand = open("commands.txt", "r")
        commandList = deleteCommand.readlines()
        deleteCommand.close()
        commandMessage = getMessage(line)
        command = commandMessage.split(input, 1)[-1].strip()
        try:
            if command in str(commandList) and command[0] == "!":
                for commandLine in commandList:
                    if command in commandLine:
                        commandList.remove(commandLine)
                overwriteCommand = open("commands.txt", "w")
                overwriteCommand.write(str("".join(commandList).strip()))
                sendMessage(s, "Command succesfully deleted.")
                overwriteCommand.close()
                cooldown()
            else:
                sendMessage(s, "Error: Command {} not found.".format(command))
                cooldown()
        except IndexError as err:
            sendMessage(s, "Error: Command {} not found.".format(command))
            cooldown()
    elif input in message:
        sendMessage(s, "Error: Only the channel owner can use this command.")
        cooldown()

#Command that works only for specific user.
def userCommand(input, output, username):
    if input == message.strip() and user == username:
        sendMessage(s, output)
        cooldown()

#Command that works differently for specific users.
def userSpecificCommand(input, output, username, userOutput):
    if input == message.strip() and user == username:
        sendMessage(s, userOutput)
    elif input == message.strip():
        sendMessage(s, output)
        cooldown()

#The !addquote command for twitch chat.
def addQuoteCommand(input):
    if input in message and user in moderators:
        quoteMessage = getMessage(line)
        quote = quoteMessage.split(input, 1)[-1].strip()
        if quote != "":
            writeQuotes = open("quotes.txt", "a")
            writeQuotes.write("\n" + quote)
            sendMessage(s, "Quote succesfully added!")
            writeQuotes.close()
            cooldown()
        else:
            sendMessage(s, "Error: Quote cannot be empty.")
            cooldown()
    elif input in message:
        sendMessage(s, "Error: Only moderators can use this command.")
        cooldown()

#Posts a random quote from quotes document.
def quoteCommand(input):
    if input == message.strip():
        readQuotes = open("quotes.txt", "r")
        quoteList = readQuotes.readlines()
        quoteCount = -1
        for quote in quoteList:
            quoteCount += 1
        for x in range(1):
            try:
                randomNumber = random.randint(0, quoteCount)
                randomQuote = quoteList[randomNumber]
                sendMessage(s, randomQuote)
                readQuotes.close()
                cooldown()
            except ValueError as err:
                sendMessage(s, "Error: You currently have {} quotes.".format(quoteCount + 1))
                readQuotes.close()
                cooldown()

#Posts all command inputs.
def getCommands(input):
    if input == message.strip():
        sendMessage(s, "!addcom, " + "!delcom " + "!addquote, " + "!quote, " + "!quit " + ', '.join(listCommand))
        cooldown()

#Posts text from Now Playing.txt.
def songCommand(input):
    if input == message.strip():
        songFile = open("Now Playing.txt", "r")
        songName = songFile.readline()
        sendMessage(s, songName[3:].title())
        songFile.close()
        cooldown()

#This makes the bot commit seppuku.
def quitCommand(input):
    if input == message.strip() and user == CHANNEL:
        sendMessage(s, "The bot is being terminated.")
        quit()
    elif input == message.strip():
         sendMessage(s, "Error: You are not the channel owner.")
         cooldown()

#Prevents commands from being spammed.
def cooldown():
    if user == CHANNEL:
        pass
    elif user:
        abort_after = COOLDOWN
        start = time.time()
        while True:
            delta = time.time() - start
            if delta >= abort_after:
                break

#Checks to see if chat line is from twitch or chat.
def Console(line):
    if "PRIVMSG" in line:
        return False
    else:
        return True

s = openSocket()
joinRoom(s)
readbuffer = ""

#Loop that keeps the chat active and updates chatlines.
while True:
    readbuffer = s.recv(1024)
    readbuffer = readbuffer.decode()
    temp = readbuffer.split("\n")
    readbuffer = readbuffer.encode()
    readbuffer = temp.pop()

    for line in temp:
        print(line)
#Prevents afk kick from server.
        if "PING" in line and Console(line):
            msgg = "PONG tmi.twitch.tv\r\n".encode()
            s.send(msgg)
            print(msgg)
            break
#Prints chat lines in a more readable fashion.
        user = getUser(line)
        message = getMessage(line)
        print(user + " typed: " + message)

#List of Moderators and Chatters
        response = urlopen('https://tmi.twitch.tv/group/user/{}/chatters'.format(CHANNEL))
        readable = response.read().decode('utf-8')
        chatlist = loads(readable)
        chatters = chatlist['chatters']
        moderators = chatters['moderators']
        
#Makes dict of commands from command.txt
        commands = {}
        listCommand = []
        commandFile = open("commands.txt", "r")
        commandList = commandFile.readlines()
        commandFile.close()
        for command in commandList:
            try:
                commandInput, commandOutput = command.split(";")
                commands[commandInput] = commandOutput
            except ValueError as err:
                sendMessage(s, "Error: Invalid command in commands.txt")
                cooldown()

#Loops dict through basicCommand function and creates a list of commands.
        for input, output in commands.items():
            basicCommand(input, output)
            listCommand.append(input)

#Add command functions below.
        getCommands("!commands")
        addCommand("!addcom")
        deleteCommand("!delcom")
        addQuoteCommand("!addquote")
        quoteCommand("!quote")
        quitCommand("!quit")
        continue
