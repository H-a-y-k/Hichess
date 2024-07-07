# HiChess

Hichess is a cross platform chess desktop app based on PySide2 and [hichesslib](https://github.com/H-a-y-k/hichesslib). It has
 - PVE against manually linked chess engine
 - PVP
 - multiplayer on local network with an integrated chat
 - other small features that make the gameplay comfortable.

This is only a fun project, with the purpose of illustrating hichesslib in action. 

![image](https://github.com/H-a-y-k/Hichess/assets/52096477/e1b0a42c-b5c4-410e-abc0-3a0e49870738)

### Dependencies
 - hichesslib
   + `pip install hichesslib`
 - python-chess
   + `pip install python-chess`
 - numpy
   + `pip install numpy`
     
### How to run
```
git clone https://github.com/H-a-y-k/Hichess
cd Hichess
python src/main.py
```

### How to link an engine
 - Install an engine such as Stockfish
 - Insert the path to the engine in the start dialog of Hichess.

### Tests
- This project does not contain integrated unit tests. The main API it is based on is hichesslib, which is thoroughly tested.

### License
 - GNU v3.0

There is no need to contribute to this project, but contributions to hichesslib are welcome.
