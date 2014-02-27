CSC444 - Software Engineering I
======
##Billiard Ball Simulator
As part of the first lab, I designed a billiard ball simulator.  Given the dimensions of a billiard board and the position/velocities of N balls, the simulator brings up a GUI showing the resulting movements.  The GUI was written using the Tkinter library.  Collisions are assumed to be elastic, and there is a drag applied to each ball proportional to its velocity.  When all of the balls are stationary, the end state is written to an output file.

###Running

    ./billiard_simulation.py [file]

Refer to [system2.txt](hw1/test_inputs/system2.txt) for an example of the input file format


##Simple Version Control
As part of the second lab, Calvin Fernandes and I designed a revision control system in Python for storing text-based files.

###Supported Commands:
* status
* add
* edit
* commit
* sync
* log
* branch
* switchbranch
* suggest - Tries to apply last change of a file in one branch, to the file in another branch

###Running

    ./vc.py [command] [args]
