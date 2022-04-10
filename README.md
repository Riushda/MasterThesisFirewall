# MasterThesisFirewall

## Setup vagrant 

We use vagrant to automate the installation of the whole project. Please refer to the official [documentation] (https://www.vagrantup.com/downloads) to install it.
Once installed, you can build the network. Please note that the provider we used is libvirt but it is possible to change it by editing the Vagrantfile. You
may need to install the plugin for libvirt support. You should also be asked to provide root privileges in order to configure the shared folder.

```sh
vagrant plugin install vagrant-libvirt # This is done locally in the Vagrantfile, but may not work.
vagrant up
```

Once the configuration is done, you can ssh through the VMs.

```sh
vagrant ssh firewall # To start the firewall.
```

