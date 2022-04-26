from configparser import ConfigParser


class Config:
    """Read and write config file"""

    def __init__(self, track_name):
        self.config_obj = ConfigParser()
        self.config_path = 'tracks/' + track_name[:6] + '.txt'
        if self.check_validity(self.config_path):
            self.config_obj.read(self.config_path)
        else:
            self.new_config()
    # end procedure

    def new_config(self):
        self.config_obj['CHECKPOINTS'] = {
            'START': ((-1, -1), (-1, -1)),  # (coordinate_1, coordinate_2)
            'FINISH': ((-1, -1), -1),  # (coordinate, radius)
            'CHECKPOINTS': [],  # [(coordinate, radius), (coordinate, radius), ...]
        }
        self.config_obj['TRACK'] = {
            'START ANGLE': 0,  # automatically filled by the program, do not change
            'MAX STEP': 0,  # automatically filled by the program, only change when the training cannot be done
            'SETTING RATIO': 1.0,  # ratio change of the track on the checkpoints page(settings)
            'SIMULATOR RATIO': 1.0,  # ratio change of the track on any simulator page
        }
        self.config_obj['CAR'] = {
            'SPEED RATIO': 0.0,  # assume the length of the starting line is 1, enter distance the car can cover in 1s
            'CAR RATIO': 0.0,  # length of the car relative to the starting line, max 0.8
            'TURNING ANGLE': 0,  # angle the car can turn in degree, max 60
        }
        self.config_obj['NN'] = {
            'LEARNING RATE': 0.05,  # learning rate of the neural network
            'MUTATION RATE': 0.05,  # mutation rate of the neural network
            'MOMENTUM': 0.9,  # momentum of the neural network
            'ACTIVATION': 'tanh',  # activation function of the neural network
            'POPULATION': 20,  # number of neural networks in one generation, have to be even
            'GENERATIONS': 1000,  # number of generations
            'FITNESS THRESHOLD': 0.0,  # fitness threshold of the neural network, automatically filled by the program
        }
    # end procedure

    @staticmethod
    def check_validity(file_path):
        if not os.path.isfile(file_path):
            return False
        else:
            config_obj = ConfigParser()
            config_obj.read(file_path)
            sections = config_obj.sections()
            if 'CHECKPOINTS' not in sections or 'TRACK' not in sections or 'CAR' not in sections or 'NN' not in sections:
                return False
            else:
                return True
            # end if`
    # end function
# end class
