
Download the application
------------------------------------------
  
* Clone or download the repository. The updated code is in the develop branch.

.. code-block:: bash

    gridappsd@gridappsd-VirtualBox:~$ git clone https://github.com/therahuljha/WSU-VVO-app -b develop
    gridappsd@gridappsd-VirtualBox:~$ cd WSU-VVO-app

..

Creating the application container
------------------------------------------

* From the command line execute the following commands to build the wsu-vvo container

.. code-block:: bash

     gridappsd@gridappsd-VirtualBox:~/WSU-VVO-app$ docker build --network=host -t wsu-vvo .
..



Mount the application
-----------------------------------

* Add following to the docker-compose.yml file. 

.. code-block:: bash

    WSU-VVO-app:
    image: wsu-vvo
    volumes:
      - /opt/ibm/ILOG/CPLEX_Studio129/:/opt/ibm/ILOG/CPLEX_Studio129
    environment:
      GRIDAPPSD_URI: tcp://gridappsd:61613
    depends_on:
      - gridappsd 
      
..
