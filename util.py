import pickle


def save_to_json_file(dictionary, filename):
    with open(filename, 'wb') as f:
        pickle.dump(dictionary, f)

def read_from_json_file(filename):
    with open(filename) as f:
        dictionary = pickle.load(f)

    return dictionary

def remap_keys(mapping):
    return [{'key':k, 'value': v} for k, v in mapping.iteritems()]
