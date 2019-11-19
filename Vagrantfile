# -*- mode: ruby -*-
# vi: set ft=ruby :

SUPPORT_DATABASE_PASSWORD = ENV['SUPPORT_DATABASE_PASSWORD']

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.box_check_update = true

  config.vm.synced_folder "www/", "/srv/www", create: true

  config.ssh.forward_agent = true

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end

  config.vm.provision "file", source: "./.bash_local", destination: "~/.bash_local"
  config.vm.provision :shell, path: "vagrant_setup.sh", env: {"SUPPORT_DATABASE_PASSWORD": SUPPORT_DATABASE_PASSWORD}, privileged: false

end
