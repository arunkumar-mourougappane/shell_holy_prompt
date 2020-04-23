#!/bin/bash

set -e

echo "Setting up apps for terminal"
sudo apt install git gitg

echo "Forcing Color prompt"
sed -i 's/#force_color_prompt=yes/force_color_prompt=yes/g' /home/${USER}/.bashrc

echo "Making prompt change a part of bash_aliases ..."
cat bashrc_prompt >> /home/${USER}/.bash_aliases

echo "Adding config files ..."
cp  bashrc_sshagent /home/${USER}/.bashrc_sshagent
cp  bashrc_gitcolor /home/${USER}/.bashrc_gitcolor

echo "Settting up permissions ..."
chmod +x /home/${USER}/.bashrc_*
