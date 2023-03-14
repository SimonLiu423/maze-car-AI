import os
import time
import pickle
import sys
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
        self.control_list = {"left_PWM": 0, "right_PWM": 0}
        self.prev_pos = [-1, -1]
        self.stuck_cnt = 0
        self.stuck_cnt_threshold = 30
        self.stuck = False
        self.gap_threshold = 20
        self.sensor_threshold = 3
        self.angle_threshold = 0.5
        self.dead_end_threshold = 10
        self.target_angle = -1
        self.direction = 0
        self.ang_diff = 0
        self._game_progress = {
            "scene_info": [],
            "action": [],
        }
        self.data_needed = 100
        self.action_angle = [0, 90, -90]
        self.action_prob = [0.95, 0.025, 0.025]  # straight, left, right

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the action according to the received scene information
        """
        # Ignore first 5 frames for incorrect sensor values
        if scene_info["frame"] < 5:
            action = Action.STRAIGHT
            self.set_action(action)
            # self.record(scene_info, action)
            self.update_values()
            return self.control_list

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

        print("(X,Y): ({},{}), angle: {}, target angle: {}".format(self.x, self.y, self.angle, self.target_angle))

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
                # self.record(scene_info, action)
                self.update_values()
                return self.control_list

        # stuck detect
        if self.is_stuck():
            self.stuck_cnt += 1
        else:
            self.stuck_cnt = 0
        # reset if stuck
        if self.stuck_cnt > self.stuck_cnt_threshold:
            self.stuck = True
            return "RESET"

        # handle dead end
        if self.f_sensor_value < self.dead_end_threshold:
            print("Dead end, ", end='')
            if abs(self.l_sensor_value - self.r_sensor_value) < self.sensor_threshold:
                # Randomly turning left or right
                action = np.random.choice([Action.LEFT, Action.RIGHT], p=[0.5, 0.5])
                self.target_angle = (self.angle + self.action_angle[action] + 360) % 360
                self.set_action(action)
                print("going straight")

            elif self.l_sensor_value > self.r_sensor_value:
                action = Action.LEFT
                self.target_angle = (self.angle + self.action_angle[action] + 360) % 360
                self.set_action(action)
                print("turning left")
            else:
                action = Action.RIGHT
                self.target_angle = (self.angle + self.action_angle[action] + 360) % 360
                self.set_action(action)
                print("turning right")

            self.record(scene_info, action)
            self.update_values()
            return self.control_list

        # Turn if left or right sensor value > gap_threshold with prob
        if self.l_sensor_value > self.gap_threshold and np.random.uniform() < self.action_prob[Action.LEFT]:
            action = Action.LEFT
            self.target_angle = (self.angle + self.action_angle[Action.LEFT] + 360) % 360
            self.set_action(Action.LEFT)
            print("Turning Left")
        elif self.r_sensor_value > self.gap_threshold and np.random.uniform() < self.action_prob[Action.RIGHT]:
            action = Action.RIGHT
            self.target_angle = (self.angle + self.action_angle[Action.RIGHT] + 360) % 360
            self.set_action(Action.RIGHT)
            print("Turning Right")
        else:
            action = Action.STRAIGHT
            self.set_action(Action.STRAIGHT)
            print("Moving Forward")

        self.record(scene_info, action)
        self.update_values()

        return self.control_list

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

    def update_values(self):
        self.prev_pos = [self.x, self.y]

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
        speed = (1 / (1 + np.exp(-(angle_diff / 255 * 20) + 5))) * 255
        print("Turn speed: {}".format(speed))
        return speed

    def is_stuck(self):
        return abs(self.x - self.prev_pos[0]) < 0.5 and abs(self.y - self.prev_pos[1]) < 0.5

    def record(self, scene_info_dict: dict, action: Action):
        """
        Record the scene information and the action
        The received scene information will be stored in a list.
        """
        scene_info_dict["stuck_cnt"] = self.stuck_cnt
        if self.target_angle != -1:
            scene_info_dict["target_angle"] = self.target_angle
            scene_info_dict["direction"] = self.direction
            scene_info_dict["angle_diff"] = self.ang_diff
        else:
            scene_info_dict["target_angle"] = -1
            scene_info_dict["direction"] = -1
            scene_info_dict["angle_diff"] = 0
        self._game_progress["scene_info"].append(scene_info_dict)
        self._game_progress["action"].append(int(action))

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
        # Store game progress to file if not stuck
        if not self.stuck:
            self.flush_to_file(1, self.frame)

            self.data_needed -= 1
            # Exit program if data is enough
            if self.data_needed == 0:
                sys.exit()

        # Reset values
        self.prev_pos = (-1, -1)
        self.stuck_cnt = 0
        self.target_angle = -1
        self.frame = 0
        self.stuck = False
        # print("reset ml script")
        pass
