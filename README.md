# musically
This repo contains my bachelors degree project

If `pygame.mixer` doesn't work:
   1.  Go to the directory where pygame is installed (you can get it by typing `pip install pygame`).
   2.  Look for the `libmpg123.dll` in pygame directory.
   3.  Copy and paste to `C:/windows/system3` and `C:/windows/sysWOW64`
   Link: https://stackoverflow.com/questions/59623969/pygame-error-failed-loading-libmpg123-dll-attempt-to-access-invalid-address

Play midi in windows (not really necessary):
   - https://ksvi.mff.cuni.cz/~dingle/2019/prog_1/python_music.html

Convert `midi` to `wav` in linux:
```
   timidity song.mid -Ow -o song.wav
```

03.04.2022:
   - time drift is a problem
   - apparently when you hold down click on a scrollbar it slows the animation
