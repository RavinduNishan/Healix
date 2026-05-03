import speech_recognition as sr
import sys

def main():
    r = sr.Recognizer()
    print("\n" + "="*40)
    print("🎤 MICROPHONE TEST 🎤")
    print("="*40)
    print("(You can ignore any ALSA/JACK errors printed above)\n")
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for background noise (stay quiet for 2 seconds)...")
            r.adjust_for_ambient_noise(source, duration=2)
            print("\n✅ Ready! Speak into the microphone now...")
            print("(Press Ctrl+C to stop)\n")
            
            while True:
                try:
                    # Listen for audio
                    audio = r.listen(source, timeout=None, phrase_time_limit=5)
                    print("Processing what you said...")
                    
                    # Convert to text
                    text = r.recognize_google(audio)
                    print(f"🗣️  YOU SAID: '{text}' \n")
                    
                except sr.UnknownValueError:
                    print("❌ Could not understand that, please try again.\n")
                except sr.RequestError as e:
                    print(f"⚠️  Network error: {e}\n")
    except KeyboardInterrupt:
        print("\nTest stopped.")
    except Exception as e:
        print(f"\nMicrophone Error: {e}")

if __name__ == "__main__":
    main()
