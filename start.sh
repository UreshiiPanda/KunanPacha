#!/bin/bash


# make sure Docker is running
if ! docker info > /dev/null 2>&1;
then
    open -a Docker
    echo opening Docker
    sleep 4
    # close the Docker window
    osascript -e 'tell application "System Events" to keystroke "w" using command down'
else
    echo Docker already running
fi


# Check if Kitty is running (this script may be run from a workflow)
if ! pgrep -q "kitty";
then
    # if Kitty is not running
    # switch to Desktop 1
    osascript -e 'tell application "System Events" to key code 18 using {control down, shift down, option down, command down}'
    # open Kitty
    open -a Kitty
    # wait for Kitty to fully open
    sleep 1
    echo opening kitty nya
else
    # if Kitty is running, then it should be running in Desktop 3
    # switch to Desktop 1
    osascript -e 'tell application "System Events" to key code 18 using {control down, shift down, option down, command down}'
    echo kitty already open nya
    sleep 1
fi


# name window1 to nya1
kitten @ set-window-title nya1

# open a new Kitty window
kitten @ launch --title=nya2
sleep 1

# open second kitty tab for watchers
kitten @ launch --type=tab --title=nya3
sleep 1

# open 2 more windows in that tab
kitten @ send-text --match=title:nya3 kitten @ launch --title=nya4'\n'
sleep 1
kitten @ send-text --match=title:nya3 kitten @ launch --title=nya5'\n'
sleep 1

# choose color in second tab (but first in all tabs)
kitten @ send-text --match=all kc spacedust'\n'
sleep 1

# choose color in first tab
kitten @ send-text --match=title:nya1 kc metal'\n'
kitten @ send-text --match=title:nya2 kc neon'\n'
sleep 1

# move to kp project in all windows
kitten @ send-text --match=all cd ~/dev/kp/kp'\n'
sleep 1

# turn on pyenv kp in all windows
kitten @ send-text --match=all pyenv activate kp'\n'
sleep 1

# checkout feat branch in nya1 windows
kitten @ send-text --match=title:nya1 git checkout feat'\n'
sleep 1

# run Docker watcher in second tab
echo spinning up containers
kitten @ send-text --match=title:nya4 docker compose watch'\n'
sleep 5

# run Tailwind watcher in second tab
kitten @ send-text --match=title:nya5 tailwindcss -i ./kp_app/static/kp_app/css/input.css -o ./kp_app/static/kp_app/css/output.css --watch'\n'

# run Docker logs in third terminal
kitten @ send-text --match=title:nya3 docker-compose logs --tail 500 -f '\n'

# switch focus back to first tab
kitten @ focus-window --match=title:nya1

