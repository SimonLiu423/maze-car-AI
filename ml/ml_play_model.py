import os
import pickle
import numpy as np
from enum import IntEnum


class Action(IntEnum):
    STRAIGHT = 0
    LEFT = 1
    RIGHT = 2


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.player_no = ai_name
        self.frame = 0
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.lt_sensor_value = 0
        self.rt_sensor_value = 0
        self.angle = 0
        self.x = 0
        self.y = 0
        self.prev_lt = 0
        self.prev_rt = 0
        self.turn_cnt = 0
        self.direction = "front"
        self.control_list = {"left_PWM": 0, "right_PWM": 0}
        self._game_progress = {
            "scene_info": [],
            "action": [],
        }
        self.data_needed = 8
        with open(os.path.join(os.path.dirname(__file__), 'save', 'model.pickle'), 'rb') as f:
            self.model = pickle.load(f)

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        # get scene values
        self.frame = scene_info["frame"]
        self.f_sensor_value = scene_info["F_sensor"]
        self.l_sensor_value = scene_info["L_sensor"]
        self.r_sensor_value = scene_info["R_sensor"]
        self.lt_sensor_value = scene_info["L_T_sensor"]
        self.rt_sensor_value = scene_info["R_T_sensor"]
        self.angle = scene_info["angle"]
        self.x = scene_info["x"]
        self.y = scene_info["y"]

        if self.f_sensor_value == -1:
            self.set_action(0, 0)
            return self.control_list

        X = np.array(
            [self.f_sensor_value, self.l_sensor_value, self.r_sensor_value, self.lt_sensor_value,
             self.rt_sensor_value]).reshape(1, -1)
        Y = self.model.predict(X).squeeze()

        self.control_list["left_PWM"] = Y[0]
        self.control_list["right_PWM"] = Y[1]
        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        pass

    def set_action(self, left_speed, right_speed):
        self.control_list["left_PWM"] = left_speed
        self.control_list["right_PWM"] = right_speed
        pass

    def update_values(self):
        # self.prev_pos = [self.x, self.y]
        pass
