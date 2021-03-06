#!/usr/bin/env python
__description__ = \
"""
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-01"
__usage__ = ""

import conway
import ledsart
from ledsart import sensors
from matplotlib import cm

# ----------- Set up the generator that will make pretty graphics ---------

# Define the class we'll use to generate the graphic (in this case, Conway's
# game of life).  This generator should have two public methods: .iterate() 
# (no arguments) and .as_rgba(kwargs).  
generator = conway.Conway

# Create a tuple of dictionaries holding information necessary to initialize a 
# new generator.  The installation will randomally select from these when it
# initializes a new generator, then pass them to the generator init function as
# **kwargs.
generator_configs = (
                     {"x_size":64,
                      "y_size":64,
                      "starting_density":0.4},
                     {"x_size":64,
                      "y_size":64,
                      "starting_density":0.5},
                     {"x_size":64,
                      "y_size":64,
                      "starting_density":0.6},
                    )

# Create a tuple of dictionaries holding information necessary to plot.  The 
# installation will randomly select from these when it initalizes a new 
# generator, then pass them to .as_rgba as **kwargs.
plot_configs = (
                {"cmap":cm.Greens,
                 "history_length":50,
                 "flip":True}, 
                {"cmap":cm.Oranges,
                 "history_length":50,
                 "flip":True}, 
                {"cmap":cm.copper,
                 "history_length":50,
                 "flip":True}, 
                {"cmap":cm.terrain,
                 "history_length":50,
                 "flip":False},
                {"cmap":cm.gnuplot,
                 "history_length":5,
                 "flip":False},
                {"cmap":cm.gray,
                 "history_length":1, 
                 "flip":False},
                {"cmap":cm.summer,
                 "history_length":50,
                 "flip":False},
                {"cmap":cm.ocean,
                 "history_length":50,
                 "flip":False},
               )

# ---------- Set up the display that will show the graphics ------------

# Create four panels
A = ledsart.Panel(32,32)
B = ledsart.Panel(32,32)
C = ledsart.Panel(32,32)
D = ledsart.Panel(32,32)

# Define the layout, connectivity, and relative rotation of the panels
layout = [[A,B],
          [C,D]]
chain = [A,B,D,C]
rotation = [0,0,180,180]

# Create a ledsart Display object that uses this layout.  This display has a 
# .draw method that takes the output of .as_rgba and maps it to the layout.
display = ledsart.Display(layout,chain,rotation,backend="rgbmatrix")


# ----------- Create the final ArtInstallation instance ---------------

installation = ledsart.ArtInstallation(conway.Conway,
                                       display,
                                       generator_configs=generator_configs,
                                       plot_configs=plot_configs,
                                       sampling_rate=0.01,
                                       iteration_interval=60,
                                       num_iterations=100)
        
# ----------- Set up range finder and append to installation ---------------
# This causes a range finder attached at PIN1 (trigger) and PIN2 (read) to
# attenuate iteration_interval between 0 and 300 s.  At 1.0 m, the interval
# will be 150 s.  At 0.0 m, the interval will be 0 s. 
s = sensors.Sensor(sensors.UltrasonicRange(5,3,timeout=100), #sensor
                   "iteration_interval", # property to modify
                    half_value=1.0,       # distance that gives 1/2 iteration_interval
                    max_value=60,         # max iteration_interval
                    steepness=4.0)        # steepness of curve (< 1 shallow, > 1 steeper)

installation.add_sensor(s)
b = sensors.Sensor(sensors.Button(8),
                   "choose_new_plot")
installation.add_sensor(b)

# ----------- Main loop ----------------
# Run until ctrl+c is pressed.
try:
    installation.run()
except KeyboardInterrupt:
    pass


