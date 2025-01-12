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

SPEECH_RATE = 170 # Words Per Minute
TTS_VOLUME = 5 # Supposed to cap at 1?

CLIP_DIRECTORY = "/home/pi/gex_clips/"

CLIP_GAIN = 5

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', SPEECH_RATE)
tts_engine.setProperty('volume', TTS_VOLUME)

conn = RawConnection()

clip_frequency = 0 # How often to play a clip
random_mode = False # Detemine if jokes are random or happen on schedule


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

        return


    except:
        tts("Unable to Play File")



def main():

    # Check if input avaiblible from remote
    if conn.has_data():

        # Read the keypress
        keypress = conn.readline(0)
        
        if keypress != None:

            data = keypress.split()
            sequence = data[1]
            command = data[2]

            # Check if repeat
            if sequence != "00":

                # Switch based on Keypressed

                if command == "KEY_MENU":
                    # Poweroff pi
                    tts("Powering off Gex. You can unplug me after the green light stops blinking.")
                    subprocess.call("sudo poweroff", shell=True)

                elif command == "KEY_MUTE":
                    # Disable output
                    tts("Gex is disabled.")
                    clip_frequency = 0

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





tts("Gex Speaker is Live.")
tts("Please select a number to activate")

while True:         
      main()