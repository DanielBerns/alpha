I want a static site generator, written with python. The goal of the static site is to show different images (each one with some text and audio)
The input has a folder structure like this

./project_alpha
  |
  |-> config.yml 
  |
  |---- resources
  |     |
  |     |---- images
  |     |      |
  |     |      |-> image_1.jpg 
  |     |      |-> image_2.png
  |     |      |-> image_3.gif
  |     |      |-> image_4.jpg
  |     |      |-> ...
  |     |      |-> image_N.jpg
  |     |      
  |     |---- audio
  |     |      |
  |     |      |-> audio_1.mp3 
  |     |      |-> audio_2.ogg
  |     |      |-> audio_3.wav
  |
  |----- pages
         |
         |-> page_1.md
         |-> page_2.md
         |-> page_3.md
         |-> ...
         |-> page_N.md

where the files page_{i}.md have text mixed with links to the resources.
The static site generator must generate a local git repo with all the content (html, images, audio, javascript and css) to be easily deployed. 
Add a readme.md with instructions to link the local git repo to github.
