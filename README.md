# musically
This repo contains my bachelors degree project

## Roadmap

### Default user
- [x] piano roll unde se poate face zoom in si zoom out
- [x] forma geometrica a notelor din piano roll sa poata fi customizata (dreptunghi, cerc, etc)
- [x] un scroll vertical cu clape de pian ca in poza de referinta
- [x] lungimea pe orizontala a unei note va reprezenta durata notei respective
- [x] posibilitatea de a da play la o melodie si de a observa in timp real cum o bara verticala parcurge notele pe rand
- [x] A0, B0, C0 / Do, Re, Mi, Fa, ...
- [ ] vizualizari extra:
   - [ ] arc diagram
   - [ ] vertical frequency visualiser
- [ ] implementare a tabului 'Help'


### Advanced user
- [x] separarea instrumentelor care canta in acelasi timp:
   - [x] abilitatea de a selecta sau a deselecta partitura unui instrument
   - [x] colorarea diferta a instrumentelor distincte
   - [x] posibilitatea de a uni cu linii continue notele care apartin aceluiasi instrument
- [x] vizualizarea consonantelor si disonantelor
- [x] procentul de note disonante in intregimea melodiei
- [x] tooltip in cazul in care se face hover deasupra unei note care sa contina
   - [x] pitch-ul
   - [x] durata
- [ ] posibilitatea cat mai mare de a customiza figurile geometrice care reprezinta notele (culoare, marime, opacitate, contur, etc)
- [ ] extragerea de sentimente din piesa muzicala

## 03.04.2022:
   - time drift is a problem
   - apparently when you hold down click on a scrollbar it slows the animation
   - playing a wav file instead of playing each individial note due to not being
   constrained about an instrument which should be downloaded as a sound for each note,
   but this solution occasionally leads to performance issues => time drift

## 07.04.2022
   - consonant intervals:
      - 0, 3, 4, 5, 7, 8, 9, 12
   - dissonant intervals
      - 1, 2, 6, 10, 11

## 10.04.2022
   - fixed track buttons bug with connected notes
   - add mute/unmute button
   - add errors for player buttons
   - add information about the song
   - cleaned up the menu

## 11.04.2022
   - change track color using a color picker
   - fix track sidebar buttons (no more stupid 3000 offset)
   - changed the menu again
   - added note opacity

## Issues when installing
If `pygame.mixer` doesn't work:
   1.  Go to the directory where pygame is installed (you can get it by typing `pip install pygame`).
   2.  Look for the `libmpg123.dll` in pygame directory.
   3.  Copy and paste to `C:/windows/system3` and `C:/windows/sysWOW64`
   Link: https://stackoverflow.com/questions/59623969/pygame-error-failed-loading-libmpg123-dll-attempt-to-access-invalid-address

Play midi in windows (not really necessary):
   - https://ksvi.mff.cuni.cz/~dingle/2019/prog_1/python_music.html

## Links
logo image:
   - https://www.vectorstock.com/royalty-free-vector/note-music-logo-design-vector-27015396 - Artist ModalTampang

consonances and dissonances:
   - https://www.earmaster.com/music-theory-online/ch05/chapter-5-3.html

music notation meaning:
   - https://en.wikipedia.org/wiki/List_of_musical_symbols
