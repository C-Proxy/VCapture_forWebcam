import json
import numpy as np
import quaternion as quat

# quat=(w,x,y,z)=(cos(a/2),lam_x*sin(a/2),lam_y*sin(a/2),lam_z*sin(a/2))


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def get_cross_x(vector: np.ndarray) -> np.ndarray:
    return np.array([0, -vector[2], vector[1]])


def get_cross_y(vector: np.ndarray) -> np.ndarray:
    return np.array([vector[2], 0, -vector[0]])


def get_cross_z(vector: np.ndarray) -> np.ndarray:
    return np.array([-vector[1], vector[0], 0])


def create_quat_from_axis(
    axis: np.ndarray, cos: float, normalized: bool = False
) -> np.quaternion:
    cos_half, sin_half = get_half_trigonometry(cos)
    if not normalized:
        axis = normalize_vector(axis)
    return np.quaternion(
        cos_half,
        axis[0] * sin_half,
        axis[1] * sin_half,
        axis[2] * sin_half,
    )


def create_quat_from_axis_x(cos: float) -> np.quaternion:
    cos_half, sin_half = get_half_trigonometry(cos)
    return np.quaternion(cos_half, sin_half, 0, 0)


def create_quat_from_axis_y(cos: float) -> np.quaternion:
    cos_half, sin_half = get_half_trigonometry(cos)
    return np.quaternion(cos_half, 0, sin_half, 0)


def create_quat_from_axis_z(cos: float) -> np.quaternion:
    cos_half, sin_half = get_half_trigonometry(cos)
    return np.quaternion(cos_half, 0, 0, sin_half)


def create_quat_from_axis_minus_z(cos: float) -> np.quaternion:
    cos_half, sin_half = get_half_trigonometry(cos)
    return np.quaternion(cos_half, 0, 0, -sin_half)


def get_half_trigonometry(cos: float) -> tuple[float, float]:
    return np.sqrt((1 + cos) / 2), np.sqrt((1 - cos) / 2)


def create_quat_from_2vector(
    v_from: np.ndarray, v_to: np.ndarray, normalized: bool = False
) -> quat.quaternion:
    if not normalized:
        v_from = normalize_vector(v_from)
        v_to = normalize_vector(v_to)
    axis = np.cross(v_from, v_to)
    cos = np.dot(v_from, v_to)
    return create_quat_from_axis(axis, cos)


def create_focus_quat_x(v_to: np.ndarray) -> np.ndarray:
    axis = get_cross_x(v_to)
    cos = v_to[0]
    return create_quat_from_axis(axis, cos)


def create_focus_quat_y(v_to: np.ndarray) -> np.ndarray:
    axis = get_cross_y(v_to)
    cos = v_to[1]
    return create_quat_from_axis(axis, cos)


def create_focus_quat_z(v_to: np.ndarray) -> np.ndarray:
    axis = get_cross_z(v_to)
    cos = v_to[2]
    return create_quat_from_axis(axis, cos)


def rotated_axis_x(q: np.ndarray) -> np.ndarray:
    q0 = q.w
    q1 = q.x
    q2 = q.y
    q3 = q.z
    return np.array(
        [
            q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3,
            (q1 * q2 + q0 * q3) * 2,
            (q1 * q3 - q0 * q2) * 2,
        ]
    )


def rotated_axis_y(q: np.ndarray) -> np.ndarray:
    q0 = q.w
    q1 = q.x
    q2 = q.y
    q3 = q.z
    return np.array(
        [
            (q1 * q2 - q0 * q3) * 2,
            q0 * q0 - q1 * q1 + q2 * q2 - q3 * q3,
            (q2 * q3 + q0 * q1) * 2,
        ]
    )


def rotated_axis_z(q: np.ndarray) -> np.ndarray:
    q0 = q.w
    q1 = q.x
    q2 = q.y
    q3 = q.z
    return np.array(
        [
            (q1 * q3 + q0 * q2) * 2,
            (q2 * q3 - q0 * q1) * 2,
            q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3,
        ]
    )


def get_look_quat_zy(forward: np.ndarray, up: np.ndarray) -> quat.quaternion:
    forward = normalize_vector(forward)
    right = normalize_vector(np.cross(forward, up))
    q_f = create_focus_quat_z(forward)
    return get_fix_quat_z(forward, right, rotated_axis_x(q_f), q_f)


def get_look_quat_zx(forward: np.ndarray, right: np.ndarray) -> quat.quaternion:
    forward = normalize_vector(forward)
    up = normalize_vector(np.cross(right, forward))
    q_f = create_focus_quat_z(forward)
    return get_fix_quat_z(forward, up, rotated_axis_y(q_f), q_f)


def get_fix_quat_z(
    forward: np.ndarray,
    sub_vector: np.ndarray,
    rotated_axis: np.ndarray,
    q_f: np.quaternion,
) -> np.ndarray:
    dot = np.dot(np.cross(rotated_axis, sub_vector), forward)
    if dot == 0:
        return q_f
    else:
        q_z = (
            create_quat_from_axis_z(np.dot(rotated_axis, sub_vector))
            if dot > 0
            else create_quat_from_axis_minus_z(np.dot(rotated_axis, sub_vector))
        )
    return q_f * q_z


def get_look_quat_xy(right: np.ndarray, up: np.ndarray) -> quat.quaternion:
    # right = normalize_vector(right)
    # forward = normalize_vector(np.cross(up, right))
    # q_z = create_focus_quat_z(forward)
    # q_x = create_quat_from_axis_z(np.dot(rotated_axis_x(q_z), right))
    # return q_z * q_x
    return get_look_quat_zx(np.cross(up, right), right)
