# Smart firewall for IoT and Smart Home applications

## Experimental setup

We use vagrant with the libvirt provider to automate the installation of the whole project. 
Please refer to the official [documentation](https://www.vagrantup.com/downloads) to install it.
It is possible to use virtualbox, but this will require to allow the range of IPs we used or to change the IPs in the Vagrantfile and in the input file directly. 
The Vagrantfile is designed to work with Linux distributions, it is possible to make it work on other operating systems but it requires changing the settings of the shared folder.
You should also be asked to provide root privileges in order to configure the shared folder.

```sh
vagrant plugin install vagrant-libvirt # If you use libvirt
vagrant up --no-parallel # Build the network, this will ask you root privileges
vagrant reload # Refresh the network configuration
```

The reload step is only necessary at the first startup because the configuration files must be updated.

Once the configuration is done, you can ssh through the VMs.

```sh
vagrant ssh firewall
vagrant ssh broker
vagrant ssh publisher
vagrant ssh subscriber
```

## Input file

The input file should be placed in /vagrant/src, and 
you should refer to the manuscript for documentation on its design.
Note that you can also generate inputs with the generator in /evaluation/generator.

We provide an example of input in input.json. 
This file contains a basic configuration with four members: broker, thermo, heater and window. 

The thermo has a decimal field to keep track of the temperature, it is attached to a categorization that defines cold below 10, average between 10 and 20 and hot above 20. 
Both the window and the heater have a single status field with two values: on and off.

Then we define two relations: trigger_heater and trigger_window. The first one only allow
thermo to send cold and hot temperatures to the heater. The second one does the same thing but with
the window. 

Next, we define two dummy triggers, one that disables the trigger_heater
relationship if a hot temperature is observed and another one that deactivates the trigger_window relationship at night and 
between 18:00 and 19:00. The night corresponds to a categorization that matches the time between
23:00 and 06:00.

Finally, we define a simple inference that says that the window should be closed if the temperature is cold,
but also an inconsistency ensuring the heating to be turned off when the
temperature is hot.

## Simulation

Start the firewall in dev mode:

```sh
vagrant ssh firewall
cd /vagrant/src
sudo python main.py --input input.json
```

For production mode (default policy drop):

```sh
sudo python main.py --input input.json --no-dev
```

The firewall can be stopped with a SIGINT (ctrl+c). It also prints some logs, for example when
a packet that has reached the constraint mapping is accepted or dropped. Prints are also made 
to trigger alarms.

### MQTT

Start the mosquitto broker:

```sh
vagrant ssh broker
cd /vagrant/evaluation/mqtt
mosquitto -v -c mosquitto.conf
```

Publish a message:

```sh
vagrant ssh publisher
mosquitto_pub -h 192.168.33.11 -t "th" -m "?temp=21&name=bob"
```

You can also use the publisher.py and subscriber.py scripts that we used for the evaluation.

### CoAP

You can use the client.py and server.py scripts such as in the evaluation. 


