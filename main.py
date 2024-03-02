#
# PROVIDED BANDLAB URL MUST BE /track/ IN ORDER FOR IT TO WORK PROPERLY.
# COPY LINK AFTER LOADING THE BANDLAB PAGE TO GET THE CORRECT URL!
#

from openai import OpenAI
import requests
import os
import sys
client = OpenAI(api_key='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')

if len(sys.argv) > 1:                                                                   # Is there a URL argument? If so, set url to the arg.
   url = sys.argv[1] 
else:                                                                                   # Else, ask for the URL via input.
   url = input("Url: ")

fileCode = url.split("track/")[1]                                                       # Split the BandLab url to just the ending arguments. Later used to get podcast file URL via their API.
directCode = fileCode.split("?")[0]                                                     # Gets just the code without the extra "sharedKey" argument so that it can be used as a transcription file name (removes everything after ? in the URL).


if not os.path.isfile(f'{directCode}.txt'):                                             # Is there already a transcription for the provided podcast?
    
  podcastInfoURL = "https://www.bandlab.com/api/v1.3/posts/" + fileCode                 # Create the podcast data API call URL.


  podcastInfoReq = requests.get(podcastInfoURL).json()                                  # Get podcast data.

  podcastInfo = {"name": podcastInfoReq["creator"]["name"], "file": podcastInfoReq["revision"]["mixdown"]["file"]}  # Create a dict for easier access to podcast data.

  podcastFileReq = requests.get(podcastInfo["file"], params={"downloadformat": "m4a"})  # Download podcast .m4a file from BandLab API.

  with open(f'{directCode}.m4a', mode="wb") as file:                                    # Create .m4a file and write the file data to it.
      file.write(podcastFileReq.content)
      file.close()

  audio_file = open(f'{directCode}.m4a', "rb")                                          # Open the audio file and send the data to OpenAI for transcription.
  transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file, 
    response_format="text"
  )
  audio_file.close()
  with open(f'{directCode}.txt', mode="w") as file:                                     # Write the transcription text to a file for later usage, saving money because transcription is expensive.
      file.write(transcript)
      file.close()

  response = client.chat.completions.create(                                            # Get summary of podcast.
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You summarize podcasts within 4-6 sentences with simple terms and direct style."},
      {"role": "user", "content": transcript},
    ]
  )
  os.remove(f'{directCode}.m4a')                                                        # Delete audio file.
  print(response.choices[0].message.content)
  
  
else:
  transFile = open(f'{directCode}.txt')                                                 # Get pre-exisitng transcription file.
  response = client.chat.completions.create(                                            # Get summary of podcast.
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You summarize podcasts within 4-6 sentences with simple terms and direct style."},
      {"role": "user", "content": transFile.read()},
    ]
  )
  transFile.close()

  if os.path.isfile(f'{directCode}.m4a'):                                               # Delete audio file, if it exists. Redundant considering that it should delete it when it's originally made, included just in case.
    os.remove(f'{directCode}.m4a')

  print(response.choices[0].message.content)