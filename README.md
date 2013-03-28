Project VPG
===========

Project VPG (Versatile Patroller Gelwoo) is a robot which can be programmed by
arranging tiles in meatspace. A camera then identifies the tiles and transmits
the information to the robot.

The Gelwoo itself is based on the SparkFun RedBot board and the Dagu Magician
Chassis. The controller is built on a pcDuino, running a Python 2.7 application
that uses simpleCV to recognize the tiles.

Communications between the Gelwoo and the CPU are via an XBee board.

Repository Contents
-------------------

* **/firmware** - Arduino code that runs on the RedBot driving the Gelwoo
* **/software** - Python code which runs on the pcDuino, controlling the Gelwoo
* **/hardware** - Documentation of the electronics involved in giving the 
    Gelwoo life.
* **/mechanical** - Drawings of parts fabricated for the project.

License Information
-------------------
The entire project (except where specified in individual files) is released 
under [Creative Commons Share-alike 3.0](http://creativecommons.org/licenses/by-sa/3.0/).  

<small><b>Where did the name come from, you weirdo?</b>  
The name came from [this giant robot name generator](http://www.rhetoricalramblings.com/robotname/index.html).
I find few things as tiresome as trying to name my new projects, so I asked
Google to give me a random name generator, and so was born Project VPG.</small>