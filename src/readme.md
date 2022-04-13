# Setup a venv (optional)

```sh
pip install virtualenv 
cd my_project_folder # optional 
virtualenv venv # creates the venv 
source venv/bin/activate # activate the venv
deactivate # deactivate the venv
```

Now each package will be installed inside the venv and the interpreter will use it.

# Install the requirements

```sh
pip install -r requirements.txt
sudo dnf install python3-nftables
sudo pip3 install jsonschema
```

# Start the name server

```sh
python -m Pyro4.naming
```

This should be done in another terminal. Now you can start the daemon, The client will communicate with it.

```sh
python old_main.py
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

python client.py relation --broker 192.168.33.11 --pub 192.168.33.12 --sub 192.168.33.13  --subject test --constraint time/20:00-22:00 --constraint str/name/bob/alice --constraint int/temp/5/5-10/20-25

# Show the rules

python client.py show
```

# Mosquitto pub

```sh
mosquitto_pub -h 192.168.33.11 -t "test" -m "?temp=21&name=bob"
```

# Nftables commands

```sh
sudo nft add table ip filter # create a table of type ip and name filter (automatically created by the iptables command)

sudo nft 'add chain ip filter input { type filter hook input priority 0 ; }' # create an input chain in the table of type ip and name filter

sudo nft list tables # show name and type of all tables

sudo nft list table filter # show all the chains and rules inside the table filter

sudo nft add rule filter INPUT tcp dport 22 mark set 82 # add a marker integer 82 to all packet with destination port 22, in the chain INPUT in the table filter

sudo nft add rule filter OUTPUT tcp sport 22 mark set 82 # add a marker integer 82 to all packet with source port 22, in the chain OUTPUT in the table filter

sudo nft add rule filter OUTPUT tcp sport 22 counter mark set 82 # same command than previous one but has a counter to check how many packets matched, useful to debug rules

sudo nft -n -a list ruleset # to list all rules with their handle (index)

sudo nft delete rule filter OUTPUT handle 11 # delete rule of handle (index) 11 in the chain OUTPUT in the table filter

sudo nft flush ruleset # remove all rules, chains and tables
```

