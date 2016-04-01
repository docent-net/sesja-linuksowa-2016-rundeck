# sesja-linuksowa-2016-rundeck

Materials used during presentation I gave on Sesja Linuksowa 2016 in Wrocław / Poland

Using those materials you can repeat all the activities I showed during my talk.

### Howto ###

All following jobs are meant to be run with SELinux enabled in enforcing mode.

1. Prepare Fedora-23 VM (or any other distro with systemd at least 222). We will call this **main_host**
  * Export your SSH key to the root account on the main_host
  * Make sure root can login via SSH on main_host
  * Enter main_host IP addr into the ansible inventory in **inventory/hosts** as well as in **host_vars/main_host.yml**
  * Prepare basic environment on main_host: `ansible-playbook -i inventory/hosts plays/prepare_env.yml` 
  * Prepare systemd-networkd based bridged networking for containers on main_host: `ansible-playbook -i inventory/hosts plays/prepare_networking.yml`
1. Prepare systemd-nspawn containers on which we will deploy lab applications:
  * Prepare systemd-nspawn container template: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn-template.yml`
  * Prepare systemd-nspawn environment on main_host: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn.yml`
  * Spawn systemd-nspawn containers: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn-containers.yml `
  * Prepare basic environment on containers: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn-containers_env.yml`