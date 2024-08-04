#!/bin/bash

# Get the basic dependencies set up
sudo apt update
sudo apt upgrade -y
sudo apt install curl vim build-essential gnome-tweaks git -y

# Install Volta (volta.sh)
curl https://get.volta.sh | bash

# Install node using volta from the absolute path
$HOME/.volta/bin/volta install node@lts

# TMUX
sudo apt install tmux -y
touch $HOME/.tmux.conf

# Install tmux plugin manager
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# Configure the ~/.tmux.conf file.
echo "set -g @plugin 'tmux-plugins/tpm'" >> $HOME/.tmux.conf
echo "set -g @plugin 'tmux-plugins/tmux-sensible'" >> $HOME/.tmux.conf
echo "set -g @plugin 'catppuccin/tmux#latest'" >> $HOME/.tmux.conf
echo "" >> $HOME/.tmux.conf
echo "run '$HOME/.tmux/plugins/tpm/tpm'" >> $HOME/.tmux.conf
echo "" >> $HOME/.tmux.conf
echo "set -g @catppuccin_flavour 'mocha'" >> $HOME/.tmux.conf
echo "set -g mouse on" >> $HOME/.tmux.conf

# Fonts!
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/CascadiaCode.zip -O $HOME/CascadiaCode.zip
mkdir -p $HOME/post-install-temp
unzip $HOME/CascadiaCode.zip -d $HOME/post-install-temp

sudo mv $HOME/post-install-temp/*.ttf /usr/share/fonts
sudo fc-cache -f -v

# clean up the font installation files
rm $HOME/CascadiaCode.zip
rm -rf $HOME/post-install-temp


# Gnome Terminal Theme
curl -L https://raw.githubusercontent.com/catppuccin/gnome-terminal/v0.3.0/install.py | python3 -

echo "All done! You will now need to perform these manual steps to complete the installation:"
echo "1. Refresh shell environment: source ~/.bashrc." 
echo "2. For tmux, be sure to install the plugins in ~/.tmux.conf with prefix key + I and then run tmux source ~/.tmux.conf."
