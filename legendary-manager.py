from enum import Enum
import subprocess
from subprocess import PIPE
from pathlib import Path
import string
import os

installed_games_readable = []
installed_games_ugly = []
available_games_readable = []
available_games_ugly = []
importable_games_readable = []
importable_games_ugly = []

legendary_call_str = "legendary"
# legendary_call_str = "C:\\Users\\Basti\\Desktop\\legendary\\legendary"

class Context(Enum):
	AVAILABLE_GAMES = 1
	INSTALLED_GAMES = 2
	IMPORTABLE_GAMES = 3

# enum.value for the string
class Commands(Enum):
	LAUNCH		= "launch"
	UPDATE 		= "update"
	IMPORT 		= "import"
	MOVE 		= "move"
	INSTALL 	= "install"
	UNINSTALL 	= "uninstall"
	SYNC		= "sync-saves"
	VERIFY		= "verify"


def change_installation_dir():
	path_to_config = str(Path.home()) + "\.config\legendary\config.ini"
	if os.path.isfile(path_to_config) == False:
		print("Can't find legendary config file. Should be at \"C:\\Users\\user\\.config\\legendary\\config.ini\"")
		return
	
	with open(path_to_config, "r") as config_file:
		content = config_file.readlines()
	
	i = 0
	for line in content:
		inst_dir_position = line.find("install_dir")
		if inst_dir_position != -1:
			dir_line = line
			break
		i = i + 1

	inst_dir_position = inst_dir_position + len("install_dir = ")
	current_dir = content[i][inst_dir_position:len(dir_line)]
	print("Current dir: " + current_dir)
	change_dir = input("Change installation dir? Y/N: ")
	if change_dir.upper() == 'Y':
		new_dir = input("Enter new installation dir: ")
		if os.path.isdir(new_dir) == False:
			print("Path not valid!")
		else:
			content[i] = "install_dir = " + new_dir
			with open(path_to_config, "w") as config_file:
				config_file.writelines(content)
			print("Installation directory changed!")


def legendary_cmd(command, selection_text, context):
	print("####### " + command.value + " Game #######")
	print_games(context)

	if context == Context.INSTALLED_GAMES:
		highest_selection = len(installed_games_readable) + 1
	elif context == Context.AVAILABLE_GAMES:
		highest_selection = len(available_games_readable) + 1
	elif context == Context.IMPORTABLE_GAMES:
		highest_selection = len(importable_games_readable) + 1
	else:
		error("[legendary_cmd] 0x01")
	
	while True:
		selection = get_selection(selection_text)
		
		lowest_selection = 1
		if command == Commands.UPDATE:
			lowest_selection = 0
		elif command == Commands.IMPORT:
			lowest_selection = 0
		elif command == Commands.VERIFY:
			lowest_selection = 0


		if (selection < lowest_selection) or (selection > highest_selection):
			print("Selection out of range")
			continue
		break

	if selection == highest_selection:
		return

	cmd_postfix = ""

	legendary_call_needed = True

	if command == Commands.LAUNCH:
		# nothing special to do here
		pass
	elif command == Commands.UPDATE:
		if selection == 0:
			for i in range(len(installed_games_readable)):
				legendary_call(context, command, cmd_postfix, i)
			
			legendary_call_needed = False

	elif command == Commands.IMPORT:
		if selection == 0:
			path = input("Path to gamefolder: ")
			sub_dirs = []
			for element in os.listdir(path):
				d = os.path.join(path, element)
				if os.path.isdir(d):
					sub_dirs.append(d)
			
			for sub_dir in sub_dirs:
				read = input("Do you want to import this game? (Y/N): " + sub_dir + " :")
				if read.upper() == 'Y':
					print_games(context)
					selection = get_selection("Select the related game to the folder: ")
					cmd_postfix = " " + path
					legendary_call(context, command, cmd_postfix, selection-1)

			legendary_call_needed = False
		else:
			path = input("Path to game (" + available_games_readable[selection-1] + "): ")
			cmd_postfix = " " + path

	elif command == Commands.MOVE:
		path = input("New game location (" + installed_games_readable[selection-1] + "): ")
		cmd_postfix = " " + path

	elif command == Commands.INSTALL:
		change_installation_dir()
	elif command == Commands.UNINSTALL:
		# nothing special to do here
		pass
	elif command == Commands.SYNC:
		pass
	elif command == Commands.VERIFY:
		print("Verifying output is buggy, just be patient, it takes a while")
		if selection == 0:
			for i in range(len(installed_games_readable)):
				legendary_call(context, command, cmd_postfix, i)
			
			legendary_call_needed = False

	if legendary_call_needed == True:
		legendary_call(context, command, cmd_postfix, selection-1)

def legendary_call(context, command, cmd_postfix, selection):
	if context == Context.INSTALLED_GAMES:
		cmd_list_ugly = installed_games_ugly
		cmd_list_readable = installed_games_readable
	elif context == Context.AVAILABLE_GAMES:
		cmd_list_ugly = available_games_ugly
		cmd_list_readable = available_games_readable
	elif context == Context.IMPORTABLE_GAMES:
		cmd_list_ugly = importable_games_ugly
		cmd_list_readable = importable_games_readable
	else:
		error("[legendary_call] 0x01")

	command_str = legendary_call_str + " " + command.value + " " + cmd_list_ugly[selection] + cmd_postfix
	print("\n######### " + command.value + " " + cmd_list_readable[selection] + " #########")
	result = subprocess.run(command_str, stdout=subprocess.PIPE, universal_newlines=True)

	print(result.stdout)

def get_selection(input_str):
	while True:
		selection = input(input_str)
		if selection.isnumeric():
			selection = int(selection)
		else:
			print("Not a number")
			continue
		return selection

def print_games(context):
	if context == Context.AVAILABLE_GAMES:
		list = available_games_readable
	elif context == Context.INSTALLED_GAMES:
		list = installed_games_readable
	elif context == Context.IMPORTABLE_GAMES:
		list = importable_games_readable
	else:
		error("[print_games] 0x01")

	i = 1
	for game in list:
		print("[" + str(i) + "] " + game)
		i = i + 1

	print("[" + str(i) + "] " + "Abort")

def fill_game_list(context):
	if context == Context.AVAILABLE_GAMES:
		output_raw = (subprocess.run("legendary list-games", capture_output=True)).stdout
		available_games_readable.clear()
		available_games_ugly.clear()
	elif context == Context.INSTALLED_GAMES:
		output_raw = (subprocess.run("legendary list-installed", capture_output=True)).stdout
		installed_games_readable.clear()
		installed_games_ugly.clear()
	elif context == Context.IMPORTABLE_GAMES:
		for game in available_games_ugly:
			if not game in installed_games_ugly:
				importable_games_ugly.append(game)

		for game in available_games_readable:
			if not game in installed_games_readable:
				importable_games_readable.append(game)
		return

	else:
		error("[fill_game_list] 0x01")

	output_raw = output_raw.decode('utf-8', 'backslashreplace')
	string_to_search = "App name: "
	position_ugly = 0
	while True:
		position_readable = output_raw.find('*', position_ugly) + 2
		position_ugly = output_raw.find(string_to_search, position_ugly)
		if position_ugly == -1:
			return
		position_ugly = position_ugly  + len(string_to_search)
		game_readable = output_raw[position_readable:output_raw.find("(",position_readable)-1]
		game_ugly = output_raw[position_ugly:output_raw.find(" ",position_ugly)]
		
		if context == Context.AVAILABLE_GAMES:
			available_games_readable.append(game_readable)
			available_games_ugly.append(game_ugly)
		elif context == Context.INSTALLED_GAMES:
			installed_games_readable.append(game_readable)
			installed_games_ugly.append(game_ugly)
		else:
			error("[fill_game_list] 0x02")

def error(error):
	print("ERROR " + error)
	exit()


def main():
	while True:
		print("\n\n\n\n####### Legendary Manager #######")
		print("[1] Launch game")
		print("[2] Update game(s)")
		print("[3] Import game(s)")
		print("[4] Install game")
		print("[5] Uninstall game")
		print("[6] Move game")
		print("[7] Sync Game")
		print("[8] Change installation directory")
		print("[9] Verify game(s)")
		print("[0] Exit")
		
		selection = input("Enter your selection: ")
		if selection.isnumeric():
			selection = int(selection)
		else:
			print("Not a number")
			continue

		if selection == 0:
			exit()
			
		fill_game_list(Context.AVAILABLE_GAMES)
		fill_game_list(Context.INSTALLED_GAMES)
		fill_game_list(Context.IMPORTABLE_GAMES)

		print()
		if selection == 1:
			legendary_cmd(Commands.LAUNCH, "What you wanna play?: ", Context.INSTALLED_GAMES)
		elif selection == 2:
			legendary_cmd(Commands.UPDATE, "What you wanna update? (0 for everything): ", Context.INSTALLED_GAMES)
		elif selection == 3:
			legendary_cmd(Commands.IMPORT, "What you wanna import? (0 for multiple): ", Context.IMPORTABLE_GAMES)
		elif selection == 4:
			legendary_cmd(Commands.INSTALL, "What game you wanna install?: ", Context.AVAILABLE_GAMES)
		elif selection == 5:
			legendary_cmd(Commands.UNINSTALL, "What game you wanna uninstall?: ", Context.INSTALLED_GAMES)
		elif selection == 6:
			legendary_cmd(Commands.MOVE, "What game you wanna move?: ", Context.INSTALLED_GAMES)
		elif selection == 7:
			legendary_cmd(Commands.SYNC, "What game you wanna sync?: ", Context.INSTALLED_GAMES)
		elif selection == 8:
			change_installation_dir()
		elif selection == 9:
			legendary_cmd(Commands.VERIFY, "What you wanna verify? (0 for everything): ", Context.INSTALLED_GAMES)
		else:
			print("Selection out of range")

if __name__=="__main__":
	main()
