# sesja-linuksowa-2016-rundeck

Materials used during presentation I gave on Sesja Linuksowa 2016 in Wrocław / Poland

Using those materials you can repeat all the activities I showed during my talk.

### Howto ###

1. Prepare Fedora-23 VM (or any other distro with systemd at least 222). We will call this **main_host**
    1. Export your SSH key to the root account on the main_host
    1. Make sure root can login via SSH on main_host
    1. Enter main_host IP addr into the ansible inventory in **inventory/hosts** as well as in **host_vars/main_host.yml**
    