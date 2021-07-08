import pygame
from game_core import MazeCar, gameView
from mlgame.view.view import PygameView
from mlgame.gamedev.generic import quit_or_esc

if __name__ == '__main__':
    pygame.init()
    game = MazeCar.MazeCar(2, "MAZE",4, 120, 5, "off")
    # game = MazeCar.MazeCar(1, "MOVE_MAZE", 4, 120, 3, "off")
    # game = MazeCar.MazeCar(1, "PRACTICE", 6, 120, 5, "off")
    scene_init_info_dict = game.get_scene_init_data()
    game_view = PygameView(scene_init_info_dict)
    interval = 1 / 30
    frame_count = 0

    while game.is_running and not quit_or_esc():
        game.update(game.get_keyboard_command())
        game_progress_data = game.get_scene_progress_data()
        game_view.draw_screen()
        game_view.draw(game_progress_data)
        game_view.flip()
        frame_count += 1

    pygame.quit()
