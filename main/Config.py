def new_config(self):
    # size and ratio for showing onto the pygame screen and converting data
    size = self.img.size
    self.track_config_obj['CHECKPOINTS'] = {
        'START': ((-1, -1), -1, (-1, -1), (-1, -1)),  # (midpoint, radius, edge_1, edge_2)
        'FINISH': ((-1, -1), -1, (-1, -1), (-1, -1)),  # (midpoint, radius, edge_1, edge_2)
        'CHECKPOINTS': [],  # [(midpoint, radius, edge_1, edge_2), (midpoint, radius, edge_1, edge_2), ...]
    }
    self.track_config_obj['DISPLAY'] = {
        'ORIGINAL SIZE': size,  # (width, height)
        'SIMULATOR SIZE': (1200, 900),  # (width, height)
    }
    self.track_config_obj['TRACK'] = {
        'START ANGLE': 0,  # automatically filled by the program, do not change
    }
    self.track_config_obj['CAR'] = {
        'SPEED': 10.0,  # Number of pixels the car can travel within 1 second, at the start
        'MAX SPEED': 15.0,  # Maximum speed the car can travel
        'MIN SPEED': 5.0,  # Maximum speed the car can travel
        'SPEED STEP': 1.0,  # The value for the speed to change each time
        'LENGTH': 60.0,  # The length of the car in pixels
        'WIDTH': 60.0,  # The width of the car in pixels
        'TURNING ANGLE': 7,  # angle the car can turn in degrees, max 10 degrees
    }
    self.track_config_obj['NN'] = {
        'LEARNING RATE': 0.05,  # learning rate of the neural network
        'MUTATION RATE': 0.05,  # mutation rate of the neural network
        'POPULATION': 20,  # number of neural networks in one generation, have to be even
        'GENERATIONS': 1000,  # number of generations
        'TIME': 20,  # Time allowed for each generation
        'FITNESS THRESHOLD': 0.0,  # fitness threshold of the neural network, automatically filled by the program
    }