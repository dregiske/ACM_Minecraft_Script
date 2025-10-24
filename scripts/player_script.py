'''
This is a player script that automatically
sets weather and time settings, teleports to
randomized locations, and screenshots the
players screen

How to use:
1) run env
python -m venv venv
source venv/bin/activate

2) install dependencies:
pip install pyautogui pyobjc

3) run program
python player_script.py

4) switch to minecraft and let it run

! If you're having issues with pyautogui,
make sure accessibility is on
FOR MACOS:
System Settings > Privacy & Security > Accessibility > Toggle terminal on

For optimal screenshot data (in minecraft world), do:
/time set noon
/weather clear
/gamerule doDaylightCycle false
/gamerule doWeatherCycle false
/kill @e[type=!minecraft:player]
'''

import os, time, random, shutil, sys, platform
import pyautogui


# ---- SETTINGS ----

NUM_TELEPORTS	= 50 		# how many screenshots
X_RANGE			= (2000, 5000)
Y_RANGE			= (90, 120)
Z_RANGE			= (2000, 5000)

TP_WAIT_SECONDS = 8.5 		# tweak to accomodate computer

FILE_PATHS = {
	"destination": os.path.expanduser("~/Desktop/biome_screenshots"),
	"screenshots": os.path.expanduser("~/Documents/screenshots")
}


# ---- HELPERS ----

def update_file(folder):
	'''
	Finds the most recent file
	created in folder, or None
	'''
	try:
		files = [os.path.join(folder, f) for f in os.listdir(folder)]
		files = [f for f in files if os.path.isfile(f)]
		return max(files, key=os.path.getctime) if files else None
	except FileNotFoundError:
		return None

def timeout(folder, prev_latest, timeout):
	'''
	Grabs the updated file for up to timeout seconds.
	Returns the new file path, or none if timeout.
	'''
	start = time.time()
	while time.time() - start < timeout:
		cur_latest = update_file(folder)
		if cur_latest and cur_latest != prev_latest and (
		not prev_latest or os.path.getctime(cur_latest) > os.path.getctime(prev_latest)
		):
			return cur_latest
		time.sleep(0.25)
	return None

def verify_dir(folder):
	'''
	Verifies that folder path exists,
	specifically used for screenshot path.
	'''
	if not os.path.isdir(folder):
		print(f"Screenshot folder not found:\n {folder}")
		print("Make sure your Minecraft screenshots path is correct for your OS.")
		print("Press F2 in Minecraft and see where the file appears, then set file path accordingly.")
		sys.exit(1)

def safe_move(src, dest, retries=5, delay=0.2):
	'''
	Safety net to make sure files are
	safely moved across directories
	'''
	for i in range(retries):
		try:
			shutil.move(src, dest)
			return True
		except Exception:
			time.sleep(delay)
	return False


# ---- MAIN SCRIPT ----

def main():
	DEST_DIR = FILE_PATHS["destination"]
	os.makedirs(DEST_DIR, exist_ok=True)

	SCREENSHOT_DIR = FILE_PATHS["screenshots"]

	print(f"Using Minecraft screenshots folder:\n {SCREENSHOT_DIR}")
	print(f"Destination folder:\n {DEST_DIR}")
	verify_dir(SCREENSHOT_DIR)

	print("You have 5 seconds to click into Minecraft. . .")
	time.sleep(5)

	for i in range(NUM_TELEPORTS):
		x = random.randint(*X_RANGE)
		y = random.randint(*Y_RANGE)
		z = random.randint(*Z_RANGE)

		prev_latest = update_file(SCREENSHOT_DIR)

		# teleport
		cmd = f"/tp {x} {y} {z}"
		pyautogui.press('t')
		pyautogui.typewrite(cmd)
		pyautogui.press('enter')

		time.sleep(TP_WAIT_SECONDS + random.uniform(0.5, 1.5))

		# take screenshot
		pyautogui.press('f2')

		# wait for the new screenshot file to appear
		new_file = timeout(SCREENSHOT_DIR, prev_latest, timeout=10)

		if not new_file:
			print(f"Could not detect a new screenshot after teleport {i+1}.")
			print("Verify F2 (fn+F2 on Mac) captures screenshots, check Accessibility permissions,")
			print("and confirm the screenshots folder path.")
			continue
		
		# move to destination folder + rename
		rand_id = random.randint(1000, 9999)
		new_name = f"{x}_{z}_{rand_id}.png"
		dest_path = os.path.join(DEST_DIR, new_name)
		
		if safe_move(new_file, dest_path):
			print(f"[{i + 1}/{NUM_TELEPORTS}] Teleported to {x},{y},{z} -> saved {new_name}")
		else:
			print(f"Failed to move {new_file} -> {dest_path}.")
	print("Done")

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Aborting...")