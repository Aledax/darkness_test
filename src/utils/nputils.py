import numpy as np


def project_vector(from_vector: list, onto_vector: list):

    onto_vector_norm_squared = np.dot(onto_vector)
    if onto_vector_norm_squared == 0:
        return None
    return ((np.dot(from_vector, onto_vector) / onto_vector_norm_squared) * onto_vector).tolist()