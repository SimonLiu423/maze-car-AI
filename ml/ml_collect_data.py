import copy
import os
import time
import pickle
import sys
import numpy as np
from enum import IntEnum


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

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the action according to the received scene information
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

        # Ignore first 5 frames for incorrect sensor values
        if self.f_sensor_value == -1:
            self.set_action(0, 0)
            # self.record(scene_info, action)
            self.update_values()
            return self.control_list

        if self.turn_cnt > 0:
            self.turn_cnt -= 1

            self.update_values()
            self.record(scene_info)
            return self.control_list
        else:
            self.set_action(255, 255)

        # if self.lt_sensor_value - self.prev_lt > 5:
        if self.lt_sensor_value > 25:
            self.set_action(35, 255)
            self.turn_cnt = 0

        if self.f_sensor_value < 10:
            self.set_action(255, -255)
            self.turn_cnt = 0

        self.update_values()
        self.record(scene_info)
        return self.control_list

    def set_action(self, left_speed, right_speed):
        self.control_list["left_PWM"] = left_speed
        self.control_list["right_PWM"] = right_speed
        pass

    def update_values(self):
        self.prev_lt = self.lt_sensor_value
        self.prev_rt = self.rt_sensor_value

        return

    def record(self, scene_info_dict: dict):
        """
        Record the scene information and the action
        The received scene information will be stored in a list.
        """
        control = copy.deepcopy(self.control_list)
        self._game_progress["scene_info"].append(scene_info_dict)
        self._game_progress["action"].append(control)

    def flush_to_file(self, map_idx, frame_used):
        """
        Flush the stored objects to the file
        """
        filename = "{}_{}frame_".format(map_idx, frame_used) + time.strftime("%m%d_%H-%M-%S") + ".pickle"
        if not os.path.exists(os.path.dirname(__file__) + "/log"):
            os.makedirs(os.path.dirname(__file__) + "/log")
        filepath = os.path.join(os.path.dirname(__file__), "./log/" + filename)
        # Write pickle file
        with open(filepath, "wb") as f:
            pickle.dump(self._game_progress, f)

        # Clear list
        self._game_progress["scene_info"].clear()
        self._game_progress["action"].clear()

    def reset(self):
        """
        Reset the status
        """
        print(self._game_progress)
        self.flush_to_file(4, self.frame)
        self.data_needed -= 1
        if self.data_needed == 0:
            sys.exit(1)
        pass
