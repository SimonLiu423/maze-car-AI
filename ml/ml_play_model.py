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
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.angle = 0
        self.x = 0
        self.y = 0
        self.stuck_cnt = 0
        self.target_angle = -1
        self.direction = -1
        self.ang_diff = 0
        self.angle_threshold = 0.5
        self.control_list = {"left_PWM": 0, "right_PWM": 0}
        self.prev_pos = [-1, -1]
        self.action_angle = [0, 90, -90]
        with open(os.path.join(os.path.dirname(__file__), 'save', 'model.pickle'), 'rb') as f:
            self.model = pickle.load(f)

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        # Ignore first 5 frames for incorrect sensor values
        if scene_info["frame"] < 5:
            self.control_list["left_PWM"] = 255
            self.control_list["right_PWM"] = 255
            return self.control_list

        self.f_sensor_value = scene_info["F_sensor"]
        self.l_sensor_value = scene_info["L_sensor"]
        self.r_sensor_value = scene_info["R_sensor"]
        self.angle = scene_info["angle"]
        self.x = scene_info["x"]
        self.y = scene_info["y"]

        # turn if target_angle is set
        if self.target_angle != -1:
            self.angle_diff()
            # continue if angle is about correct
            if self.ang_diff < self.angle_threshold:
                self.target_angle = -1
            else:
                if self.direction == 0:
                    action = Action.LEFT
                else:
                    action = Action.RIGHT

                self.set_action(action)
                return self.control_list

        # stuck detect
        if self.is_stuck():
            self.stuck_cnt += 1
        else:
            self.stuck_cnt = 0

        # x = np.array([self.f_sensor_value, self.l_sensor_value, self.r_sensor_value, self.angle, self.target_angle,
        #               self.stuck_cnt, self.direction, self.ang_diff]).reshape(1, -1)
        x = np.array([self.f_sensor_value, self.l_sensor_value, self.r_sensor_value, self.angle]).reshape(1, -1)
        action = self.model.predict(x).reshape(-1, )[0]
        print(action)

        if action != Action.STRAIGHT:
            self.target_angle = (self.angle + self.action_angle[action] + 360) % 360

        self.set_action(action)

        print(self.control_list)

        self.update_values()
        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        pass

    def set_action(self, action):
        if action == Action.STRAIGHT:
            self.control_list["left_PWM"] = 255
            self.control_list["right_PWM"] = 255
        else:
            self.angle_diff()
            speed = self.turn_speed(self.ang_diff)
            if action == Action.LEFT:
                self.control_list["left_PWM"] = -speed
                self.control_list["right_PWM"] = speed
            else:
                self.control_list["left_PWM"] = speed
                self.control_list["right_PWM"] = -speed

    def angle_diff(self):
        diff = self.target_angle - self.angle

        if diff > 0:
            if diff < 180:
                self.direction = 0
                self.ang_diff = diff
            else:
                self.direction = 1
                self.ang_diff = 360 - diff
        else:
            if abs(diff) < 180:
                self.direction = 1
                self.ang_diff = abs(diff)
            else:
                self.direction = 0
                self.ang_diff = 360 - abs(diff)
        return

    def turn_speed(self, angle_diff):
        a = 255 / (180 ** 2)
        speed = a * angle_diff ** 2
        print("Turn speed: {}".format(speed))
        return speed

    def update_values(self):
        # self.prev_pos = [self.x, self.y]
        pass

    def is_stuck(self):
        return abs(self.x - self.prev_pos[0]) < 0.5 and abs(self.y - self.prev_pos[1]) < 0.5
