import pygame
from .mazeMode import PlayingMode
from .env import *
from .sound_controller import *

'''need some fuction same as arkanoid which without dash in the name of fuction'''


class MazeCar:
    def __init__(self, user_num, game_type, map, time, sound):
        self.ranked_score = {"1P": 0, "2P": 0, "3P": 0, "4P": 0, "5P": 0, "6P": 0}  # 積分
        self.maze_id = map - 1
        self.game_end_time = time
        self.is_sound = sound
        self.sound_controller = SoundController(self.is_sound)
        self.game_mode = PlayingMode(user_num, map, time, self.sound_controller)
        self.game_type = "MAZE"
        self.user_num = user_num

    def get_player_scene_info(self):
        scene_info = self.get_scene_info
        player_info = {}
        for car in self.game_mode.car_info:
            # type of car is dictionary
            player_info["ml_" + str(car["id"] + 1) + "P"] = {"frame": scene_info["frame"],
                                                             "status": scene_info["status"],
                                                             "R_sensor": car["r_sensor_value"],
                                                             "L_sensor": car["l_sensor_value"],
                                                             "F_sensor": car["f_sensor_value"], }

        return player_info

    def update(self, commands):
        self.game_mode.handle_event()
        self.game_mode.detect_collision()
        self.game_mode.update_sprite(commands)
        self.draw()
        if not self.isRunning():
            return "QUIT"

    def reset(self):
        for key in self.game_mode.ranked_score.keys():
            self.ranked_score[key] += self.game_mode.ranked_score[key]
        print(self.ranked_score)
        self.game_mode = PlayingMode(user_num, map, time, self.sound_controller)

    def isRunning(self):
        return self.game_mode.isRunning()

    def draw(self):
        self.game_mode.draw_bg()
        self.game_mode.drawWorld()
        self.game_mode.flip()

    @property
    def get_scene_info(self):
        """
        Get the scene information
        """
        scene_info = {
            "frame": self.game_mode.frame,
            "status": self.game_mode.status,
        }
        for car in self.game_mode.car_info:
            # type of car is dictionary
            scene_info[str(car["id"]) + "P_position"] = car["vertices"]
        return scene_info

    def get_game_info(self):
        """
        Get the scene and object information for drawing on the web
        """
        wall_vertices = []
        for wall in Maze[self.maze_id]:
            vertices = []
            for vertice in wall:
                vertices.append(
                    (vertice[0] * PPM * self.game_mode.size, HEIGHT - vertice[1] * PPM * self.game_mode.size))
            wall_vertices.append(vertices)
        game_info = {
            "scene": {
                "size": [WIDTH, HEIGHT],
                "walls": wall_vertices  #
            },
            "game_object": [
                {"name": "player1_car", "size": self.game_mode.car.size, "color": RED, "image": "car_01.png"},
                {"name": "player2_car", "size": self.game_mode.car.size, "color": GREEN, "image": "car_02.png"},
                {"name": "player3_car", "size": self.game_mode.car.size, "color": BLUE, "image": "car_03.png"},
                {"name": "player4_car", "size": self.game_mode.car.size, "color": YELLOW, "image": "car_04.png"},
                {"name": "player5_car", "size": self.game_mode.car.size, "color": BROWN, "image": "car_05.png"},
                {"name": "player6_car", "size": self.game_mode.car.size, "color": PINK, "image": "car_06.png"},
                {"name": "info", "size": (306, 480), "color": WHITE, "image": "info.png"},
            ],
            "images": ["car_01.png", "car_02.png", "car_03.png", "car_04.png", "car_05.png", "car_06.png", "info.png",
                       ]
        }
        return game_info

    def _progress_dict(self, pos_left=None, pos_top=None, vertices=None, size=None, color=None, image=None, angle=None,
                       center=None):
        '''
        :return:Dictionary for game_progress
        '''
        object = {}
        if pos_left != None and pos_top != None:
            object["pos"] = [pos_left, pos_top]
        if vertices != None:
            object["vertices"] = vertices
        if size != None:
            object["size"] = size
        if color != None:
            object["color"] = color
        if image != None:
            object["image"] = image
        if angle != None:
            object["angle"] = angle
        if center != None:
            object["center"] = center

        return object

    def get_game_progress(self):
        """
        Get the position of game objects for drawing on the web
        """
        scene_info = self.get_scene_info
        game_progress = {
            "game_object": {"info": [self._progress_dict(507, 20)], },
            "game_user_information": []
        }
        for user in self.game_mode.car_info:
            user_information = {"right_sensor_value": user["r_sensor_value"],
                                "left_sensor_value": user["l_sensor_value"],
                                "front_sensor_value": user["f_sensor_value"], }
            game_progress["game_user_information"].append(user_information)
            game_progress["game_object"]["player" + str(user["id"] + 1) + "_car"] = [
                self._progress_dict(vertices=user["vertices"], angle=user["angle"], center=user["center"])]
        return game_progress

        pass

    def get_game_result(self):
        """
        Get the game result for the web
        """
        scene_info = self.get_scene_info
        result = self.game_mode.result

        return {"used_frame": scene_info["frame"],
                "result": result}

        pass

    def get_keyboard_command(self):
        """
        Get the command according to the pressed keys
        """
        key_pressed_list = pygame.key.get_pressed()
        cmd_1P = [{"left_PWM": 0, "right_PWM": 0}]
        cmd_2P = [{"left_PWM": 0, "right_PWM": 0}]

        if key_pressed_list[pygame.K_UP]:
            cmd_1P[0]["left_PWM"] = 75
            cmd_1P[0]["right_PWM"] = 75
        if key_pressed_list[pygame.K_DOWN]:
            cmd_1P[0]["left_PWM"] = -75
            cmd_1P[0]["right_PWM"] = -75
        if key_pressed_list[pygame.K_LEFT]:
            cmd_1P[0]["right_PWM"] += 75
        if key_pressed_list[pygame.K_RIGHT]:
            cmd_1P[0]["left_PWM"] += 75

        if key_pressed_list[pygame.K_w]:
            cmd_2P[0]["left_PWM"] = 75
            cmd_2P[0]["right_PWM"] = 75
        if key_pressed_list[pygame.K_s]:
            cmd_2P[0]["left_PWM"] = -75
            cmd_2P[0]["right_PWM"] = -75
        if key_pressed_list[pygame.K_a]:
            cmd_2P[0]["right_PWM"] += 75
        if key_pressed_list[pygame.K_d]:
            cmd_2P[0]["left_PWM"] += 75

        return {"ml_1P": cmd_1P,
                "ml_2P": cmd_2P}

# if __name__ == "__main__":
#     game=MazeCar(1,"NORMAL",1,"off")
#     print(game.get_game_progress())
