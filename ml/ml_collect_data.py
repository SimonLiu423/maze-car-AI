class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.player_no = ai_name
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
        self.turn_threshold = 3
        self.angle_threshold = 10
        self.dead_end_threshold = 10
        self.target_angle = -1

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        # Ignore first 5 frames for incorrect sensor values
        if scene_info["frame"] < 5:
            self.set_action(255, 255)
            self.update_values()
            return self.control_list

        # get scene values
        self.f_sensor_value = scene_info["F_sensor"]
        self.l_sensor_value = scene_info["L_sensor"]
        self.r_sensor_value = scene_info["R_sensor"]
        self.lt_sensor_value = scene_info["L_T_sensor"]
        self.rt_sensor_value = scene_info["R_T_sensor"]
        self.angle = scene_info["angle"]
        self.x = scene_info["x"]
        self.y = scene_info["y"]

        # turn if target_angle is set
        if self.target_angle != -1:
            # continue if angle is about correct
            if abs(self.angle - self.target_angle) < self.angle_threshold:
                self.target_angle = -1
            else:
                self.set_action(100, -100)  # Turn clockwise
                self.update_values()
                return self.control_list

        # stuck detect
        if self.is_stuck():
            self.stuck_cnt += 1
        else:
            self.stuck_cnt = 0
        # handle stuck
        if self.stuck_cnt > self.stuck_cnt_threshold:
            self.target_angle = (self.angle - 90 + 360) % 360
            self.stuck_cnt = 0

        # handle dead end
        if self.f_sensor_value < self.dead_end_threshold:
            self.target_angle = (self.angle - 90 + 360) % 360
            self.stuck_cnt = 0

        # keeping left front sensor & right front sensor values about the same
        if self.lt_sensor_value - self.rt_sensor_value > self.turn_threshold:
            self.set_action(10, 255)    # Move left
        elif self.rt_sensor_value - self.lt_sensor_value > self.turn_threshold:
            self.set_action(255, 10)    # Move right
        else:
            self.set_action(255, 255)

        # update values
        self.update_values()

        return self.control_list

    def set_action(self, l_pwm, r_pwm):
        self.control_list["left_PWM"] = l_pwm
        self.control_list["right_PWM"] = r_pwm

    def update_values(self):
        self.prev_pos = [self.x, self.y]
    def is_stuck(self):
        return abs(self.x - self.prev_pos[0]) < 0.5 and abs(self.y - self.prev_pos[1]) < 0.5

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        pass
