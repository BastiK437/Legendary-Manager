import subprocess
from subprocess import PIPE

installed_games_readable = []
installed_games_ugly = []
available_games_readable = []
available_games_ugly = []

def uninstall_game():
	print("####### Uninstall Game #######")
	print_installed()

	selection = get_selection("What you wanna uninstall?: ", 1, len(installed_games_readable))
	path = input("Path to game (" + installed_games_readable[selection-1] + "): ")
	
	uninstall_str = "legendary uninstall " + installed_games_ugly[selection-1]
	print("\n######### Uninstalling " + installed_games_readable[selection-1] + "#########")
	subprocess.call(uninstall_str)

def import_game():
	print("####### Import Game #######")
	print_available()

	selection = get_selection("What you wanna import?: ", 1, len(available_games_readable))
	path = input("Path to game (" + available_games_readable[selection-1] + "): ")
	
	import_str = "legendary import " + available_games_ugly[selection-1] + " " + path
	print("\n######### Importing " + available_games_readable[selection-1] + "#########")
	subprocess.call(import_str)


def get_selection(input_str, lower_limit, high_limit):
	while True:
		selection = input(input_str)
		if selection.isnumeric():
				selection = int(selection)
		else:
			print("Not a number")
			continue

		if selection < lower_limit or selection > high_limit:
			print("Selection out of range")
			continue
		return selection

def print_installed():
	i = 1
	for game in installed_games_readable:
		print("[" + str(i) + "] " + game)
		i = i + 1

def print_available():
	i = 1
	for game in available_games_readable:
		print("[" + str(i) + "] " + game)
		i = i + 1

def launch_game():
	print("####### Launch Game #######")
	print_installed()

	selection = get_selection("What you wanna play?: ", 1, len(installed_games_ugly))
	
	launch_str = "legendary launch " + installed_games_ugly[selection-1]
	print("\n######### Launching " + installed_games_readable[selection-1] + "#########")
	subprocess.call(launch_str)

def update_games():
	print("####### Update Game(s) #######")
	print_installed()

	selection = get_selection("What you wanna update? (0 for everything): ", 0, len(installed_games_ugly))

	if selection == 0:
		for game in installed_games_ugly:
			update_str = "legendary update CrabTest"
			print(update_str)
			subprocess.call(update_str)
	else:
		update_str = "legendary update " + installed_games_ugly[selection-1]
		print("\n####### UPDATE " + installed_games_readable[selection-1] + " #######")
		subprocess.call(update_str)

	


def fill_installed_games():
	if installed_games_ugly and installed_games_readable:
		return
	else:
		installed_raw = (subprocess.run("legendary list-installed", capture_output=True)).stdout
		installed_raw = installed_raw.decode('utf-8', 'backslashreplace')
		string_to_search = "App name: "
		position_ugly = 0
		while True:
			position_readable = installed_raw.find('*', position_ugly) + 2
			position_ugly = installed_raw.find(string_to_search, position_ugly)
			if position_ugly == -1:
				return
			position_ugly = position_ugly  + len(string_to_search)
			game_readable = installed_raw[position_readable:installed_raw.find("(",position_readable)-1]
			game_ugly = installed_raw[position_ugly:installed_raw.find(" ",position_ugly)]
			
			installed_games_readable.append(game_readable)
			installed_games_ugly.append(game_ugly)

def fill_available_games():
	if available_games_ugly and available_games_readable:
		return
	else:
		available_raw = (subprocess.run("legendary list-games", capture_output=True)).stdout
		available_raw = available_raw.decode('utf-8', 'backslashreplace')
		string_to_search = "App name: "
		position_ugly = 0
		while True:
			position_readable = available_raw.find('*', position_ugly) + 2
			position_ugly = available_raw.find(string_to_search, position_ugly)
			if position_ugly == -1:
				return
			position_ugly = position_ugly  + len(string_to_search)
			game_readable = available_raw[position_readable:available_raw.find("(",position_readable)-1]
			game_ugly = available_raw[position_ugly:available_raw.find(" ",position_ugly)]
			
			available_games_readable.append(game_readable)
			available_games_ugly.append(game_ugly)


def main():
	while True:
		print("\n\n\n\n####### Legendary Manager #######")
		print("[1] Launch game")
		print("[2] Update game(s)")
		print("[3] Import game")
		print("[4] Move game (not implemented yet)")
		print("[5] Install game (not implemented yet)")
		print("[6] Uninstall game")
		print("[9] Exit")
		
		selection = input("Enter your selection: ")
		if selection.isnumeric():
			selection = int(selection)
		else:
			print("Not a number")
			continue

		if selection == 9:
			exit()
		if selection < 1 and selection > 5:
			print("Selection out of range")
			continue
			
		fill_installed_games()
		fill_available_games()
		print()
		if selection == 1:
			launch_game()
		elif selection == 2:
			update_games()
		elif selection == 3:
			import_game()
		elif selection == 4:
			print("To be done")
		elif selection == 5:
			uninstall_game()

if __name__=="__main__":
	main()
