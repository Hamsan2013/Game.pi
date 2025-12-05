#!/bin/bash
set -e
echo "Installing RasPi Game Caster..."
sudo apt update
sudo apt install -y python3 python3-pip adb scrcpy
sudo mkdir -p /opt/raspi-game-caster
sudo cp -r * /opt/raspi-game-caster/
sudo pip3 install -r /opt/raspi-game-caster/requirements.txt
cat <<EOF | sudo tee /usr/share/applications/raspi-game-caster.desktop
[Desktop Entry]
Name=RasPi Game Caster
Exec=python3 /opt/raspi-game-caster/app.py
Type=Application
Terminal=false
Categories=Game;
EOF
echo "Installation complete. Run the app from the menu or with: python3 /opt/raspi-game-caster/app.py"
