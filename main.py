'''
Load audio files from specficed directory and play them at random times

'''

from lirc import RawConnection
from os import listdir
from os.path import isfile, join
import asyncio
import pyttsx3
import subprocess
import random
import time

SPEECH_RATE = 160 # Words Per Minute
TTS_VOLUME = 6 # Supposed to cap at 1?

CLIP_GAIN = 7

UPDATE_INTERVAL = 5 # Seconds between checks for playing clip

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', SPEECH_RATE)
tts_engine.setProperty('volume', TTS_VOLUME)

conn = RawConnection()


play_interval = 0 # Seconds between playing clips
random_mode = False # Detemine if jokes are random or happen on schedule
last_clip_update = time.time() # Last time since update for the clip play
last_clip_played = time.time() # Last time clip was played


''' intro_list and name_list should be 1 element longer than directory_list -> For random clips'''
clip_directory_list = ["/home/pi/gex_clips/", "/home/pi/dunkey_clips/"] # Locations to pull clips from
clip_intro_list = ["/home/pi/gex_clips/Heeeeerrrrreee_ssss_GEXY!.wav", "/home/pi/dunkey_clips/heyalexitsreggie.wav", None] # Clip to play when changing clip speaker
clip_name_list = ["Gex", "Dunky", "Random"] # Names of the clip speakers



def tts(text):
    tts_engine.say(text)
    tts_engine.runAndWait()


def _play_clip(file_path):
    return subprocess.run(["cvlc", "--gain", str(CLIP_GAIN), "--play-and-exit", "-A", "alsa", "--alsa-audio-device", "sysdefault:CARD=Headphones", file_path])


def play_specfic_clip(file_path):

    # Catch if the file is not real / audio
    try:

        # Play the clip
        _play_clip(file_path)

        return 1

    except:
        tts("Unable to Play File")
        return 0


def play_random_clip(directory_path):

    # Get all files from clip directory
    files = [f for f in listdir(directory_path) if isfile(join(directory_path, f))]

    # Suppose all files are audio, but catch if not
    try:

        # Shuffle the file list and pick the first one
        random.shuffle(files)
        f_path = directory_path + files.pop()

        # Play the clip
        _play_clip(f_path)

        return 1


    except:
        tts("Unable to Play File")
        return 0


def get_speaker_directory(c_ind):

    # Check if index is equal to directory_list length -> Random speaker
    if c_ind == len(clip_directory_list):
        return clip_directory_list[random.randint(0,len(clip_directory_list)-1)]
    else:
        return clip_directory_list[c_ind]


def main():

    global play_interval, random_mode, last_clip_update, last_clip_played, clip_index

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
                tts("Powering off. You can unplug me after the green light stops blinking.")
                subprocess.call("sudo poweroff", shell=True)

            elif command == "KEY_MUTE":
                # Disable output
                tts("Clips are disabled.")
                play_interval = 0

            elif command == "KEY_RIGHT":
                # Random Mode
                tts(clip_name_list[clip_name_list] + " will give out quotes randomly.")
                random_mode = True

            elif command == "KEY_LEFT":
                # Sceduled Mode
                tts(clip_name_list[clip_name_list] + " will give out quotes periodicly.")
                random_mode = False

            elif command == "KEY_UP":
                # Increse speaker index
                clip_index = clip_index + 1
                if clip_index > len(clip_directory_list):
                    clip_index = 0

                # If intro clip is not avaiable, then use tts
                if clip_intro_list[clip_index] == None or not play_specfic_clip(clip_intro_list[clip_index]):
                    tts("Speaker is set to " + clip_name_list[clip_name_list] + ".")

            elif command == "KEY_DOWN":
                # Decrease speaker index
                clip_index = clip_index - 1
                if clip_index < 0:
                    clip_index = len(clip_directory_list)

                # If intro clip is not avaiable, then use tts
                if clip_intro_list[clip_index] == None or not play_specfic_clip(clip_intro_list[clip_index]):
                    tts("Speaker is set to " + clip_name_list[clip_name_list] + ".")

            elif command == "KEY_ENTER":
                # Play a clip
                play_random_clip(get_speaker_directory(clip_index))
                last_clip_played = time.time()

            elif command == "KEY_1":
                # Minute
                tts(clip_name_list[clip_name_list] + " is set to one clip per minute.")
                play_interval = 60
            
            elif command == "KEY_2":
                # 5 Minute
                tts(clip_name_list[clip_name_list] + " is set to one clip every five minutes.")
                play_interval = 60*5

            elif command == "KEY_3":
                # 10 Minute
                tts(clip_name_list[clip_name_list] + " is set to one clip every ten minutes.")
                play_interval = 60*10

            elif command == "KEY_4":
                # 15 Minute
                tts(clip_name_list[clip_name_list] + " is set to one clip every fifteen minutes.")
                play_interval = 60*15

            elif command == "KEY_5":
                # 30 Minute
                tts(clip_name_list[clip_name_list] + " is set to one clip every half hour.")
                play_interval = 60*30
            
            elif command == "KEY_6":
                # 60 Minutes
                tts(clip_name_list[clip_name_list] + " is set to one clip every hour.")
                play_interval = 60*60

            elif command == "KEY_7":
                # 120 Minute
                tts(clip_name_list[clip_name_list] + " is set to one clip every two hours.")
                play_interval = 60*120
            
            elif command == "KEY_8":
                # 6 hours
                tts(clip_name_list[clip_name_list] + " is set to one clip every six hours.")
                play_interval = 60*60*6
            
            elif command == "KEY_9":
                # 12 hours
                tts(clip_name_list[clip_name_list] + " is set to one clip every twelve hours.")
                play_interval = 60*60*12

            elif command == "KEY_0":
                # 24 hours
                tts(clip_name_list[clip_name_list] + " is set to one clip every day.")
                play_interval = 60*60*24


    # Check if muted
    if play_interval == 0:
        return

    # Check if a update interval has passed
    if time.time() - last_clip_update > UPDATE_INTERVAL:

        last_clip_update = time.time()

        if random_mode:

            # If random, calculate probality based on play_interval, then roll the dice
            rand_threshold = UPDATE_INTERVAL / play_interval

            if random.random() < rand_threshold:
                play_random_clip(get_speaker_directory(clip_index))
                last_clip_played = time.time()
        
        else:

            # If schecudled, then see if due for another clip to play
            if time.time() - last_clip_played > play_interval:
                play_random_clip(get_speaker_directory(clip_index))
                last_clip_played = time.time()


tts("Clip Speaker is online.")
tts("Please select a number to activate")

while True:         
    main()