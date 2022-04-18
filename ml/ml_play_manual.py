import pygame


class MLPlay:
    def __init__(self, player):
        self.player_no = player[6]
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.control_list = [{"left_PWM" : 0, "right_PWM" : 0}]
        # print("Initial ml script")

    def update(self, scene_info: dict,keyboard:list=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"
        if pygame.K_w in keyboard:
            self.control_list[0]["left_PWM"] = 200
            self.control_list[0]["right_PWM"] = 200
        elif pygame.K_a in keyboard:
            self.control_list[0]["left_PWM"] = -150
            self.control_list[0]["right_PWM"] = 150
        elif pygame.K_d in keyboard:
            self.control_list[0]["left_PWM"] = 150
            self.control_list[0]["right_PWM"] = -150
        elif pygame.K_s in keyboard:
            self.control_list[0]["left_PWM"] = -150
            self.control_list[0]["right_PWM"] = -150
        else:

            self.control_list[0]["left_PWM"] = 100
            self.control_list[0]["right_PWM"] = 100

        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        pass