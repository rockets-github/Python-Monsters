from settings import *
from pytmx.util_pygame import load_pygame
from pathlib import Path

from sprite import Sprite, AnimatedSprite
from entities import Player
from groups import AllSprites

from support import *


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Monster Hunter")

        self.clock = pygame.Clock()

        # group
        self.all_sprites = AllSprites()

        self.import_asset()
        self.set_up(self.tmx_maps["world"], "house")

    def import_asset(self):
        self.tmx_maps = {
            "world": load_pygame(
                Path.joinpath(Path(__file__).parents[1], "data", "maps", "world.tmx")
            ),
            "hospital": load_pygame(
                Path.joinpath(Path(__file__).parents[1], "data", "maps", "hospital.tmx")
            ),
        }
        self.overworld_frames = {
            "water": import_folder(
                Path.joinpath(
                    Path(__file__).parents[1], "graphics", "tilesets", "water"
                )
            ),
            "coast": coast_importer(
                24,
                12,
                Path.joinpath(
                    Path(__file__).parents[1], "graphics", "tilesets", "coast"
                ),
            ),
        }
        print(self.overworld_frames["coast"])

    def set_up(self, tmx_map, player_start_pos):
        # water
        for obj in tmx_map.get_layer_by_name("Water"):
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite(
                        (x, y), self.overworld_frames["water"], self.all_sprites
                    )

        # terrain
        for layer in ["Terrain", "Terrain Top"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # entities
        for obj in tmx_map.get_layer_by_name("Entities"):
            if obj.name == "Player" and obj.properties["pos"] == player_start_pos:
                self.player = Player((obj.x, obj.y), self.all_sprites)

        # objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            Sprite((obj.x, obj.y), obj.image, self.all_sprites)

        # coast

    def run(self):
        while True:
            # frame rate
            dt = self.clock.tick() / 1000

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # game logic
            self.all_sprites.update(dt)

            self.display_surface.fill("black")
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
