#!/bin/bash

# Get the basic dependencies set up
sudo apt update
sudo apt upgrade -y
sudo apt install curl vim build-essential gnome-tweaks git -y

# Install Volta (volta.sh)
curl https://get.volta.sh | bash

# Install node using volta from the absolute path
$HOME/.volta/bin/volta install node@lts

echo "All done! You should run this command to finish up: source ~/.bashrc"
