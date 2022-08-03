# TWavString

## What is `TWavString`?

* TWavString is an audio-to-binary converter.

## How to use `TWavString`?

### called from the command prompt

* You can run the command 'python TWavString. exe <PATH_TO_FILE>'
* Two arguments in the command: `-e` enables forced encoding and `-d` enables forced decoding

### Drag the file OR directly open

* You can drag files to TWavString.exe
* You can directly open the executable file, enter the command line mode and enter the specified path to convert the file

## What is the principle of `TWavString`?

* Technology basement: the lossless inclusion and access to written bytes data (rawData) in WAV

### Library implementation: PyDub

* Read implementation: raw_data property of the AudioSegment class
* Write implementation: data argument in the constructor of the AudioSegment class

### Default audio technical parameters

* Frame rate: 44100 Hz
* Sample width: 2
* Channels: 2

### Important technical obstacles

* "completion problem" caused by "byte units" in data (the length of the data can only be an integer multiple of the length of the data unit)

## Does `TWavString` have an open source license?

* `TWavString` is now used ***MIT License***(See LICENCE)
