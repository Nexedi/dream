========================
DREAM overview
========================

Scope
============

DREAM is an EU funded (FP7) project. Its main objective is to increase the competitiveness of the European Manufacturing Sector through targeting the advancement of discrete event simulation technology beyond the current state of the art to promote the embedding of simulation based decision support across the array of multi-level decisions faced by European Manufacturing Enterprises, from strategic (product/process development), tactical (ERP decision level support) and down to the MES level with the requirement of reactive real time decision support. More information can be found in http://dream-simulation.eu/.

What's included
=================

Within DREAM project 3 sub-projects are currently being developed. They are separate projects, but they also cooperate in the DREAM framework. A brief description of each one is given below. 

Currently in DREAM folder there are 4 sub-folders:
 + simulation: contains all ManPy simulation objects. 
 + KnowledgeExtraction: contains the KE tool code.	
 + platform: contains code related to the platform and the GUI.
 + tests: contains code for unit-testing.

How to get started
========================

To install DREAM along with its dependencies, the recommended way is to use `SlapOS <http://www.slapos.org/>`_ as described in the `DREAM Developer Tutorial <DREAM%20Platform%20Developer%20Tutorial.pdf>`_.

If you have the dependencies installed, you can use the setup.py in the root of the repository ( `python setup.py install` , `pip` or similar ).


Dependencies
=================

ManPy uses the following Python libraries:
 + `SimPy3 <http://simpy.readthedocs.org/en/latest/>`_
 + `NumPy <http://www.numpy.org/>`_
 + `xlrd <https://pypi.python.org/pypi/xlrd>`_
 + `xlwt <https://pypi.python.org/pypi/xlwt>`_

KE tool uses the following Python libraries:
 + `xlrd <https://pypi.python.org/pypi/xlrd>`_
 + `xlwt <https://pypi.python.org/pypi/xlwt>`_
 + `rpy2 <http://rpy.sourceforge.net/>`_
 + `R <http://www.r-project.org/>`_

The HTML5 graphical user interface uses the following javascript libraries:
 + `DHTMLX Gantt <http://dhtmlx.com/docs/products/dhtmlxGantt/>`_
 + `Flot <http://www.flotcharts.org/>`_
 + `Handsontable <http://handsontable.com/>`_
 + `jIO <http://j-io.org>`_
 + `JQuery <http://jquery.com/>`_
 + `JQuery Mobile <http://jquerymobile.com/>`_
 + `JSPlumb <http://jsplumbtoolkit.com/>`_
 + `RenderJS <http://www.renderjs.org/>`_
 + `RSVP.js <https://github.com/tildeio/rsvp.js>`_

Documentation
=================

Documentation for ManPy and KE tool can be found in the root directory of this repository.

Acknowledgements
=================

ManPy is product of a research project funded from the European Union Seventh Framework 
Programme (FP7-2012-NMP-ICT-FoF) under grant agreement n° 314364. The project name is 
DREAM and stands for "Simulation based application Decision support in Real-time for 
Efficient Agile Manufacturing". More information about the scope of DREAM can be found in 
http://dream-simulation.eu/. 

Copyright and license
==================================

DREAM modules are licensed under the GNU Lesser General Public License (LGPL).


Authors
==================================

Georgios Dagkakis

Jerome Perrin

Sebastien Robin

Kazuhiko Shiozaki

Ioannis Papagiannopoulos

Panos Barlas

Anna Rotondo

Dipo Olaitan

========================
ManPy 
========================

ManPy stands for "Manufacturing in Python" and it is a layer of Discrete Event Simulation 
(DES) objects built in Python. ManPy uses the `SimPy3 <http://simpy.readthedocs.org/en/latest/>`_ library in order to implement the process oriented world view.

The scope of the project is to provide simulation modellers with a collection of open-
source DES objects that can be connected like "black boxes" in order to form a model. 

This collection is desired to be expandable by giving means to developers for:  
 + customizing existing objects  
 + adding completely new objects to the list

Documentation for ManPy can be found in the root directory of this repository.

========================
KE tool 
========================

KE tool stands for "Knowledge Extraction" and is an IT solution built to link production data stored in different organization's IT-systems with the simulation software. The software built using `rpy2 <http://rpy.sourceforge.net/>`_ and other Python libraries.

The scope of the tool is the provision of functionalities that cover the "input data phase" in DES. These functionalities cover the four main components of the tool ('Data extraction', 'Data processing', 'Output preparation', 'Output analysis'), are offered as Python objects that can be connected line "black boxes" in order to form the KE tool main script.

The collection of the objects is desired to be expandable by giving means for developers for:
 + customizing existing objects  
 + developing new objects based on their needs.

Documentation for the KE tool can be found in the root directory of this repository.

========================
GUI editor
========================

The GUI editor has been developed with two ideas in mind: firstly it should help the user to develop a simulation model visually and it should also provide the user with straightforward and understandable results of simulation experiments that should help him understanding at a glance the output of the model by showing the results in formats such as bar charts, plots, Gantt diagrams or spreadsheets.

The GUI editor is designed based on the Javascript language so as to be supported by web browsers like Firefox, Chrome, Opera, Apple Safari, etc.