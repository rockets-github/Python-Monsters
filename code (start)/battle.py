from settings import *
from sprite import (
    MonsterSprite,
    MonsterNameSprite,
    MonsterLevelSprite,
    MonsterStatsSprite,
)
from groups import BattleSprites


class Battle:
    def __init__(
        self, player_monsters, opponent_monsters, monster_frame, bg_surf, fonts
    ):
        self.display_surface = pygame.display.get_surface()
        self.bg_surg = bg_surf
        self.monster_frames = monster_frame
        self.fonts = fonts
        self.monster_data = {"player": player_monsters, "opponent": opponent_monsters}

        # groups
        self.battle_sprites = BattleSprites()
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()
        self.setup()

    def setup(self):
        for entity, monster in self.monster_data.items():
            for index, monster in {k: v for k, v in monster.items() if k <= 2}.items():
                self.create_monster(monster, index, index, entity)

    def create_monster(self, monster, index, pos_index, entity):
        frames = self.monster_frames["monsters"][monster.name]
        if entity == "player":
            pos = list(BATTLE_POSITIONS["left"].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            frames = {
                state: [pygame.transform.flip(frame, True, False) for frame in frames]
                for state, frames in frames.items()
            }
        else:
            pos = list(BATTLE_POSITIONS["right"].values())[pos_index]
            groups = (self.battle_sprites, self.opponent_sprites)

        monster_sprite = MonsterSprite(
            pos, frames, groups, monster, index, pos_index, entity
        )

        # ui
        name_pos = (
            monster_sprite.rect.midleft + vector(16, -70)
            if entity == "player"
            else monster_sprite.rect.midright + vector(-40, -70)
        )

        name_sprite = MonsterNameSprite(
            name_pos, monster_sprite, self.battle_sprites, self.fonts["regular"]
        )

        level_pos = (
            name_sprite.rect.bottomleft
            if entity == "player"
            else name_sprite.rect.bottomright
        )
        MonsterLevelSprite(
            entity, level_pos, monster_sprite, self.battle_sprites, self.fonts["small"]
        )
        MonsterStatsSprite(
            monster_sprite.rect.midbottom + vector(0, 20),
            monster_sprite,
            (150, 48),
            self.battle_sprites,
            self.fonts["small"],
        )

    def update(self, dt):
        self.display_surface.blit(self.bg_surg, (0, 0))
        self.battle_sprites.update(dt)
        self.battle_sprites.draw()
