import numpy as np
import quaternion as quat

# quat=(w,x,y,z)=(cos(a/2),lam_x*sin(a/2),lam_y*sin(a/2),lam_z*sin(a/2))


def get_normalized_vector(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def get_cross_x(vector: np.ndarray) -> np.ndarray:
    return np.array([0, -vector[2], vector[1]])


def get_cross_y(vector: np.ndarray) -> np.ndarray:
    return np.array([vector[2], 0, -vector[0]])


def get_cross_z(vector: np.ndarray) -> np.ndarray:
    return np.array([-vector[1], vector[0], 0])


def create_quat_from_axis(axis: np.ndarray, cos: float) -> np.quaternion:
    cos_half = np.sqrt((1 + cos) / 2)
    sin_half = np.sqrt((1 - cos) / 2)
    return np.quaternion(
        cos_half,
        axis[0] * sin_half,
        axis[1] * sin_half,
        axis[2] * sin_half,
    )


def create_quat_from_2vector(
    v_from: np.ndarray, v_to: np.ndarray, normalized: bool = False
) -> quat.quaternion:
    if not normalized:
        v_from = get_normalized_vector(v_from)
        v_to = get_normalized_vector(v_to)
    axis = np.cross(v_from, v_to)
    cos = np.dot(v_from, v_to)
    return create_quat_from_axis(axis, cos)


def create_quat_from_vector_x(v_to: np.ndarray) -> np.ndarray:
    axis = get_cross_x(v_to)
    cos = v_to[0]
    return create_quat_from_axis(axis, cos)


def create_quat_from_vector_y(v_to: np.ndarray) -> np.ndarray:
    axis = get_cross_y(v_to)
    cos = v_to[1]
    return create_quat_from_axis(axis, cos)


def create_quat_from_vector_z(v_to: np.ndarray) -> np.ndarray:
    axis = get_cross_z(v_to)
    cos = v_to[2]
    return create_quat_from_axis(axis, cos)


def get_look_quat_v(forward: np.ndarray, up: np.ndarray) -> np.ndarray:
    forward = get_normalized_vector(forward)
    right = get_normalized_vector(np.cross(forward, up))
    q_z = create_quat_from_vector_y(forward)
    q_x = create_quat_from_vector_x(quat.rotate_vectors(q_z, right))
    # print("right:{},qz:{},qx:{}".format(right, q_z, q_x))
    return q_z * q_x


def get_look_quat_h(forward: np.ndarray, right: np.ndarray) -> np.ndarray:
    forward = get_normalized_vector(forward)
    up = get_normalized_vector(np.cross(right, forward))
    q_z = create_quat_from_vector_y(forward)
    q_y = create_quat_from_vector_x(quat.rotate_vectors(q_z, up))
    # print("up:{},up2:{},qz:{},qy:{}".format(up, quat.rotate_vectors(q_z, up), q_z, q_y))
    return q_z * q_y


print(get_look_quat_h(np.array([0, 0, 1]), np.array([0, 1, 0])))
