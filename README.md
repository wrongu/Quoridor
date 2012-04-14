Python Quoridor
===============

## Runnin' it

Just some code. no installation or anything.

The interface is TkBoard.py, so run with:

    python TkBoard.py
    -or-
    python TKBoard.py 2

Four player:

    python TkBoard.py 4

---

## Interface

The board itself and what I call the "panel" on the right should both be pretty self-explanatory..

**Controls**

* press M, or click 'move' button - make current move some movement
* press W, or click 'wall' button - make current move placing a wall
* press SPACE - toggle type of move
* Arrow Keys - move in that direction
* Click on board to move to a space or place a wall
* Escape - quit
* press U or click button to undo
* press R or click button to redo

---

## AI

So there's an AI. It is broken and very stupid. working on it.

    python TkBoard.py p a

where `p` is the total number of players (2 or 4) and `a` is the number of ai players. For example, 1-on-1 human vs ai is

    python TkBoard.py 2 1
    
Or, to watch 4 AIs play each other

    python TkBoard.py 4 4