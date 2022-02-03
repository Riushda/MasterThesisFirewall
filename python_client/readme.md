# Setup a venv (optional)

pip install virtualenv 
cd my_project_folder # optional
virtualenv venv # creates the venv
source venv/bin/activate # activate

Now each package will be installed inside the venv and the interpreter will use it

deactivate # deactivate

# Install the requirements

pip install -r requirements.txt

# Start the name server

python -m Pyro4.naming

This should be done in a separated terminal

Now you can start the daemon 

python daemon.py

The client will communicate with it

python client.py {COMMAND}

# Command examples

python client.py member A --type pub
python client.py member B --type sub
python client.py member C --type broker

python client.py relation / A B --broker C

python client.py show

Use --help to see all the possibilites, also old commands are available

python client.py rule --src 192.168.1.1/24 --sport 22 --dst 192.168.1.2/24 --dport 22