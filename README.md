# PCCT
The source code of the point cloud classification tool (PCCT) will soon be published. This source code was created as
part of my dissertation at HafenCity University Hamburg. The collection of scripts is used to examine to investigate the 
properties of different manual and semi-automatic classification tools. The approach used in this tool is based on 
projecting the point cloud with all features into 2D space (into an image). Different methods such as panoramic 
projection, vertical, horizontal slices or prior knowledge based segmentations can be selected. In addition, the 
segment in the image space are formed based on different features (e.g. RGB or I-values) (Module 1). The classification 
is done via a web interface (module 2), where human users assign the previously automatically formed segments to a 
class. The classifications are then combined with the point clouds to create a semantic point cloud (module 3). For the 
uses of the PCCT, a database (I have MariaDB) and a (web) server are necessary. 

![Alt text](Motivation.png?raw=true "Concept and Motivation")

In Modul 1 the point cloud is given in to database and the automatisch image-based segmentation is preformed. Use the
script: 

    gui.py 

to open the user interface. To learn more about the parameter see the technical paper [1].

The second modul runs on the webserver (Preferably there is also the database). Execute: 

    WebtoolID.py

The results of the classification need to be combined with the 3D point cloud. To do so you can run:   
    
    M3_Evaluation.py

An userinterface will open, and you can select the database and the point cloud (scan) of interest. All results will
export as csv or pts.

### Installation

You also need to install tkinter, glob, matplotlib, pandas, numpy, time, math, random, PIL, pyntcloud, cherrypy, 
sqlalchemy, os.path, pymysql. The code has been tested with Python 3.8.3 on Windows10. 

Use your favourite terminal and install packages for Python:
```bash
 pip3 install *package*
```

### Citation
If you find our work useful in your research, please consider citing:

Technical detail about the tool:

[1]
  ```
  @InProceedings{barnefske19,
   author    = {Barnefske, Eike and Sternberg, Harald},
   title     = {{Generation of Training Data for {3D} Point Cloud Classification by {CNN}}},
   booktitle = {Proceedings of 80th FIG Working Week 2019, April 22-26, Vietnam.}
  }
  ```
The paper on the code was presented at the 80th FIG Working Week in Hanoi (22. -26. April 2019) and can be found
at http://www.fig.net/resources/proceedings/fig_proceedings/fig2019/papers/ts02c/TS02C_barnefske_sternberg_9881.pdf.

General idea and results of investigation:

[2]
   ```
	@PhdThesis{Barnefske2023,
	  title={Automated segmentation and classification with artificial neural networks of objects in 3D point clouds},
	  author={Barnefske,Eike},
      date        = {2023},
      institution = {HafenCity University Hamburg}, 
      type        = {phdthesis},
    }
   ```
### License
The code is released under MIT License (see LICENSE file for details), unless other restrictions prohibit it.

