# Smart Firewall

## Setup vagrant

We use vagrant to automate the installation of the whole project. 
Please refer to the official [documentation](https://www.vagrantup.com/downloads) to install it.
Note that the provider we used is libvirt, but it is possible to change it with the provider option. 
You may need to install the plugin for libvirt support. 
You should also be asked to provide root privileges in order to configure the shared folder.

```sh
vagrant plugin install vagrant-libvirt # If you use libvirt
vagrant up --no-parallel # Build the network
vagrant reload # Refresh the network configuration
```

Once the configuration is done, you can ssh through the VMs.

```sh
vagrant ssh firewall
vagrant ssh broker
vagrant ssh publisher
vagrant ssh subscriber
```

## Simulation

Start the firewall:

```sh
vagrant ssh firewall
cd /vagrant/src
sudo python main.py --input input.json
```

### MQTT

Start the mosquitto broker:

```sh
vagrant ssh broker
cd /vagrant/evaluation/devices/mqtt
mosquitto -v -c mosquitto.conf
```

Publish a message:

```sh
vagrant ssh publisher
mosquitto_pub -h 192.168.33.11 -t "th" -m "?temp=21&name=bob"
```
