'''
Load audio files from specficed directory and play them at random times

'''

from lirc import RawConnection, AsyncConnection
from os import listdir
from os.path import isfile, join
import asyncio
import pyttsx3
import subprocess
import random
import time

SPEECH_RATE = 170 # Words Per Minute
TTS_VOLUME = 5 # Supposed to cap at 1?

CLIP_DIRECTORY = "/home/pi/gex_clips/"

CLIP_GAIN = 5

UPDATE_INTERVAL = 5 # Seconds between checks for playing clip

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', SPEECH_RATE)
tts_engine.setProperty('volume', TTS_VOLUME)

conn = RawConnection()

clip_interval = 0 # Seconds between clips
random_mode = False # Detemine if jokes are random or happen on schedule
last_clip_update = time.time() # Last time since update for the clip play
last_clip_played = time.time() # Last time clip was played


def tts(text):
    tts_engine.say(text)
    tts_engine.runAndWait()


def _play_clip(file_path):
    return subprocess.run(["cvlc", "--gain", str(CLIP_GAIN), "--play-and-exit", "-A", "alsa", "--alsa-audio-device", "sysdefault:CARD=Headphones", file_path])


def play_random_clip():

    # Get all files from clip directory
    files = [f for f in listdir(CLIP_DIRECTORY) if isfile(join(CLIP_DIRECTORY, f))]

    # Suppose all files are audio, but catch if not
    try:

        # Shuffle the file list and pick the first one
        random.shuffle(files)
        f_path = CLIP_DIRECTORY + files.pop()

        # Play the clip
        _play_clip(f_path)

        return 1


    except:
        tts("Unable to Play File")
        return 0



def main():

    global clip_interval, random_mode, last_clip_update, last_clip_played

    # Read the keypress
    keypress = conn.readline(0)
    
    if keypress != None:

        data = keypress.split()
        sequence = data[1]
        command = data[2]

        print(command)

        # Check if repeat
        if sequence == "00":

            # Switch based on Keypressed

            if command == "KEY_MENU":
                # Poweroff pi
                tts("Powering off Gex. You can unplug me after the green light stops blinking.")
                subprocess.call("sudo poweroff", shell=True)

            elif command == "KEY_MUTE":
                # Disable output
                tts("Gex is disabled.")
                clip_interval = 0

            elif command == "KEY_RIGHT":
                # Random Mode
                tts("Gex will give out quotes randomly.")
                random_mode = True

            elif command == "KEY_LEFT":
                # Sceduled Mode
                tts("Gex will give out quotes periodicly.")
                random_mode = False

            elif command == "KEY_ENTER":
                # Play a clip
                play_random_clip()
                last_clip_played = time.time()

            elif command == "KEY_1":
                # Minute
                tts("Gex is set to one clip per minute.")
                clip_interval = 60
            
            elif command == "KEY_2":
                # 5 Minute
                tts("Gex is set to one clip every five minutes.")
                clip_interval = 60*5

            elif command == "KEY_3":
                # 10 Minute
                tts("Gex is set to one clip every ten minutes.")
                clip_interval = 60*10

            elif command == "KEY_4":
                # 15 Minute
                tts("Gex is set to one clip every fifteen minutes.")
                clip_interval = 60*15

            elif command == "KEY_5":
                # 20 Minute
                tts("Gex is set to one clip every twenty minutes.")
                clip_interval = 60*20
            
            elif command == "KEY_6":
                # 30 Minute
                tts("Gex is set to one clip every half hour.")
                clip_interval = 60*30

            elif command == "KEY_7":
                # 45 Minute
                tts("Gex is set to one clip every fourty five minutes.")
                clip_interval = 60*45
            
            elif command == "KEY_8":
                # 60 Minute
                tts("Gex is set to one clip every hour.")
                clip_interval = 60*60
            
            elif command == "KEY_9":
                # 120 Minute
                tts("Gex is set to one clip every two hours.")
                clip_interval = 60*120

            elif command == "KEY_0":
                # 120 Minute
                tts("Gex is set to one clip every day.")
                clip_interval = 60*60*24
            


    # Check if muted
    if clip_interval == 0:
        return

    # Check if a update interval has passed
    if time.time() - last_clip_update > UPDATE_INTERVAL:

        last_clip_update = time.time()

        if random_mode:

            # If random, calculate probality based on clip_interval, then roll the dice
            rand_threshold = UPDATE_INTERVAL / clip_interval

            if random.random() < rand_threshold:
                play_random_clip()
                last_clip_played = time.time()
        
        else:

            # If schecudled, then see if due for another clip to play
            if time.time() - last_clip_played > clip_interval:
                play_random_clip()
                last_clip_played = time.time()







tts("Gex Speaker is online.")
tts("Please select a number to activate")

while True:         
    main()