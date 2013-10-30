
========================
ManPy overview
========================

ManPy stands for "Manufacturing in Python" and it is a layer of Discrete Event Simulation 
(DES) objects built in SimPy (http://simpy.readthedocs.org/en/latest/). 

It is built within DREAM project (http://dream-simulation.eu/) 

Scope
============

The scope of the project is to provide simulation modellers with a collection of open-
source DES objects that can be connected like "black boxes" in order to form a model. This 

collection is desired to be expandable by giving means to developers for:  
 + customizing existing objects  
 + adding completely new objects to the list

What's included
=================

In the DREAM folder you can find three sub-folders:
 + simulation: contains all the simulation objects that are built in SimPy and also 2 python scripts to read inputs and run the simulation. Support documents and example inputs are provided in subfolders
 + platform: contains code related to the platform and the GUI that is also built and cooperates with the ManPy simulation engine
 + test: contains code fore unit-testing

Current Status
=================

DREAM is a project which kicked off in October of 2012 and finishes in September of 2015. 
ManPy is an ongoing project and we do not claim that it is complete. The platform will be 
expanded and validated through the industrial pilot cases of DREAM. Nevertheless, we 
launch the project in order to attract the interest of simulation modellers and software 
developers.  

Note that ManPy currently uses SimPy2 (http://simpy.sourceforge.net/old/). Soon it will be upgraded to the newest version SimPy3 (http://simpy.readthedocs.org/en/latest/).

How to get started
========================

To be able to run the documentation examples just copy the dream/simulation to your Python folder. Then you can import ManPy objects as it is written in the examples, e.g.:
 + *from simulation.Queue import Queue* or
 + *from simulation.imports import Machine, Source, Exit*

If you copy the whole dream folder, then the import should change to something like *from dream.simulation.Queue import Queue*. If you want to rename the folder it can be *from path.to.my.new.folder.Queue import Queue*.

Dependencies
=================

ManPy uses the following Python libraries:
 + SimPy2
 + NumPy
 + SciPy
 + xlrd
 + xlwt

=================
Documentation
=================

Documentation for ManPy. can be found in this repo in the root directory.   

=================
Acknowledgements
=================

ManPy is product of a research project funded from the European Union Seventh Framework 
Programme (FP7-2012-NMP-ICT-FoF) under grant agreement n° 314364. The project name is 
DREAM and stands for "Simulation based application Decision support in Real-time for 
Efficient Agile Manufacturing". More information about the scope of DREAM can be found in 
http://dream-simulation.eu/. 

==================================
Copyright and license
==================================

ManPy is licensed under the GNU Lesser General Public License (LGPL).

==================================
Authors
==================================

Georgios Dagkakis

Jerome Perrin

Sebastien Robin

Ioannis Papagiannopoulos