#!/usr/bin/env python3
import speech_recognition as sr
import time
import subprocess
import sys

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening for 'biscuit' (Speak clearly into the microphone)...")
        
        try:
            # Listen indefinitely but evaluate in chunks
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            print("Processing audio...")
            
            # Using Google's speech recognition
            text = recognizer.recognize_google(audio).lower()
            print(f"I heard: '{text}'")
            
            # Check if the word "biscuit" was spoken
            if "biscuit" in text:
                print("Command recognized! Triggering biscuit handover...")
                return True
                
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass # Ignore unrecognized audio
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            
    return False

if __name__ == "__main__":
    print("Voice Control Started.")
    while True:
        if listen_for_command():
            print("Running biscuit_main.py...")
            try:
                # Provide the full path to python in the env or use current sys.executable
                subprocess.run([sys.executable, "biscuit_main.py"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running biscuit_main.py: {e}")
            except FileNotFoundError:
                print("Error: biscuit_main.py not found.")
            
            # Wait a bit before listening again to avoid accidental double triggers
            time.sleep(5)
        time.sleep(0.1)
