# Stampobot - a robotic arm that creates digital stamp collections.

## Overview

With this project I created a machine, that can produce digital stamp collections. Multiple machine learning models have
been built to analyze the pictures of stamps. The tasks of the various models are:

- detecting single laying stamps in a box of many stamps
- analyzing pictured stamp if single or multiple
- crop stamp
- detecting text on stamp
- align on virtual collection space

This process is iterated by communicating between Arduino and PC via USB serial communication. The Arduino is programmed
separately to control all the motors/electronics that are used in this project. 

The following is used and controlled by Arduino:

- uArm Swift Pro robotic arm
- own designed vacuum pump system, including 1 pump, 1 valve as well as two SSR relays
- 1 linear motor that moves the stamps from the picture area into a box
- 1 linear motor that moves boxes once a collection is finished
- 1 stepper motor that flattens the pictured stamp in order to increase picture quality
- 3 stepper motor drivers

## Structure

- arduino

    The Arduino code for communication between PC and Arduino

- src

    The main source code for detecting stamps and communication with Arduino
    
- utils

    * The deep learning model for stamp detection
    * The source code for management of files and folders

- app

    The main execution file
    
- requirements

    All the dependencies for this project
    
- settings

    Several settings

- user_config

    Some configurations of user input for image processing like contrast, brightness, sharpness, gamma, white balance etc.
 
## Installation

Please note, that I do not make the deep learning models public but they are necessary to run the project. 
If you would like to use them please send me a request at robert.kloepsch@gmail.com.

- Environment

    Ubuntu 18.04, Windows 10(Recommended), Python 3.6

- Dependency Installation

    Please navigate to this project directory and run the following command in the terminal.
    * Ubuntu 18.04
    ```
        sudo apt-get install libsdl2-dev libsdl2-ttf-dev libsdl2-image-dev libsdl2-mixer-dev
        sudo apt-get install xclip
        pip3 install -r requirements.txt
    ```
    * Windows
    ```
        python3 -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew --extra-index-url https://kivy.org/downloads/packages/simple/
        pip3 install -r requirements.txt
    ```

- Please create "model" folder in the "utils" folder and copy the 3 deep learning models into the "model" folder.

- Please create "credential" folder in the "utils" folder and copy the vision_key.txt file into the "credential" folder.

## Execution

- Configuration (in user_config file)

    * arduino_port: the port connected with Arduino.
    * gamma: float value for gamma of image processing 
    * brightness: int value between -255 and 255 for brightness
    * contrast: int value between -127 and 127 for contrast
    * sharpness: bool value with true and false for sharpness
    * white_balance: bool value with true and false for white balance
    * collection_number: int value of collection number
    * top_cam: int value of top camera number
    * bottom_cam: int value of bottom camera number
    * stamp_detector_cam: int value of stamp detector camera number

- In the case of Ubuntu OS, please run the following command in the terminal.

    ```
        sudo chmod 666 {ARDUINO_PORT} # like /dev/ttyUSB0
    ```

- Please run the following command in the terminal.

    ```
        python3 app.py
    ```

## Note

- Please refer arduino/coordinate_sender.ino file for communication between Arduino and PC.

- Communication between PC and Arduino

    1. Arduino -> PC: "detect": PC detects the stamp
    2. Once PC detects the stamp: PC -> Arduino: coordinate with x, y like "x,y"
    3. Robot moves the stamp, Arduino -> PC: "moved", PC takes the photos of top and bottom
    4. If multi stamps or not any stamp, PC -> Arduino: "retry"
    5. If single, after estimation of the front side and rotation, PC aligns the stamp.
    6. If alignment is not complete, PC -> Arduino: "retry"
    7. If alignment is complete, PC -> Arduino: "complete"
