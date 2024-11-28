# Peer-to-peer file sharing

This is instruction to use this file. Please read carefully and follow if you want to use.

_This project is for the first assignment of Computer Network course CO3093. If you want to use this project, please contact me via Github._

## 0. Description
This project is a peer-to-peer file sharing program, written in Python. This project using static IP method and socket connection to implement, with the main idea is based on torrent.
This project consists of this instruction file and 2 folders: Client and Tracker.

## 1. Tracker
Tracker acts as a server for holding magnetinfo and list of seeders of files. Tracker **MUST** run and hold in a terminal before you can do anything else. But before run Tracker, you **MUST** do little things.

### 1.1. Setting up static IP
**Windows**
- Open cmd, type `ipconfig`
- Note your network information
- Open Settings.
- Navigate to: Network & Internet > Status > Change adapter options (in the Advanced Network Settings section).
- Right-click on your network adapter (e.g., Ethernet or Wi-Fi) and choose Properties.
- Select Internet Protocol Version 4 (TCP/IPv4) and click Properties.
- The IPv4 address will have the format: aaa.bbb.ccc.ddd
- Choose Use the following IP address and enter:
  + IP address: aaa.bbb.1.100 (based on your IPv4 address)
  + Subnet mask: Based on your subnet mask
  + Default gateway: Based on your default gateway
- Set DNS servers:
  + Preferred: 8.8.8.8
  + Alternate: 8.8.4.4
- Click OK and close.

**Linux**
- Open a terminal.
- Edit your network configuration file. Depending on the distribution:
  + Ubuntu/Debian: `/etc/netplan/*.yaml (newer versions) or /etc/network/interfaces (older versions).`
  + Red Hat/CentOS: `/etc/sysconfig/network-scripts/ifcfg-<interface>.`

  Example for a Netplan YAML configuration:
  ```yaml
  network:
    version: 2
    renderer: networkd
    ethernets:
      eth0:
        dhcp4: no
        addresses: [192.168.1.100/24]
        gateway4: 192.168.1.1
        nameservers:
          addresses: [8.8.8.8, 8.8.4.4]
  ```
- Apply changes:
```bash
sudo netplan apply
```
- Verify:
```
ip addr
```
### 1.2. Run Tracker
