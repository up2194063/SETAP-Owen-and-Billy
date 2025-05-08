Installation
============

When using the HouseShare Assistant web application for the first time, make sure that the repository is downloaded locally from GitHub and that your terminal is connected to the
local clone of the repository.

For example:

.. code-block:: posh

    PS C:\users\my_user\repository_name

Before you are able to use the web app, a few more steps are required. The first step is to pip install Flask, which can be achieved by typing the following code into the terminal:

.. code-block:: posh

    PS C:\users\my_user\repository_name> pip install Flask

The final step before being able to open the web app is the initialisation of the databse, which can be achieved by typing the following code into the terminal:

.. code-block:: posh

    PS C:\users\my_user\repository_name> python -m flask --app hsa_b init-db

.. note::

    The initialisation of the database must only be completed for the initial setup of the app, as re-initialising the database will erase all existing data

After completing all of the steps above, the following code must be run in the terminal for the app to run:

.. code-block:: posh

    PS C:\users\my_user\repository_name> python -m flask --app hsa_b run --debug

When the above code is run, this will host the web app on a server which can be seen in the terminal:

.. code-block:: posh

    PS C:\users\my_user\repository_name> python -m flask --app hsa_b run --debug
     * Serving Flask app 'hsa'
     * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5000
    Press CTRL+C to quit
    * Restarting with stat
    * Debugger is active!
    * Debugger PIN: ***-***-***

To open the web app, the address which includes the server must be pasted into a web browser which will open the HouseShare Assistant web application