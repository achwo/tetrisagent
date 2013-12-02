import pickle
import json
import os

CONFIG_FILENAME = 'config.json'

def save_gui_config(controller):
    alpha = float(controller.control_panel.alphaInput.get())
    gamma = float(controller.control_panel.gammaInput.get())
    epsilon = float(controller.control_panel.epsilonInput.get())
    config = {'alpha' : alpha, 'gamma' : gamma, 'epsilon' : epsilon }
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), CONFIG_FILENAME)
    with open(path, 'w') as f:
        json.dump(config, f)


def load_gui_config(controller):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), CONFIG_FILENAME)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except IOError:
        pass


def save_to_file(dictionary, filename):
    with open(filename, 'wb') as f:
        pickle.dump(dictionary, f)


def read_from_file(filename):
    with open(filename) as f:
        dictionary = pickle.load(f)

    return dictionary
