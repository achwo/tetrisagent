import pickle
import json
import os

CONFIG_FILENAME = 'config.json'
STATISTICS_FILENAME = 'q-statistics.json'
Q_FILENAME = 'q-table.bin'


def save_gui_config(controller):
    alpha = float(controller.panel.alphaInput.get())
    gamma = float(controller.panel.gammaInput.get())
    epsilon = float(controller.panel.epsilonInput.get())
    fastforward_count = int(controller.panel.fastForwardInput.get())
    config = {'alpha': alpha, 'gamma': gamma, 'epsilon': epsilon,
              'fastforward_count': fastforward_count}
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        CONFIG_FILENAME)
    with open(path, 'w') as f:
        json.dump(config, f)


def save_statistics(array):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        STATISTICS_FILENAME)
    config = {'steps_per_episode': array}
    with open(path, 'w') as f:
        json.dump(config, f)


def load_json(filename):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        filename)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except IOError:
        print 'Error reading config file'


def save_q_table(dictionary):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        Q_FILENAME)
    with open(path, 'wb') as f:
        pickle.dump(dictionary, f)


def load_q_table():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        Q_FILENAME)
    with open(path) as f:
        dictionary = pickle.load(f)
    return dictionary
