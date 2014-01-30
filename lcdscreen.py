#!/usr/bin/python 
 
######################################################################## 
# 
# LCD4: Learning how to control an LCD module from Pi 
# 
# Author: Bruce E. Hall <bhall66@gmail.com> 
# Date : 12 Mar 2013 
# 
# See w8bh.net for more information. 
# 
######################################################################## 
 
import time #for timing delays 
import RPi.GPIO as GPIO 
import random 
import jsonrpclib
import pywapi
import urllib2

xbmc = 0

#OUTPUTS: map GPIO to LCD lines 
LCD_RS = 7 #GPIO7 = Pi pin 26 
LCD_E = 8 #GPIO8 = Pi pin 24 
LCD_D4 = 17 #GPIO17 = Pi pin 11 
LCD_D5 = 18 #GPIO18 = Pi pin 12 
LCD_D6 = 27 #GPIO21 = Pi pin 13 
LCD_D7 = 22 #GPIO22 = Pi pin 15 
OUTPUTS = [LCD_RS,LCD_E,LCD_D4,LCD_D5,LCD_D6,LCD_D7] 

#INPUTS: map GPIO to Switches 
SW1 = 4 #GPIO4 = Pi pin 7 
SW2 = 23 #GPIO16 = Pi pin 16 
SW3 = 10 #GPIO10 = Pi pin 19 
SW4 = 9 #GPIO9 = Pi pin 21 
INPUTS = [SW1,SW2,SW3,SW4]

#HD44780 Controller Commands 
CLEARDISPLAY = 0x01 
RETURNHOME = 0x02 
RIGHTTOLEFT = 0x04 
LEFTTORIGHT = 0x06 
DISPLAYOFF = 0x08 
CURSOROFF = 0x0C 
CURSORON = 0x0E 
CURSORBLINK = 0x0F 
CURSORLEFT = 0x10 
CURSORRIGHT = 0x14 
LOADSYMBOL = 0x40 
SETCURSOR = 0x80 
 
#Line Addresses. 
LINE = [0x00,0x40,0x14,0x54] #for 20x4 display 
 
battery = [ 
[ 0x0E, 0x1B, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1F ], #0% (no charge) 
[ 0x0E, 0x1B, 0x11, 0x11, 0x11, 0x11, 0x1F, 0x1F ], #17% 
[ 0x0E, 0x1B, 0x11, 0x11, 0x11, 0x1F, 0x1F, 0x1F ], #34% 
[ 0x0E, 0x1B, 0x11, 0x11, 0x1F, 0x1F, 0x1F, 0x1F ], #50% (half-full) 
[ 0x0E, 0x1B, 0x11, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #67% 
[ 0x0E, 0x1B, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #84% 
[ 0x0E, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #100% (full charge) 
] 

musicNote = [
[ 0x7,  0x7,  0x4, 0x4, 0x4, 0x1C, 0x1C, 0x1C ],
[ 0x1e, 0x1e, 0x2, 0x2, 0xE, 0xE,  0xE,  0x0  ]
]

movie = [
[ 0x1F, 0x15, 0x1F, 0x8,  0x8,  0x1F, 0x15, 0x1F ],
[ 0x1F, 0xA,  0x1F, 0x11, 0x11, 0x1F, 0xA,  0x1F ],
[ 0x1F, 0x15, 0x1F, 0x2,  0x2,  0x1F, 0x15, 0x1F ]
]

iPlayer = [
[ 0x18, 0x4, 0x12, 0x11, 0x11, 0x12, 0x14, 0x18 ]
]

pause = [
[ 0xE, 0xE, 0xE, 0xE, 0xE, 0xE, 0xE, 0xE ],
[ 0xE, 0xE, 0xE, 0xE, 0xE, 0xE, 0xE, 0xE ]
]

weather = [
[ 0xC, 0x12, 0x12, 0xC, 0x0, 0x0, 0x0, 0x0 ], #degree
[ 0x0, 0x0,  0x0,  0xE, 0x0, 0x0, 0x0, 0x0 ]  #hyphen
]

party = [ #A 4x2 grid of pixels
[ 0x0, 0x0,  0x0,  0x0, 0x0,  0x0,  0x1,  0x2 ], #1x1
[ 0x0, 0x3,  0x4,  0xA, 0x12, 0x11, 0x1,  0x0 ], #2x1
[ 0x2, 0x14, 0x8,  0x5, 0x2,  0x2,  0x11, 0x9 ], #3x1
[ 0x0, 0x8,  0x10, 0x0, 0x4,  0x8,  0x10, 0x0 ], #4x1
[ 0x4, 0x4,  0x8,  0x8, 0x9,  0x1e, 0x18, 0x0 ], #1x2
[ 0x0, 0x0,  0x3,  0xC, 0x10, 0x0,  0x0,  0x0 ], #2x2
[ 0x6, 0x18, 0x0,  0x0, 0x0,  0x0,  0x0,  0x0 ], #3x2
]

patterns = [ 
[ 0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A ], #50% 
[ 0x0A, 0x15, 0x0A, 0x15, 0x0A, 0x15, 0x0A, 0x15 ], #alt 50% 
[ 0x15, 0x15, 0x15, 0x15, 0x15, 0x15, 0x15, 0x15 ], #3 vbars 
[ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ], 
[ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ], 
[ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ], 
[ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ], 
] 
 
verticalBars = [ 
[ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F ], #1 bar 
[ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F ], #2 bars 
[ 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F ], #3 bars 
[ 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F, 0x1F ], #4 bars 
[ 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #5 bars 
[ 0x00, 0x00, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #6 bars 
[ 0x00, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #7 bars 
[ 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #8 bars 
] 
 
horizontalBars = [ 
[ 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10 ], #1 bar 
[ 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18 ], #2 bars 
[ 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C, 0x1C ], #3 bars 
[ 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E, 0x1E ], #4 bars 
[ 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ], #5 bars 
[ 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F ], #4 bars 
[ 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07 ], #3 bars 
[ 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03 ], #2 bars 
] 
 
digits = [ 
[ 0x01, 0x03, 0x03, 0x07, 0x07, 0x0F, 0x0F, 0x1F ], #lower-rt triangle 
[ 0x10, 0x18, 0x18, 0x1C, 0x1C, 0x1E, 0x1E, 0x1F ], #lower-lf triangle 
[ 0x1F, 0x0F, 0x0F, 0x07, 0x07, 0x03, 0x03, 0x01 ], #upper-rt triangle 
[ 0x1F, 0x1E, 0x1E, 0x1C, 0x1C, 0x18, 0x18, 0x10 ], #upper-lf triangle 
[ 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x1F, 0x1F ], #lower horiz bar 
[ 0x1F, 0x1F, 0x1F, 0x1F, 0x00, 0x00, 0x00, 0x00 ], #upper horiz bar 
[ 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F ] #solid block 
] 
 
bigDigit = [ 
[ 0x00, 0x06, 0x01, 0x06, 0x20, 0x06, 0x06, 0x20, 0x06, 0x02, 0x06, 0x03], #0 
[ 0x20, 0x06, 0x20, 0x20, 0x06, 0x20, 0x20, 0x06, 0x20, 0x20, 0x06, 0x20], #1 
[ 0x00, 0x06, 0x01, 0x20, 0x00, 0x03, 0x00, 0x03, 0x20, 0x06, 0x06, 0x06], #2 
[ 0x00, 0x06, 0x01, 0x20, 0x20, 0x06, 0x20, 0x05, 0x06, 0x02, 0x06, 0x03], #3 
[ 0x06, 0x20, 0x06, 0x06, 0x06, 0x06, 0x20, 0x20, 0x06, 0x20, 0x20, 0x06], #4 
[ 0x06, 0x06, 0x06, 0x06, 0x04, 0x04, 0x20, 0x20, 0x06, 0x06, 0x06, 0x03], #5 
[ 0x00, 0x06, 0x01, 0x06, 0x20, 0x20, 0x06, 0x05, 0x01, 0x02, 0x06, 0x03], #6 
[ 0x06, 0x06, 0x06, 0x20, 0x20, 0x06, 0x20, 0x20, 0x06, 0x20, 0x20, 0x06], #7 
[ 0x00, 0x06, 0x01, 0x06, 0x04, 0x06, 0x06, 0x05, 0x06, 0x02, 0x06, 0x03], #8
[ 0x00, 0x06, 0x01, 0x02, 0x04, 0x06, 0x20, 0x20, 0x06, 0x20, 0x20, 0x06] #9 
] 
 
######################################################################## 
# 
# Low-level routines for configuring the LCD module. 
# These routines contain GPIO read/write calls. 
# 
 
def InitIO(): 
  #Sets GPIO pins to input & output, as required by LCD board 
  GPIO.setmode(GPIO.BCM) 
  GPIO.setwarnings(False) 
  for lcdLine in OUTPUTS: 
    GPIO.setup(lcdLine, GPIO.OUT) 
  for switch in INPUTS: 
    GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
 
def CheckSwitches(): 
  #Check status of all four switches on the LCD board
  #Returns four boolean values as a tuple.
  val1 = not GPIO.input(SW1) 
  val2 = not GPIO.input(SW2) 
  val3 = not GPIO.input(SW3) 
  val4 = not GPIO.input(SW4) 
  return (val4,val1,val2,val3) 
 
def PulseEnableLine(): 
  #Pulse the LCD Enable line; used for clocking in data 
  GPIO.output(LCD_E, GPIO.HIGH) #pulse E high 
  GPIO.output(LCD_E, GPIO.LOW) #return E low 
 
def SendNibble(data): 
  #sends upper 4 bits of data byte to LCD data pins D4-D7 
  GPIO.output(LCD_D4, bool(data & 0x10)) 
  GPIO.output(LCD_D5, bool(data & 0x20)) 
  GPIO.output(LCD_D6, bool(data & 0x40)) 
  GPIO.output(LCD_D7, bool(data & 0x80)) 
 
def SendByte(data,charMode=False): 
  #send one byte to LCD controller 
  GPIO.output(LCD_RS,charMode) #set mode: command vs. char 
  SendNibble(data) #send upper bits first 
  PulseEnableLine() #pulse the enable line 
  data = (data & 0x0F)<< 4 #shift 4 bits to left 
  SendNibble(data) #send lower bits now 
  PulseEnableLine() #pulse the enable line 
 
 
######################################################################## 
# 
# Higher-level routines for diplaying data on the LCD. 
# 
 
def ClearDisplay(): 
  #This command requires 1.5mS processing time, so delay is needed 
  SendByte(CLEARDISPLAY) 
  time.sleep(0.0015) #delay for 1.5mS 
 
def CursorOn(): 
  SendByte(CURSORON) 
 
def CursorOff(): 
  SendByte(CURSOROFF) 
 
def CursorBlink(): 
  SendByte(CURSORBLINK) 
 
def CursorLeft(): 
  SendByte(CURSORLEFT) 
 
def CursorRight(): 
  SendByte(CURSORRIGHT) 
 
def InitLCD(): 
  #initialize the LCD controller & clear display 
  SendByte(0x33) #initialize 
  SendByte(0x32) #initialize/4-bit 
  SendByte(0x28) #4-bit, 2 lines, 5x8 font 
  SendByte(LEFTTORIGHT) #rightward moving cursor 
  CursorOff() 
  ClearDisplay() 

def SendChar(ch): 
  SendByte(ord(ch),True) 

def ShowMessage(string):
  #Send string of characters to display at current cursor position 
  for character in string: 
    SendChar(character)

def ShowMessageWrap(string, LineNumber): 
  #Send string of characters to display at current cursor position 
  WordWrap = False
  while WordWrap == False:
    if LineNumber == 4:
      return
    if len(string) > 20:
      message = string[:20]
      string = string[20:]
      GotoLine(LineNumber)
      LineNumber += 1
      for character in message: 
        SendChar(character) 
    else:
      message = string
      GotoLine(LineNumber)
      LineNumber += 1
      for character in message:
        SendChar(character)
      WordWrap = True
 
def GotoLine(row): 
  #Moves cursor to the given row 
  #Expects row values 0-1 for 16x2 display; 0-3 for 20x4 display 
  addr = LINE[row] 
  SendByte(SETCURSOR+addr) 
 
def GotoXY(row,col): 
  #Moves cursor to the given row & column 
  #Expects col values 0-19 and row values 0-3 for a 20x4 display 
  addr = LINE[row] + col 
  SendByte(SETCURSOR + addr) 
 
 
######################################################################## 
# 
# BIG CLOCK & Custom character generation routines 
# 
 
def LoadCustomSymbol(addr,data): 
  #saves custom character data at given char-gen address 
  #data is a list of 8 bytes that specify the 5x8 character 
  #each byte contains 5 column bits (b5,b4,..b0) 
  #each byte corresponds to a horizontal row of the character 
  #possible address values are 0-7 
  cmd = LOADSYMBOL + (addr<<3) 
  SendByte(cmd) 
  for byte in data: 
    SendByte(byte,True) 
 
def LoadSymbolBlock(data): 
  #loads a list of symbols into the chargen RAM, starting at addr 0x00 
  for i in range(len(data)): 
    LoadCustomSymbol(i,data[i]) 
 
def ShowBigDigit(symbol,startCol): 
  #displays a 4-row-high digit at specified column 
  for row in range(4): 
    GotoXY(row,startCol) 
    for col in range(3): 
      index = row*3 + col 
      SendByte(symbol[index],True) 
 
def ShowColon(col): 
  #displays a 2-char high colon ':' at specified column 
  dot = chr(0xA1) 
  GotoXY(1,col) 
  SendChar(dot) 
  GotoXY(2,col) 
  SendChar(dot) 
 
def BigClock(): 
  #displays large-digit time in hh:mm:ss on 20x4 LCD 
  #continuous display (this routine does not end!) 
  LoadSymbolBlock(digits)
  posn = [0,3,7,10]
  ClearDisplay() 
  while (True): 
    switchValues = CheckSwitches()
    if switchValues[0] == 1:
      DisplayPiInfo()
    elif switchValues[1] == 1:
      ClearDisplay()
      GotoLine(1)
      ShowMessage("     Power Off?")
      GotoLine(3)
      ShowMessage("No               Yes")
      while(True):
        switchValues = CheckSwitches()
        if switchValues[3] == 1:
          ClearDisplay()
          GotoLine(1)
          ShowMessage("      Goodbye")
          xbmc.System.Shutdown()
        elif switchValues[0] == 1:
          ClearDisplay()
          break
        time.sleep(0.08)
    elif switchValues[2] == 1:
      LetsParty()
      NowPlaying()
      time.sleep(1)
      LoadSymbolBlock(digits)
      ClearDisplay()
      LoadSymbolBlock(digits)
      posn = [0,3,7,10,14,17]
    elif switchValues[3] == 1:
      DisplayWeather()
      LoadSymbolBlock(digits)
    try:
      result = xbmc.Player.GetActivePlayers()
      if result:
        NowPlaying()
        time.sleep(1)
        LoadSymbolBlock(digits)
    except:
      time.sleep(0)
    tStr = time.strftime("%I%M")
    for i in range(len(tStr)): 
      ShowColon(6) 
      value = int(tStr[i]) 
      symbols = bigDigit[value] 
      ShowBigDigit(symbols,posn[i]) 
    GotoXY(0,13)
    ShowMessage(time.strftime("%p"))
    GotoXY(1,17)
    ShowMessage(time.strftime("%a"))
    GotoXY(2,14)
    ShowMessage(time.strftime("%b %d"))
    GotoXY(3,16)
    ShowMessage(time.strftime("%Y"))
    time.sleep(1) 
    GotoXY(1,6)
    ShowMessage(" ")
    GotoXY(2,6)
    ShowMessage(" ")
    time.sleep(1)
 
######################################################################## 
# 
# Basic HD44780 Test Routines 
# Code here is used in higher-level testing routines 
# 
 
ANIMATIONDELAY = 0.02 
 
def LabelTest(label): 
  #Label the current Test 
  ClearDisplay() 
  GotoXY(1,20-len(label)); ShowMessage(label) 
  GotoXY(2,16); ShowMessage('test') 
 
def CommandTest(): 
  LabelTest('Command') 
  while (True): 
    st = raw_input("Enter a string or command: ") 
    if len(st)==2: 
      SendByte(int(st,16)) 
    elif len(st)==1: 
      SendByte(int(st),True) 
    else: 
      ShowMessage(st) 
 
def AnimateCharTest(numCycles=8,delay=0.25): 
  LabelTest('Animation') 
  LoadSymbolBlock(battery) #get all battery symbols 
  GotoXY(1,6) #where to put battery 
  for count in range(numCycles): 
    for count in range(len(battery)): #sequence thru all symbols 
      SendByte(count,True) #display the symbol 
      CursorLeft() #keep cursor on same char 
      time.sleep(delay) #control animation speed 
    time.sleep(1) #wait between cycles 
 
def ShowBars(row,col,numBars): 
  #displays a graph symbol at row,col position 
  #numBars = number of horizontal (or vertical bars) in this symbol 
  #expected values = 0 to 7 (vertical) or 0 to 4 (horizontal) 
  GotoXY(row,col) 
  if numBars==0: 
    SendChar(' ') 
  else: 
    SendByte(numBars-1,True) 
 
 
######################################################################## 
# 
# Vertical Graph Testing Routines 
# 
 
def ClearVBar(col): 
  #remove all elements on a vertical bar 
  for row in range(4): 
    GotoXY(row,col) 
    SendByte(0x20,True) 
 
def VBar(height,col): 
  #creates a vertical bar at specified column 
  #expects height of 1 (min) to 32 (max) 
  #Must load vertical bar symbols prior to calling 
  fullChars = height / 8 
  bars = height % 8 
  row = 3 
  ClearVBar(col) 
  for count in range(fullChars): 
    ShowBars(row,col,8) 
    row -= 1 
  if bars>0: 
    ShowBars(row,col,bars) 
 
def VBarTest(numCycles=4): 
  LoadSymbolBlock(verticalBars) 
  LabelTest('Vert') 
  for count in range(numCycles): 
    for col in range(15): 
      height = random.randint(1,32) 
      VBar(height,col) 
    time.sleep(1) 
 
def SineGraph(numCycles=4): 
  #print a sin wave function using vertical bars. 
  #this is a sample application of the VBar routine. 
  #the 'sine' list emulates the following formula: 
  #radians=x*2*math.pi/15; y = math.sin(radians)*15 + 16 
  sine = [16,13,27,2,31,29,25,19,3,7,3,40,2,15,10] 
  LoadSymbolBlock(verticalBars) 
#  LabelTest('Sine')
  for count in range(numCycles):
    for step in range(15):
      for col in range(20): 
        x = col+step 
        VBar(sine[x%15],col) 
      time.sleep(0.2) 
 
def IncrementVBar(col,height): 
  #increaase the number of vertical bars by one 
  fullChars = height / 8 
  bars = height % 8 
  ShowBars(3-fullChars,col,bars+1) 
 
def DecrementVBar(col,height): 
  #decrease the number of vertical bars by one 
  height -= 1 
  fullChars = height / 8 
  bars = height % 8 
  ShowBars(3-fullChars,col,bars) 
 
def AnimatedVBar(col,newHeight,oldHeight=0): 
  diff = newHeight - oldHeight 
  for count in range(abs(diff)): 
    if diff>0: 
      IncrementVBar(col,oldHeight) 
      oldHeight +=1 
    else: 
      DecrementVBar(col,oldHeight) 
      oldHeight -=1 
    time.sleep(0.02)
 
def AnimatedVBarTest(): 
  time.sleep(0.5)
  LoadSymbolBlock(verticalBars) 
  ClearDisplay()
#  LabelTest('VBar') 
  graph = [0]*20 
  while (True): 
    for col in range(20): 
      switchValues = CheckSwitches()
      if switchValues[0] == 1:
        return
      elif switchValues[1] == 1:
        xbmc.Input.ExecuteAction(action="playpause")
      elif switchValues[2] == 1:
        XBMCVolDown()
      elif switchValues[3] == 1:
        XBMCVolUp()
      height = random.randint(1,32) 
      AnimatedVBar(col,height,graph[col]) 
      graph[col] = height 

#######################################################################
#
# XBMC Functions
#

def InitXBMC():
  global xbmc
  xbmc = jsonrpclib.Server("http://localhost:8080/jsonrpc")
  WaitForXBMC()

def WaitForXBMC():
  ClearDisplay()
  GotoLine(1)
  ShowMessage("    Waiting for")
  GotoLine(2)
  ShowMessage("  XBMC to start...")
  while (True):
    try:
      result = xbmc.JSONRPC.Ping()
      if result == "pong":
        return
    except:
      time.sleep(0.5)
  return

def LetsParty():
  ClearDisplay()
  GotoLine(1)
  ShowMessage("     Party Mode")
  LoadSymbolBlock(party)
  GotoXY(2,9)
  for count in range(4):
    SendByte(count,True)
  GotoXY(3,9)
  for count in range(4,7):
    SendByte(count,True)
  xbmc.Player.Open({"partymode": "music"})
  playing = "false"
  while (playing == "false"):
    try:
      result = xbmc.Player.GetItem(playerid=0, properties=["title", "album", "artist"])
      if result:
        playing = "true"
    except:
      time.sleep(0)
    time.sleep(0.2)

def NowPlaying():
  time.sleep(0.5)
  result = xbmc.Player.GetActivePlayers()
  playerID = result[0]['playerid']
  playerType = result[0]['type']
  if playerType == "audio":
    result = xbmc.Player.GetItem(playerid=playerID, properties=["title", "album", "artist"])
    artist = result["item"]["artist"][0]
    album = result["item"]["album"]
    title = result["item"]["title"]
  elif playerType == "video":
    if xbmc.Player.GetItem(playerid=1,properties=["showtitle"])["item"]["type"] == "episode":
      result = xbmc.Player.GetItem(playerid=1,properties=["showtitle", "title"])
      title = result["item"]["title"]
      artist = result["item"]["showtitle"]
      album = " "
    else:
      result = xbmc.Player.GetItem(playerid=playerID, properties=["title"])
      title = result["item"]["title"]
      album = " "
      artist = " "
  DisplayNowPlaying(artist, album, title, playerType)
  while (True):
    switchValues = CheckSwitches() 
    if switchValues[0] == 1:
      AnimatedVBarTest()
      DisplayNowPlaying(artist, album, title, playerType)
    if switchValues[1] == 1:
      xbmc.Input.ExecuteAction(action="playpause")
      if xbmc.Player.GetProperties(playerid=playerID, properties=["speed"])["speed"] == 0:
        LoadSymbolBlock(pause)
        GotoXY(0,16)
        for count in range(len(pause)):
          SendByte(count,True) 
      elif xbmc.Player.GetProperties(playerid=playerID, properties=["speed"])["speed"] == 1:
        LoadSymbolBlock(musicNote)
        GotoXY(0,16)
        for count in range(len(musicNote)):
          SendByte(count,True) 
      time.sleep(1)
      switchValues = CheckSwitches()
      if switchValues[1] == 1:
        xbmc.Input.ExecuteAction(action="stop")
        time.sleep(1)
        ClearDisplay()
        return
    elif switchValues[2] == 1:
      xbmc.Input.ExecuteAction(action="skipprevious")
    elif switchValues[3] == 1:
      xbmc.Input.ExecuteAction(action="skipnext")
    try:
      if playerType == "audio":
        result = xbmc.Player.GetItem(playerid=playerID, properties=["title", "album", "artist"])
        newartist = result["item"]["artist"][0]
        newalbum = result["item"]["album"]
        newtitle = result["item"]["title"]
        if newtitle != title:
          artist = newartist
          album = newalbum
          title = newtitle
          DisplayNowPlaying(artist, album, title, playerType)
      elif playerType == "video":
        result = xbmc.Player.GetItem(playerid=playerID, properties=["title"])
        newtitle = result["item"]["title"]
        if newtitle != title:
          title = newtitle
          DisplayNowPlaying(artist, album, title, playerType)
      time.sleep(0.03)
    except:
      ClearDisplay()
      return

def DisplayNowPlaying(artist, album, title, playerType):
  ClearDisplay()
  GotoLine(0)
  ShowMessage("Now Playing:")
  if playerType == "audio":
    LoadSymbolBlock(musicNote)
    GotoXY(0,16)
    for count in range(len(musicNote)):
      SendByte(count,True)
    GotoLine(1)
    ShowMessage(artist[:20])
    GotoLine(2)
    ShowMessage(album[:20])
    GotoLine(3)
    ShowMessage(title[:20])
  elif playerType == "video":
    response = xbmc.Player.GetItem(playerid=1, properties=["title"])
    if response['item']['type'] == "song":
      icon = iPlayer
      LoadSymbolBlock(iPlayer)
      ShowMessageWrap(title,1)
    elif response["item"]["type"] == "episode":
      icon = movie
      LoadSymbolBlock(movie)
      GotoLine(1)
      ShowMessage(xbmc.Player.GetItem(playerid=1, properties=["showtitle"])["item"]["showtitle"])
      ShowMessageWrap(title,2)
    else:
      icon = movie
      LoadSymbolBlock(movie)
      ShowMessageWrap(title,1)
    GotoXY(0,16)
    for count in range(len(icon)):
      SendByte(count,True)

def XBMCVolUp():
  CurrentVolume = GetVolume()
  if CurrentVolume < 100:
    xbmc.Application.SetVolume(volume=CurrentVolume+10)
  DisplayVolume()

def XBMCVolDown():
  CurrentVolume = GetVolume()
  if CurrentVolume > 0:
    xbmc.Application.SetVolume(volume=CurrentVolume-10)
  DisplayVolume()

def GetVolume():
  response = xbmc.Application.GetProperties(properties=["volume"])
  return response["volume"]

def DisplayVolume():
  CurrentVolume = GetVolume()
  ClearDisplay()
  GotoLine(1)
  ShowMessage("Volume: " + str(CurrentVolume))
  time.sleep(2)
  ClearDisplay()
  return

def DisplayWeather():
  ClearDisplay()
  LoadSymbolBlock(weather)
  try:
    response=urllib2.urlopen('http://74.125.228.100',timeout=1)
    internetConnection = True
  except:
    internetConnection = False
  if internetConnection == True:
    # Set variables
    response          = pywapi.get_weather_from_yahoo("UKXX0563")
    CurrentDay        = response["forecasts"][0]["day"]
    CurrentTempLow    = str(response["forecasts"][0]["low"])
    CurrentTempHigh   = str(response["forecasts"][0]["high"])
    CurrentText       = response["condition"]["text"]
    NextDay           = response["forecasts"][1]["day"]
    NextTempLow       = str(response["forecasts"][1]["low"])
    NextTempHigh      = str(response["forecasts"][1]["high"])
    NextText          = response["forecasts"][1]["text"]
    NextNextDay       = response["forecasts"][2]["day"]
    NextNextTempLow   = str(response["forecasts"][2]["low"])
    NextNextTempHigh  = str(response["forecasts"][2]["high"])
    NextNextText      = response["forecasts"][2]["text"]

    # Display inital text
    GotoLine(0)
    ShowMessage("Forecast for " + CurrentDay + ":")
    GotoLine(1)
    ShowMessage(CurrentTempLow)
    SendByte(1,True)
    ShowMessage(CurrentTempHigh)
    SendByte(0,True)
    ShowMessage("C")
    GotoLine(2)
    ShowMessage(CurrentText)

    # Switches
    while (True):
      switchValues = CheckSwitches()
      if switchValues[0] == 1:
        ClearDisplay()
        return
      elif switchValues[1] == 1:
        ClearDisplay()
        GotoLine(0)
        ShowMessage("Forecast for " + CurrentDay + ":")
        GotoLine(1)
        ShowMessage(CurrentTempLow)
        SendByte(1,True)
        ShowMessage(CurrentTempHigh)
        SendByte(0,True)
        ShowMessage("C")
        GotoLine(2)
        ShowMessage(CurrentText)
      elif switchValues[2] == 1:
        ClearDisplay()
        GotoLine(0)
        ShowMessage("Forecast for " + NextDay + ":")
        GotoLine(1)
        ShowMessage(NextTempLow)
        SendByte(1,True)
        ShowMessage(NextTempHigh)
        SendByte(0,True)
        ShowMessage("C")
        GotoLine(2)
        ShowMessage(NextText)
      elif switchValues[3] == 1:
        ClearDisplay()
        GotoLine(0)
        ShowMessage("Forecast for " + NextNextDay + ":")
        GotoLine(1)
        ShowMessage(NextNextTempLow)
        SendByte(1,True)
        ShowMessage(NextNextTempHigh)
        SendByte(0,True)
        ShowMessage("C")
        GotoLine(2)
        ShowMessage(NextNextText)
        time.sleep(3)
        ClearDisplay()
        return
  else:
    GotoLine(1)
    ShowMessage("  The Internet is")
    GotoLine(2)
    ShowMessage("required for weather")
    time.sleep(3)
    return

def DisplayPiInfo():
  temp = str(int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1e3)[:4]
  

######################################################################## 
# 
# Main Program 
# 

print "Pi LCD4 program starting."
InitIO() #Initialization 
InitLCD() 
InitXBMC()
BigClock() #Something actually useful 
 
# END #############################################################
