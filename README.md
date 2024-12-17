# Overcooked! 2 save player transfer.
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)  


## Summary
The game Overcooked! 2 made by Team17 encrypts its save files using the game id of the player. 
You can find your game id here: C:\Users\your_username\AppData\LocalLow\Team17\Overcooked2\Saves
There will be a folder in there that folder's number is your game id.


This tool has only be tested using GOG game id but should work with any game id i.e. epic games or steam. 
But essentially it will allow you to transfer ownership of the saves to a friend.
You will need both the owners game id and the friends game id to do this!

## Usage
Python 3 required (tested on Python 3.7)
Once python is installed to launch the app do the following.
Open CMD and get to the directory of this repo i.e. 
'cd C:\Users\your_username\Downloads\OC2_Save_Transfer'
This will then put you in the correct directory then run this command.
'pip install -r requirements.txt'
This installs the needed modules for the python program to run then finally launch the program using this command.
'python oc2_gui.py'
Then you'll see a GUI open and just enter all the info required and you should have converted a friends save to your save.

## Issues
The user interface could look better any suggestions for improvements i'm all ears.
Not certain if it will 100% work with every save file but worth testing as it might!

## Licensing
This software is licensed under the terms of Apache 2.0.  
You can find a copy of the license in the LICENSE file.
