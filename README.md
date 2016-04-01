# sesja-linuksowa-2016-rundeck

Materials used during presentation I gave on Sesja Linuksowa 2016 in Wrocław / Poland

Using those materials you can repeat all the activities I showed during my talk.

### Howto ###

All following jobs are meant to be run with SELinux enabled in enforcing mode.

In the following manual **main_host** refers to the VM on which we install our test - lab (nspawn containers with applications)
By **control_host** we assume host from which we run ansible-playbooks (probably your desktop).

1. Prepare Fedora-23 VM (or any other distro with systemd at least 222; on Fedora make sure you have python2, python2-dnf, libselinux-python packages installed) on your **control_host**. We will call this provisioned VM a **main_host**
  * Export your SSH pubkey from **control_host** to the root account on the **main_host**
  * Make sure you can login from your **control_host** via ssh into root account on **main_host**
  * cwd this repo directory on **control_host**
  * add/export your SSH pubkey to the file **plays/files/ssh_keys/authorized_keys**: `cat ~/.ssh/id_rsa.pub >> plays/files/ssh_keys/authorized_keys`
  * Enter **main_host**'s' IP addr into the ansible inventory in **inventory/hosts** as well as in **host_vars/main_host.yml**
  * Prepare basic environment on main_host: `ansible-playbook -i inventory/hosts plays/prepare_env.yml`
  * Prepare systemd-networkd based bridged networking for containers on main_host: `ansible-playbook -i inventory/hosts plays/prepare_networking.yml`
1. Prepare systemd-nspawn containers on which we will deploy lab applications:
  * Prepare systemd-nspawn container template: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn-template.yml`
  * Prepare systemd-nspawn environment on main_host: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn.yml`
  * Spawn systemd-nspawn containers: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn-containers.yml `
  * On your **control_host** prepare file **~/.config/vault_sesja.pwd** and make it contain only string: **sesja_haslo_vault**: `echo "sesja_haslo_vault" > ~/.config/vault_sesja.pwd`
  * Prepare basic environment on containers: `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn-containers_env.yml --vault-password-file ~/.config/vault_sesja.pwd --tags env``
1. Deploy rundeck app:
  * `ansible-playbook -i inventory/hosts plays/prepare_systemd-nspawn-containers_env.yml --vault-password-file ~/.config/vault_sesja.pwd --tags rundeck`
