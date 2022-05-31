boxes = [
    {
        :name => "broker",
        :eth1 => "192.168.33.11"
    },
    {
        :name => "publisher",
        :eth1 => "192.168.33.12"
    },
    {
        :name => "subscriber",
        :eth1 => "192.168.33.13"
    }
]

Vagrant.configure("2") do |config|
  providers = ["libvirt", "virtualbox"]
  config.vm.synced_folder ".", "/vagrant", type: "nfs"

  config.vm.define "firewall" do |firewall|
  
    firewall.vm.provision :shell, path: "./bootstrap/firewall_bootstrap.sh"
    firewall.vm.box = "fedora/35-cloud-base"
    firewall.vm.hostname = "firewall"
    firewall.vm.network "private_network", ip: "192.168.33.10"

    providers.each do |p|
        firewall.vm.provider p do |firewall|
          firewall.cpus = 2
          firewall.memory = 2048
        end
    end

  end
  
  boxes.reverse_each do |opts|
        config.vm.define opts[:name] do |config|
            
            config.vm.provision :shell, path: "./bootstrap/device_bootstrap.sh"
            config.vm.box = "fedora/35-cloud-base"
            config.vm.hostname = opts[:name]
            config.vm.network :private_network, ip: opts[:eth1]

             providers.each do |p|
                 config.vm.provider p do |vb|
                    vb.cpus = 1
                    vb.memory = 1024
                 end
             end
        end
  end

end
