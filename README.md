#led-art-installation

Classes for controlling a raspberry-pi based art installation based on LED panels.

## Example 
```
# Configure environment
sudo apt-get install python-numpy python-scipy python-matplotlib python-imaging

# Make directory for panel art
mkdir ledpanelart
cd ledpanelart

# Bring in art installation library
git clone https://github.com/harmsm/ledsart.git
cd ledsart
sudo python setup.py install
cd ../

# Bring in conway's game of life
git clone https://github.com/harmsm/conway.git
cd conway
sudo python setup.py install
cd ../

# Bring in panel control library
git clone  https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make
cd python
sudo python setup.py install
cd ../../

# Copy example art script into the current directory
cp ledsart/example/run_art.py .
```

+ comment out snd-bcm2835 in /etc/modules
+ modify run_art.py to fit hardware
+ add the following to `/etc/rc.local`: `python /home/pi/ledpanelart/run_art.py &`

