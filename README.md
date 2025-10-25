# ACM_Minecraft_Script

## Hello fellow ACM members, and non-members!

We will walk you through on how to use this lovely minecraft script to easily and automatically grab data. This is a (almost) fully automated system that takes screenshots at random locations and sorts them by biome name. By now I hope that you have minecraft installed… lets get started!


## 1. Setup the repo

1. First clone this repo into your computer:
```
git clone https://github.com/dregiske/ACM_Minecraft_Script.git
```

2. After cloning this repo, lets start up a environment:
```
python -m venv venv
source venv/bin/activate	# for my macOS users
venv\Scripts\activate		# for my windows users
```

3. Lets also install the dependencies we will need for this to work:
```
pip install pyautogui pyobjc-core pyobjc-framework-Quartz amulet-core amulet-leveldb amulet-nbt numpy
```

4. Then let's direct ourselves to the correct directory:
```
cd scripts
```

### HOW IT FUNCTIONS
(if you're uninterested, you can skip this part, see `2. Setup Minecraft`)  
In this directory, we have 3 simple files:

1. `player_script.py`: this is the player script which does the teleporting and screenshotting for us. It uses the random library to randomly pick some `x`, `z` coordinates and teleports to them. Then it screenshots and saves the file under those coordinates with a random integer ID.

2. `amulet_data_reader.py`: this program grabs the chunk data by parsing the `.png` file names labelled with their coordinates, and finds the biome name at those coordinates. 
- EXAMPLE: `312_87_9083.png` -> `x: 312`, `z: 87`, `rand_id: 9083`

3. `sort_photos.py`: this script auto sorts the `.png` screenshots into directories labelled by their biome name using `amulet_data_reader.py`.
- EXAMPLE: chunk at `x` and `z` = `minecraft:plains` -> move to `data/plains`


## 2. Setup Minecraft

Now lets boot up Minecraft! Now in the launcher, we will first load into version 1.14 of Minecraft. 

1. Find the installations tab located at the top of the screen
2. Click `New installation`.
3. Name the world whatever you like.
4. Under the `VERSION` dropbox, pick anywhere between `release 1.14` - `release 1.14.3`.
5. Then under `GAME DIRECTORY`, this is where you pick where the game files will be stored. This is important so take note of this later, I like to keep mine in `~/Documents`, but whatever works.

Open the new world we just created. Before we can let the scripts run, lets optimize our game settings for the best data.

1. Set our weather and time:
```
/time set noon
/weather clear
```

2. Stop the weather and time cycles so it stays perfect forever:
```
/gamerule doDaylightCycle false
/gamerule doWeatherCycle false
```

3. Kill all mobs so they don't interfere with our data:
```
/kill @e[type=!minecraft:player]
```

4. Turn off the HUD by pressing `f3` (`fn + f3` for macOS)


## 3. player_script.py

Setup is done! Now we can begin grabbing data. I like to keep my game windowed, to see the progress displayed in the IDE terminal (I have setup print statements that show progress on screenshots, at your convenience).  
At the top of the file, I set up the settings section, here we can tweak:
- how many screenshots we want to take,
- the range at which we want our player to teleport to,
- and the time we set the script to sleep to allow our computer to render the chunk. It is important that we give the computer time to render the chunk so the information is stored properly in the game folders.

In the same section are file paths, modify the screenshots path to where your game files are being saved (from `2. Setup Minecraft` steps)
- EXAMPLE: I saved my game files at `~/Documents`, so the in-game screenshots will be located at `~/Documents/screenshots`.

Also modify the destination file path, where you want the data to be temporarily stored.

1. Run the file:
```
python player_script.py
```

2. Open the Minecraft game and let it run.

Let this run for as much as you like. Running it multiple times will not affect previous data, everything will be stored incrementally in the specified directory labelled in the `SETTINGS` section.

Use `control + c` to interrupt the script (macOS).


## 4. sort_photos.py

Now that we have our data, lets sort it!. This `main()` function takes at least 4 args:
1. `arg[0] = sort_photos`
2. `arg[1] = minecraft/world/path`
3. `arg[2] = where-the-current-screenshots-are`
4. `arg[3] = where-we-want-the-screenshots-to-go`

When calling the function, it will look like this (modify to your filepaths):
```
python sort_photos.py \
  --world "~/Documents/saves/ACM" \
  --src "~/Desktop/biome_screenshots" \
  --out "~/Desktop/final_screenshots"
```

We can also add the `--dry-run` tag to ensure the script runs smoothly before making any changes:
```
python sort_photos.py \
  --world "~/Documents/saves/ACM" \
  --src "~/Desktop/biome_screenshots" \
  --out "~/Desktop/final_screenshots" \
  --dry-run
```

## 5. Other notes
If you're having issues with pyautogui, make sure accessibility is on
FOR MACOS:
```
System Settings > Privacy & Security > Accessibility > Toggle terminal on
```
! im not sure if Windows runs into this issue...

Documentation:  
https://amulet-core.readthedocs.io/en/latest/getting_started/read_chunk.html  
https://amulet-nbt.readthedocs.io/en/3.0/api_reference/index.html  

Thats all! Have fun!
`:)`