#!/bin/bash

# Install required packages
sudo apt-get update
sudo apt-get install -y dconf-editor gnome-tweaks

# Open Settings GUI
echo "Please follow these steps to disable lock screen using GUI:"
echo "1. Open Settings"
echo "2. Go to Privacy"
echo "3. Set Screen Lock to OFF"
echo "4. Go to Power"
echo "5. Set Blank Screen to Never"
echo "6. Set Automatic Suspend to OFF"

# Launch settings
gnome-control-center &

# Launch Tweaks
gnome-tweaks &

echo "Settings and Tweaks applications have been launched."
echo "Disable these additional settings in Tweaks:"
echo "1. Go to General"
echo "2. Turn off 'Suspend when laptop lid is closed'"
echo "3. Go to Power"
echo "4. Turn off all power saving options"
