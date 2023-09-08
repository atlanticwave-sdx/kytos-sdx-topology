#!/bin/sh
sudo rm -r /kytos
sudo rm -r /var/lib/kytos
sudo rm -r /var/run/kytos
sudo rm -r /var/tmp/kytos
sudo rm -r /etc/kytos
sudo mkdir /kytos
sudo mkdir /var/lib/kytos
sudo mkdir /var/run/kytos
sudo mkdir /var/tmp/kytos
sudo mkdir /etc/kytos
sudo chown -R admin:admin /kytos
sudo chown -R admin:admin /var/lib/kytos
sudo chown -R admin:admin /var/run/kytos
sudo chown -R admin:admin /var/tmp/kytos
sudo chown -R admin:admin /etc/kytos
cp ./2_venvinstall.sh /kytos/2_venvinstall.sh
cp ./3_pipinstall.sh /kytos/3_pipinstall.sh
cp ./4_clone_kytos.sh /kytos/.
cp ./5_install_kytos.sh /kytos/.
cp ./docker-compose.yml /kytos/.
cp ./env /kytos/.env
cd /kytos
