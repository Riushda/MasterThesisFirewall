# Setup a venv (optional)

```sh
pip install virtualenv cd my_project_folder # optional 
virtualenv venv # creates the venv 
source venv/bin/activate # activate the venv
deactivate # deactivate the venv
```

Now each package will be installed inside the venv and the interpreter will use it.

# Install the requirements

```sh
pip install -r requirements.txt
```

# Start the name server

```sh
python -m Pyro4.naming
```

This should be done in another terminal. Now you can start the daemon, The client will communicate with it.

```sh
python daemon.py
python client.py {COMMAND}
```

# Command examples

Use --help to see all the possibilities

```sh
# Add members

python client.py member --name A --type pub

python client.py member --name B --type sub

python client.py member --name C --type broker

# Add relations

python client.py relation --pub A --sub B --broker C

python client.py relation --pub A --sub B --broker C --constraint subject/allo --constraint time/20:00-22:00 --constraint str/name/bob/alice

python client.py relation --pub 192.168.1.1/24 --sub 192.168.1.1/24 --broker 192.168.1.1/24 --constraint subject/allo --constraint time/20:00-22:00 --constraint str/name/bob/alice

# Show the rules

python client.py show
```

