import os
import pickle
import numpy as np


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.player_no = ai_name
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor = 0
        self.lt_sensor = 0
        self.rt_sensor = 0
        self.angle = 0
        self.x = 0
        self.y = 0
        self.control_list = {"left_PWM": 0, "right_PWM": 0}
        self.prev_pos = [-1, -1]
        with open(os.path.join(os.path.dirname(__file__), 'save', 'model.pickle'), 'rb') as f:
            self.model = pickle.load(f)

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        self.f_sensor = scene_info["F_sensor"]
        self.lt_sensor = scene_info["L_T_sensor"]
        self.rt_sensor = scene_info["R_T_sensor"]
        self.x = scene_info["x"]
        self.y = scene_info["y"]

        if self.prev_pos == (-1, -1):
            dx = 0
            dy = 0
        else:
            dx = self.x - self.prev_pos[0]
            dy = self.y - self.prev_pos[1]

        x = np.array([self.x, self.y, dx, dy, self.f_sensor, self.lt_sensor, self.rt_sensor]).reshape(1, -1)
        y = self.model.predict(x).squeeze()

        self.control_list["left_PWM"] = y[0]
        self.control_list["right_PWM"] = y[1]

        print(self.control_list)

        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        pass
