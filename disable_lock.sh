#!/bin/bash

# Disable screen lock and screensaver
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.settings-daemon.plugins.power idle-dim false

# Disable auto-suspend
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing'

# Disable lock on suspend
gsettings set org.gnome.desktop.screensaver ubuntu-lock-on-suspend false

# Disable automatic updates
sudo systemctl disable apt-daily.service
sudo systemctl disable apt-daily.timer
sudo systemctl disable apt-daily-upgrade.timer
sudo systemctl disable apt-daily-upgrade.service

# Create autostart entry to disable lock on login
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/disable-lock.desktop << EOL
[Desktop Entry]
Type=Application
Name=Disable Lock
Exec=bash -c "gsettings set org.gnome.desktop.screensaver lock-enabled false; gsettings set org.gnome.desktop.screensaver idle-activation-enabled false; gsettings set org.gnome.desktop.session idle-delay 0"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOL

# Disable lock screen in lightdm
sudo mkdir -p /etc/lightdm/lightdm.conf.d/
sudo tee /etc/lightdm/lightdm.conf.d/10-disable-lock.conf << EOL
[SeatDefaults]
greeter-hide-users=false
greeter-show-manual-login=true
allow-guest=false
EOL

# Disable power management in XRDP
echo "mate-power-manager --no-daemon" >> ~/.xsessionrc

# Set power button action to nothing
gsettings set org.gnome.settings-daemon.plugins.power power-button-action 'nothing'

# Disable automatic logout
gsettings set org.gnome.desktop.session idle-delay 0

echo "All auto-lock features have been disabled!"
echo "Please restart your session for changes to take effect."
