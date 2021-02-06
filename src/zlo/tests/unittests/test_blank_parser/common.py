import json
import os

from zlo.tests import fixtures


class BlankParserMixin:
    def get_matrix_data(self, file_name):
        file_path = os.path.join(os.path.dirname(fixtures.__file__), file_name + '.json')
        with open(file_path, 'r') as f:
            matrix = json.load(f)
        return matrix
