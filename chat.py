# -*- coding: utf-8 -*-

from datetime import date
from io import BytesIO
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

import google.generativeai as genai
from gtts import gTTS
from pygame import mixer 
import speech_recognition as sr
import sounddevice 

mixer.pre_init(frequency=24000, buffer=2048) 
mixer.init()

# add your Google Gemini API key here
my_api_key = "AIzaSyAn078Ihmc0I0JRY_TRwG61F94TaFofzf8"

if len(my_api_key) < 5:
    print(f"Please add your Google Gemini API key in the program. \n ")
    quit() 

# set Google Gemini API key as a system environment variable or add it here
genai.configure(api_key=my_api_key)

# model of Google Gemini API
model = genai.GenerativeModel("gemini-1.5-flash",
    generation_config=genai.GenerationConfig(
        candidate_count=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=60, # 100 tokens correspond to roughly 60-80 words.
        temperature=0.9,
    ))

# start the chat model 
chat = model.start_chat(history=[])

today = str(date.today())

# Initialize the counters  
numtext = 0 
numtts = 0 
numaudio = 0

# Function for text generation 
def chatfun(request, text_queue):
    global numtext, chat 
    
    response = chat.send_message(request, stream=True)
    shortstring = ''  
    ctext = ''
    
    for chunk in response:
        try:
            if chunk.candidates[0].content.parts:
                ctext = chunk.candidates[0].content.parts[0].text
                ctext = ctext.replace("*", "")
                
                if len(shortstring) > 10 or len(ctext) > 10:
                    shortstring = "".join([shortstring, ctext])
                    text_queue.append(shortstring)
                    print(shortstring, end='')
                    shortstring = ''
                    numtext += 1
                else:
                    shortstring = "".join([shortstring, ctext])
                    ctext = ''
                
        except Exception as e:
            continue 

    if len(ctext) > 0: 
        shortstring = "".join([shortstring, ctext])
        
    if len(shortstring) > 0: 
        print(shortstring, end='') 
        text_queue.append(shortstring)                         
        numtext += 1
        
    if numtext > 0: 
        append2log(f"AI: {response.candidates[0].content.parts[0].text}\n")
    
# convert "text" to audio file and play back 
def speak_text(text):
    global numtts
    
    mp3file = BytesIO()
    tts = gTTS(text, lang="en", tld='us') 
    tts.write_to_fp(mp3file)

    mp3file.seek(0)
    print("AI: ", text)
    
    try:
        mixer.music.load(mp3file, "mp3")
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.2)   

    except KeyboardInterrupt:
        mixer.music.stop()

# Main function  
def main():
    global today, numtext, numtts
    
    rec = sr.Recognizer()
    mic = sr.Microphone()
    
    rec.dynamic_energy_threshold = False
    rec.energy_threshold = 400   
  
    sleeping = True 
    
    # while loop for conversation 
    while True:     
        with mic as source:            
            rec.adjust_for_ambient_noise(source, duration=0.5)

            try: 
                print("Listening ...")                
                audio = rec.listen(source, timeout=10) 
                text = rec.recognize_google(audio, language="en-EN") 
                
                if len(text) > 0:
                    print(f"You: {text}\n")
                else:
                    continue  
                
                if sleeping:
                    if "rexy" in text.lower():
                        request = text.lower().split("rexy")[1]
                        print("rexy RECEIVED")
                        sleeping = False
                        chat = model.start_chat(history=[])
                        append2log(f"_"*40)                    
                        today = str(date.today())  
                        if len(request) < 2:
 
                            speak_text("Hi, there, how can I help?")
                            #append2log(f"AI: Hi, there, how can I help? \n")
                            continue                       
                    else:
                        continue
                else: 
                    request = text.lower()
                    if "that's all" in request:
                        append2log(f"You: {request}\n")
                        speak_text("Bye now")
                        append2log(f"AI: Bye now.\n")                        
                        sleeping = True
                        continue
                    
                    if "rexy" in request:
                        request = request.split("rexy")[1]

                if len(request) == 0:
                    continue                
                      
                append2log(f"You: {request}\n ")

                # Initialize the counters before each reply from AI 
                numtext = 0 
                numtts = 0 
                text_queue = []

                chatfun(request, text_queue)
                
                for text in text_queue:
                    speak_text(text)
                    numtts += 1

            except Exception as e:
                continue 
   
def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a", encoding='utf-8') as f:
        f.write(text + "\n")

if __name__ == "__main__":
    main()
