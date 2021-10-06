## Processing Pipeline
### Normalizing
* Remove extraneous punctuation: commas, semicolons, colons, exclamations, questions, etc
* Expand apostrophies when needed: it's -> it is
* Avoid incorrect apostrophy expansion: David's -> David is
* Extract a file as a list of lines
* Substitute \r\n with a period ("."):  re.sub("\\r\\n", ".", s.decode("utf-8"))
* Save the original URL and the original namings as well as the normalized ones. Use the normalized versions for storage in the Database and the originals for displaying to the user.



### Load a Reference Dictionary
```python
dictionary_name = "/usr/share/dict/web2"
dictionary = word_set(dictionary_name)
```



### Get File Name
```python
>>> names[1000]
>>> 'Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt'

# convert name to path object for easy name extraction
from pathlib import Path
name = Path(names[1000])
>>> name
>>> PosixPath('Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt')
>>> name.name
>>> 'Kataklysm_Face the Face of War.txt'

# name without the extension
>>> name.stem
>>> 'Kataklysm_Face the Face of War'
```



### Convert from bytes and remove the escape sequences
```python
>>> s = tar.extractfile("Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt").read()
>>> unescaped = re.sub("\\r\\n", ".", s.decode("utf-8"))
>>> unescaped
```
> "This time we went to far.This time we open the scars.To feel destruction inside this worlds addiction.Last dance for the new generation.Beloved ones virgins of war.Neverseen the true colors of sufferance..Forever face the face of war.Forever we shall face the face of war.We shall not fall, we shall stand tall.In the midst of all this pain.We will face the face of war..'Til the end of time, worlds will collide.People will die.And everyone you trust will turn on you.To save themselves from the devil's grip..Stay on guard, make sure you don't drift away.Prepare for battle bloodbath of innocent man.Guilty for taking life for taking life!..Corpse of dead man surround me.Release me from this sanctuary..Forever face the face of war.Forever we shall face the face of war..We shall not fall, we shall stand tall.In the midst of all this pain.We will face the face of war"



### Replace the double period with a single period
```python
>>> unescaped = re.sub("\.\.", ".", unescaped)
>>> unescaped
```
> "This time we went to far.This time we open the scars.To feel destruction inside this worlds addiction.Last dance for the new generation.Beloved ones virgins of war.Neverseen the true colors of sufferance.Forever face the face of war.Forever we shall face the face of war.We shall not fall, we shall stand tall.In the midst of all this pain.We will face the face of war.'Til the end of time, worlds will collide.People will die.And everyone you trust will turn on you.To save themselves from the devil's grip.Stay on guard, make sure you don't drift away.Prepare for battle bloodbath of innocent man.Guilty for taking life for taking life!.Corpse of dead man surround me.Release me from this sanctuary.Forever face the face of war.Forever we shall face the face of war.We shall not fall, we shall stand tall.In the midst of all this pain.We will face the face of war"



### Replace ellipses with a space
```python
>>> unescaped = re.sub("\.\.\.", "", unescaped)
>>> unescaped
```
> "This time we went to far.This time we open the scars.To feel destruction inside this worlds addiction.Last dance for the new generation.Beloved ones virgins of war.Neverseen the true colors of sufferance.Forever face the face of war.Forever we shall face the face of war.We shall not fall, we shall stand tall.In the midst of all this pain.We will face the face of war.'Til the end of time, worlds will collide.People will die.And everyone you trust will turn on you.To save themselves from the devil's grip.Stay on guard, make sure you don't drift away.Prepare for battle bloodbath of innocent man.Guilty for taking life for taking life!.Corpse of dead man surround me.Release me from this sanctuary.Forever face the face of war.Forever we shall face the face of war.We shall not fall, we shall stand tall.In the midst of all this pain.We will face the face of war"



### Split the sentences based on the period
```python
from pprint import pprint
pprint(unescaped.split("."))
```
> ['This time we went to far',
 'This time we open the scars',
 'To feel destruction inside this worlds addiction',
 'Last dance for the new generation',
 'Beloved ones virgins of war',
 'Neverseen the true colors of sufferance',
 'Forever face the face of war',
 'Forever we shall face the face of war',
 'We shall not fall, we shall stand tall',
 'In the midst of all this pain',
 'We will face the face of war',
 "'Til the end of time, worlds will collide",
 'People will die',
 'And everyone you trust will turn on you',
 "To save themselves from the devil's grip",
 "Stay on guard, make sure you don't drift away",
 'Prepare for battle bloodbath of innocent man',
 'Guilty for taking life for taking life!',
 'Corpse of dead man surround me',
 'Release me from this sanctuary',
 'Forever face the face of war',
 'Forever we shall face the face of war',
 'We shall not fall, we shall stand tall',
 'In the midst of all this pain',
 'We will face the face of war']



### Pickle a string
```python
myfile = open("lyrics.pickle", "wb")
pickle.dump(no_isolated_t, myfile)
myfile.close()
myfile = open("lyrics.pickle", "rb")
text = pickle.load(myfile)
myfile.close()
>>> text
```
> 'this time we went to far this time we open the scars to feel destruction inside this worlds addiction last dance for the new generation beloved ones virgins of war neverseen the true colors of sufferance forever face the face of war forever we shall face the face of war we shall not fall we shall stand tall in the midst of all this pain we will face the face of war til the end of time worlds will collide people will die and everyone you trust will turn on you to save themselves from the devil grip stay on guard make sure you do not drift away prepare for battle bloodbath of innocent man guilty for taking life for taking life corpse of dead man surround me release me from this sanctuary forever face the face of war forever we shall face the face of war we shall not fall we shall stand tall in the midst of all this pain we will face the face of war'



### Pickle a set
```python
set_ = set(no_isolated_t.split(" ")
myfile = open("lyricset.pickle", "wb")
pickle.dump(set_, myfile)
myfile.close()
myfile = open("lyricset.pickle", "rb")
loaded_set = pickle.load(myfile)
myfile.close()
>>> loaded_set
```
> {'collide', 'do', 'beloved', 'of', 'corpse', 'tall', 'people', 'virgins', 'stand', 'guard', 'time', 'pain', 'this', 'true', 'prepare', 'the', 'generation', 'neverseen', 'we', 'all', 'destruction', 'you', 'forever', 'dead', 'in', 'inside', 'on', 'devil', 'die', 'turn', 'sure', 'for', 'make', 'addiction', 'scars', 'new', 'worlds', 'from', 'ones', 'stay', 'shall', 'battle', 'innocent', 'bloodbath', 'taking', 'surround', 'will', 'war', 'me', 'far', 'dance', 'went', 'to', 'man', 'sanctuary', 'colors', 'last', 'away', 'and', 'face', 'sufferance', 'themselves', 'everyone', 'end', 'trust', 'release', 'midst', 'not', 'save', 'til', 'fall', 'guilty', 'open', 'grip', 'feel', 'drift', 'life'}



### Filter the words that appear in the built-in dictionary
```python
lyrics_set = set(no_isolated_t.split())
valid_words = words_in_dict(lyrics_set, dictionary)
>>> valid_words     # about 92% valid words
```
> {'pain', 'will', 'fall', 'make', 'you', 'do', 'turn', 'not', 'surround', 'all', 'die', 'away', 'release', 'new', 'people', 'save', 'innocent', 'end', 'open', 'from', 'for', 'went', 'shall', 'collide', 'beloved', 'everyone', 'life', 'and', 'dead', 'sanctuary', 'war', 'corpse', 'themselves', 'far', 'me', 'midst', 'til', 'man', 'guilty', 'guard', 'last', 'colors', 'tall', 'addiction', 'grip', 'stand', 'the', 'generation', 'destruction', 'to', 'in', 'prepare', 'of', 'devil', 'drift', 'feel', 'we', 'dance', 'true', 'forever', 'inside', 'sufferance', 'time', 'taking', 'sure', 'battle', 'on', 'face', 'stay', 'this', 'trust'}


# Important things to know about the program

## The major word collection is a trie
* I chose a trie because I wanted to have the ability to perform prefix lookups as well as membership tests on words that appear anywhere in the whole collection of lyrics files.  
* 


### Make a trie
_see trie.py_








# Obsolete Below This Line
### Tarfile Handling Basic Steps
```python
import tarfile
tar = tarfile.open("lyrics.tar.gz", "r:gz")
>>> tar
>>> <tarfile.TarFile object at 0x7f9b7d628250>

names = tar.getnames()
>>> len(names)
>>> 616509

>>> names[1000]
>>> 'Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt'

lyrics = tar.extractfile("Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt")
>>> lyrics
>>> <ExFileObject name='lyrics.tar.gz'>

# data is put into a buffer
>>> lyrics.read()
>>> b"This time we went to far\r\nThis time we open the scars\r\nTo feel destruction inside this worlds addiction\r\nLast dance for the new generation\r\nBeloved ones... virgins of war\r\nNeverseen the true colors of sufferance\r\n\r\nForever... face the face of war\r\nForever... we shall face the face of war\r\nWe shall not fall, we shall stand tall\r\nIn the midst of all this pain\r\nWe will face the face of war\r\n\r\n'Til the end of time, worlds will collide\r\nPeople will die\r\nAnd everyone you trust will turn on you\r\nTo save themselves from the devil's grip\r\n\r\nStay on guard, make sure you don't drift away\r\nPrepare for battle... bloodbath of innocent man\r\nGuilty for taking life... for taking life!\r\n\r\nCorpse of dead man surround me\r\nRelease me from this sanctuary\r\n\r\nForever... face the face of war\r\nForever... we shall face the face of war\r\n\r\nWe shall not fall, we shall stand tall\r\nIn the midst of all this pain\r\nWe will face the face of war"

# it can only be read once
>>> lyrics.read()
>>> b''

# load it again and display as a list
lyrics = tar.extractfile("Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt")
>>> lyrics.readlines()
>>> [b'This time we went to far\r\n', b'This time we open the scars\r\n', b'To feel destruction inside this worlds addiction\r\n', b'Last dance for the new generation\r\n', b'Beloved ones... virgins of war\r\n', b'Neverseen the true colors of sufferance\r\n', b'\r\n', b'Forever... face the face of war\r\n', b'Forever... we shall face the face of war\r\n', b'We shall not fall, we shall stand tall\r\n', b'In the midst of all this pain\r\n', b'We will face the face of war\r\n', b'\r\n', b"'Til the end of time, worlds will collide\r\n", b'People will die\r\n', b'And everyone you trust will turn on you\r\n', b"To save themselves from the devil's grip\r\n", b'\r\n', b"Stay on guard, make sure you don't drift away\r\n", b'Prepare for battle... bloodbath of innocent man\r\n', b'Guilty for taking life... for taking life!\r\n', b'\r\n', b'Corpse of dead man surround me\r\n', b'Release me from this sanctuary\r\n', b'\r\n', b'Forever... face the face of war\r\n', b'Forever... we shall face the face of war\r\n', b'\r\n', b'We shall not fall, we shall stand tall\r\n', b'In the midst of all this pain\r\n', b'We will face the face of war']

# it, too, can only be read once
>>> lyrics.readlines()
>>> []
```  
Bytes objects are returned from the tarfile.

