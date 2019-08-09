#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Jpegzilla
# A simple, cross-platform and lightweight graphical user interface for MozJPEG.
# https://github.com/noskla/jpegzilla
from pkg_resources import parse_version
from urllib.parse  import urlparse
from zipfile       import ZipFile
import requests, sys, os, shutil

# Check if user requested to run program with GUI enabled.
try:
	run_with_gui = (sys.argv[1] in ["-g", "--gui"])
except IndexError:
	run_with_gui = False

# Import packages required to run GUI.
if (run_with_gui):
	
	import tkinter, tkinter.ttk, threading
	from multiprocessing import Queue

# Import required information from the configuration file.
from conf import VER             as current_version
from conf import OS              as operating_system
from conf import TEMPDIR         as temporary_dir
from conf import _here           as installation_dir
from conf import JZ_ICON_TKINTER as program_icon

# Sends a request to the GitHub API to get a list of releases of jpegzilla,
# then compares it to the current version.
# Returns an dictionary containing:
#   "status" => boolean (true if updates are available,
#                       false if no updates available 
#                       or an error occurred).
#   "status-msg" => string (human-readable status summary)
#   "new-ver-url" => string (download URL of the new version, empty if no new version or error occurred)
def check_for_updates ():
	
	_releases_url = "https://api.github.com/repos/noskla/jpegzilla/releases"
	result = requests.get(_releases_url)
	
	# Check if GitHub API returned OK, otherwise return an error.
	if not result.status_code == 200:
		
		_status_msg = "Could not check for updates. GitHub returned status " + str(result.status_code)
		return {
			"status": False,
			"status-msg": _status_msg,
			"new-ver-url": ""
			}
		
	# Check if currently installed version is beta.
	is_current_pre_release = ("-pre" in current_version)

	# Get an array from json.
	releases_information = result.json()
	
	# Find in array an appropriate version for the current build.
	# (Replace pre-release version with pre-release or stable with stable)
	for release in releases_information:
		
		release_version = release["tag_name"]
		
		if ( "-pre" in release_version and not "-pre" in current_version ):
			continue
			
		else:
			newest_release = release
			break
		
	# Remove the "-pre" suffixes if they exist, then compare the versions.
	
	is_new_version_available = (
		parse_version(release_version) > parse_version(current_version)
	)
	
	# Exit the function if no new version is available.
	if (not is_new_version_available):
		return {
			"status": False,
			"status-msg": "No new versions are available.",
			"new-ver-url": ""
		}
	
	# Get the current system architecture and operating system.
	os_arch = ("x86_64" if (sys.maxsize > 2**32) else "x86")
	os_name = operating_system.lower()
	
	# Get the release's available builds.
	release_builds = newest_release["assets"]
	
	# Find the appropriate build for current system.
	for build in release_builds:
		
		# Jpegzilla's build names are named "jpegzilla - ver.sion - system - architecture"
		#                                    ^ [0]       ^ [1]      ^ [2]    ^ [3]
		# Let's remove the extension off the file name and
		# split those information into a list, and then put it into separate strings.
		build_filename    = build["name"][:-4]
		build_information = build_filename.split("-")
		
		build_program_name = build_information[0]
		build_version      = build_information[1]
		build_system_name  = build_information[2]
		build_architecture = build_information[3]
		
		# Check if the build's architecture is the same as system architecture
		_the_same_os   = (build_system_name  == os_name)
		_the_same_arch = (build_architecture == os_arch)
		
		# If so then create a string with url to this build and break the loop.
		if (_the_same_os and _the_same_arch):
			
			download_url = build["browser_download_url"]
			break
	
	# Return the data.
	return {
			"status": is_new_version_available, 
			"status-msg": "New version available.",
			"new-ver-url": download_url
		}

# / end of check_for_updates

# Downloads the .zip file from the specified source, unpacks it in
# temporary directory and replaces all the files in the jpegzilla directory.
# Arguments:
#   "download_url" => string (usually "new-ver-url" from the check_for_updates() function)
#	"label" => tkinter.Label (optional, used to update information)
#   "bar" => tkinter.Progressbar (optional, used to stop the bar after completion)
# Returns an dictionary containing:
#   "status" => boolean (true, if installed correctly, otherwise false)
#   "status-msg" => string (human-readable status summary)
def install_update (download_url, label="", bar=""):
	
	# Parse the URL and get the name of the file that has to be downloaded.
	parsed_url = urlparse(download_url)
	file_name  = os.path.basename(parsed_url.path)
	
	if (run_with_gui):
		label.configure(text="Downloading...")
		
	# Create a stream and download the file to the temporary directory.
	with requests.get(download_url, stream=True) as request:
		request.raise_for_status()
		
		# Save to file.
		location_to_save_to = (temporary_dir + file_name)
		with open(location_to_save_to, "wb") as new_file:
			
			# Get the content length header.
			content_length = request.headers.get("content-length")
			already_downloaded = 0
			
			for chunk in request.iter_content(chunk_size=4096):
				already_downloaded += len(chunk)
				new_file.write(chunk) if chunk else None
				
				percent_done = int(100 * already_downloaded / int(content_length))
				if (run_with_gui):
					label.configure(text = "Downloading..." + str(percent_done) + "%")
				else:
					print("Downloading..." + str(percent_done) + "%")
				
			new_file.close()
			
		# Create a string with a path to directory with unpacked files.
		new_version_files = (temporary_dir + "new_version/")
		
		if (run_with_gui):
			label.configure(text = "Unpacking...")
		else:
			print("Unpacking...")
			
		# Unpack the downloaded file.
		with ZipFile(location_to_save_to, "r") as zip_ref:
			zip_ref.extractall(new_version_files)
			# Switch to directory with jpegzilla files.
			new_version_files += "jpegzilla/"
			
		# Remove the zip file to save space.
		os.remove(location_to_save_to)
		
		if (run_with_gui):
			label.configure(text = "Installing...")
		else:
			print("Installing...")
			
		# Remove all the files in the installation directory
		# and move new version files to it, then return.
		shutil.rmtree(installation_dir, ignore_errors=True)
		shutil.move(new_version_files, installation_dir)
		
		if (run_with_gui):
			label.configure(text = "Done")
			bar.stop()
		else:
			print("Done")
		
		return {
			"status": True,
			"status-msg": "Success"
		}

# / end of install_update

if __name__ == "__main__":
	
	# Prepare tkinter window.
	if (run_with_gui):
		
		# Root window
		root = tkinter.Tk()
		root.geometry("320x135")
		root.title("Jpegzilla - Updating...")
		root.resizable(False, False)
		
		# Root window icon
		icon = tkinter.PhotoImage(file=program_icon)
		root.tk.call('wm', 'iconphoto', root._w, icon)

		# Text
		label = tkinter.Label(root, text="Checking for updates...")
		label.pack(pady='20')
		
		# Progress bar
		bar = tkinter.ttk.Progressbar(root, orient='horizontal', length=320, mode='indeterminate')
		bar.pack()
		bar.start()
		
	else:
		print("Checking for updates...")
		# Create empty variables, if tkinter functions not needed.
		label = ""
		bar   = ""
	
	# Check for updates.
	updates_result = check_for_updates()
	
	# If there's no update set the label with information or exit the program.
	if (not updates_result["status"]):
		
		if (run_with_gui):
			label.config(text=updates_result["status-msg"])
			bar.stop(); root.mainloop()
			
		else:
			print(updates_result["status-msg"])
			sys.exit()
	
	# Get the download URL from the check_for_updates() result.
	download_url = updates_result["new-ver-url"]
	
	if (run_with_gui):
		# Create background thread for install_update().
		installation_thread = threading.Thread(
			target = install_update,
			args = [ download_url, label, bar ],
			name = "installing_update"
		)
		
		installation_thread.start()
		root.mainloop()
		
	else:
		# Install the update.
		install_update(download_url)
		
