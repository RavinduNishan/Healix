import speech_recognition as sr
import time

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening for 'give me water' (Speak clearly into the microphone)...")
        
        try:
            # Listen indefinitely for the phrase
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            print("Processing audio...")
            
            # Using Google's speech recognition
            text = recognizer.recognize_google(audio).lower()
            print(f"I heard: '{text}'")
            
            if "water" in text and "give" in text:
                print("Command recognized! 'Give me water'")
                return True
                
        except sr.WaitTimeoutError:
            pass # Ignore and keep looping if needed
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            
    return False

if __name__ == "__main__":
    while True:
        if listen_for_command():
            break
        time.sleep(0.5)
