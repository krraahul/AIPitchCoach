# from transformers import pipeline
# from typing import AsyncIterator


# def audio_preprocessing_node(chunks: AsyncIterator[int]):
#     SAMPLING_RATE = 16000
#     CHANNEL = 1
#     DURATION = 25 # 25 SECONDS AUDIO PROCESSING

    

import sounddevice as sd

device_info = sd.query_devices(kind='input')

print(f"Device Name:          {device_info['name']}")
print(f"Default Samplerate:   {device_info['default_samplerate']} Hz")

def callback(indata, outdata, frames, time_info, status):
    # indata: Contains the fresh microphone audio
    # outdata: Ready to receive whatever you want to play out of the speakers
    
    # Example: A simple "passthrough" echo effect
    # We copy the microphone input directly to the speaker output
    #print(frames)
    print(len(indata))
    print(status)
    outdata[:] = indata


# This starts a stream that listens and repeats everything it hears
with sd.Stream(channels=1, callback=callback, samplerate=16000):
    sd.sleep(5000) # Run for 5 seconds
