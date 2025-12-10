# SWoS-DSC
Mikrotik SWos Desired SWoS Config

My first attempt to create a Desired SWoS Config.

In the future I will write a program to push a config to a swos switch (config2swos.py).
Also a command to read the swos config, and create a config file (swos2config.py). This should also be possible from RouterOS (routeros2config.py).

Secondly, in order to better understand the SWoS API, I made a program to read all info, and put this in a json file. Those files can be collected, and be compiled to a sheet, so you can easily compare the
differences between the SWoS devices.
The compiled sheet is available in html and markdown.

To develop the swos-api better and faster, I made a sampler program, to save the web interface to a file. This file can then be loaded in an emulator, and be used to develop the library at other places and times.
