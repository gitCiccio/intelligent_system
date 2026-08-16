class ColException(Exception):
    def __init__(self, message):
        super().__init__(message)

"""
    Raise exceptions related to dataset creation or loading
"""
class DatasetColException(ColException):
    pass

"""
    Raise exceptions related to topology or timeout errors during his resolutions
"""
class GraphColException(ColException):
    def __init__(self, message, num_nodes=None, graph_type=None):
        super().__init__(message)
        self.num_nodes = num_nodes
        self.graph_type = graph_type

    def __str__(self):
        base_msg = super().__str__()
        if self.num_nodes and self.graph_type:
            return f"{base_msg} (Graph Type: {self.graph_type}, Number of Nodes: {self.num_nodes})"
        return base_msg

class ModelColException(ColException):
    pass

class TrainingColException(ColException):
    pass

