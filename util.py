import pickle


def save_to_file(dictionary, filename):
    with open(filename, 'wb') as f:
        pickle.dump(dictionary, f)

def read_from_file(filename):
    with open(filename) as f:
        dictionary = pickle.load(f)

    return dictionary