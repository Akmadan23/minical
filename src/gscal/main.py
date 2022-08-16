#!/usr/bin/env python
import gi, re, sys, toml, getopt
from importlib import metadata
from os import path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from . import gscal

def run():
    # Default configuration
    default_config = {
        "window_resizable": False,
        "sunday_first": False,
        "sunday_color": "#CC0000",
        "keybindings": {
            "next_month": "n",
            "prev_month": "p",
        }
    }

    # Default config file path
    config_path = "~/.config/gscal/gscal.toml"

    try:
        # Parse options and arguments
        opts, args = getopt.getopt(sys.argv[1:], "hvc:", ["help", "version", "config="])
    except getopt.GetoptError as e:
        print("[ERROR]", e)
        sys.exit(2)

    # Handle options
    for o, a in opts:
        if o in ["-h", "--help"]:
            # Print help message
            print(open(path.dirname(__file__) + "/data/help.txt", "r").read())
            sys.exit()
        elif o in ["-v", "--version"]:
            print("gscal", metadata.version("gscal"))
            sys.exit()
        elif o in ["-c", "--config"]:
            if path.isfile(path.expanduser(a)):
                config_path = a
            else:
                print(f"[WARNING] File {a} not found: reading from default config path ({config_path}).")

    # Handle arguments (not supported)
    for a in args:
        print("[WARNING] Unknown argument:", a)

    try:
        # Import settings from config file
        config = toml.load(path.expanduser(config_path))

        # Whether is necessary to check key bindings
        check_bindings = True

        # For each key of the default config dict
        for key in default_config:
            # If the value type does not match the default type or if sunday_color does not match a hex color pattern it falls back to the default
            if key not in config or type(config[key]) != type(default_config[key]) or (key == "sunday_color" and re.match("^#[0-9a-fA-F]{6}$", config[key]) is None):
                config[key] = default_config[key]

                # If the keybindings section is not declared in user's config there is no need to check each of them
                if key == "keybindings":
                    check_bindings = False

        if check_bindings:
            for key in default_config["keybindings"]:
                # If the value type is not a string or it's not a single character
                if key not in config["keybindings"] or type(config["keybindings"][key]) != str or len(config) != 1:
                    config["keybindings"][key] = default_config["keybindings"][key]

    except FileNotFoundError:
        print("[WARNING] Config file not found: default configuration loaded.")
        config = default_config
    except ValueError as e:
        print(f"[WARNING] Error in the config file: {e}. Default configuration loaded.")
        config = default_config

    # Initialize main window
    win = gscal.MainWindow(config)
    win.show_all()

    try:
        # Launch the GTK loop
        Gtk.main()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user.")

# Run the app when launched as script
if __name__ == "__main__":
    run()
