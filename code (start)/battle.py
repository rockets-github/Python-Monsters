from settings import *
from sprite import (
    MonsterSprite,
    MonsterNameSprite,
    MonsterLevelSprite,
    MonsterStatsSprite,
    MonsterOutlineSprite,
)
from groups import BattleSprites
from game_data import ATTACK_DATA
from support import draw_bar


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

        self.current_monster = None
        self.selection_mode = None
        self.selection_side = "player"
        self.indexes = {
            "general": 0,
            "monster": 0,
            "attacks": 0,
            "switch": 0,
            "target": 0,
        }
        self.setup()

    def setup(self):
        for entity, monster in self.monster_data.items():
            for index, monster in {k: v for k, v in monster.items() if k <= 2}.items():
                self.create_monster(monster, index, index, entity)

    def create_monster(self, monster, index, pos_index, entity):
        frames = self.monster_frames["monsters"][monster.name]
        outline_frames = self.monster_frames["outlines"][monster.name]
        if entity == "player":
            pos = list(BATTLE_POSITIONS["left"].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            frames = {
                state: [pygame.transform.flip(frame, True, False) for frame in frames]
                for state, frames in frames.items()
            }
            outline_frames = {
                state: [pygame.transform.flip(frames, True, False) for frames in frames]
                for state, frames in outline_frames.items()
            }
        else:
            pos = list(BATTLE_POSITIONS["right"].values())[pos_index]
            groups = (self.battle_sprites, self.opponent_sprites)

        monster_sprite = MonsterSprite(
            pos, frames, groups, monster, index, pos_index, entity
        )

        MonsterOutlineSprite(monster_sprite, self.battle_sprites, outline_frames)

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

    def input(self):
        if self.selection_mode and self.current_monster:
            keys = pygame.key.get_just_pressed()

            match self.selection_mode:
                case "general":
                    limiter = len(BATTLE_CHOICES["full"])
                case "attacks":
                    limiter = len(self.current_monster.monster.get_abilities(all=False))
                case "switch":
                    limiter = len(self.available_monsters)

            if keys[pygame.K_DOWN]:
                self.indexes[self.selection_mode] = (
                    self.indexes[self.selection_mode] + 1
                ) % limiter
            if keys[pygame.K_UP]:
                self.indexes[self.selection_mode] = (
                    self.indexes[self.selection_mode] - 1
                ) % limiter
            if keys[pygame.K_SPACE]:
                if self.selection_mode == "general":
                    match self.indexes["general"]:
                        case 0:
                            self.selection_mode = "attacks"

                        case 1:
                            self.update_all_monsters("resume")
                            self.current_monster, self.selection_mode = None, None
                            self.indexes["general"] = 0
                        case 2:
                            self.selection_mode = "switch"
                        case 3:
                            print("attack")

            if keys[pygame.K_ESCAPE]:
                if self.selection_mode in ("attacks", "switch", "target"):
                    self.selection_mode = "general"

    def check_active(self):
        for monster_sprite in (
            self.player_sprites.sprites() + self.opponent_sprites.sprites()
        ):
            if monster_sprite.monster.initiative >= 100:
                self.update_all_monsters("pause")
                monster_sprite.monster.initiative = 0
                monster_sprite.set_highlight(True)
                self.current_monster = monster_sprite
                if self.player_sprites in monster_sprite.groups():
                    self.selection_mode = "general"

    def update_all_monsters(self, option):
        for monster_sprite in (
            self.player_sprites.sprites() + self.opponent_sprites.sprites()
        ):
            monster_sprite.monster.pause = True if option == "pause" else False

    def draw_ui(self):
        if self.current_monster:
            match self.selection_mode:
                case "general":
                    self.draw_general()
                case "attacks":
                    self.draw_attacks()
                case "switch":
                    self.draw_switch()

    def draw_general(self):
        for index, (option, data_dict) in enumerate(BATTLE_CHOICES["full"].items()):
            if index == self.indexes["general"]:
                surf = self.monster_frames["ui"][f"{data_dict['icon']}_highlight"]
            else:
                surf = pygame.transform.grayscale(
                    self.monster_frames["ui"][data_dict["icon"]]
                )
            rect = surf.get_frect(
                center=self.current_monster.rect.midright + data_dict["pos"]
            )
            self.display_surface.blit(surf, rect)

    def draw_attacks(self):
        # data
        abilities = self.current_monster.monster.get_abilities(all=False)
        width, height = 150, 200
        visible_attacks = 4
        item_height = height / visible_attacks
        v_offset = (
            0
            if self.indexes["attacks"] < visible_attacks
            else -(self.indexes["attacks"] - visible_attacks + 1) * item_height
        )

        # bg
        bg_rect = pygame.FRect((0, 0), (width, height)).move_to(
            midleft=self.current_monster.rect.midright + vector(20, 0)
        )
        pygame.draw.rect(self.display_surface, COLORS["white"], bg_rect, 0, 5)

        for index, ability in enumerate(abilities):
            selected = index == self.indexes["attacks"]

            if selected:
                element = ATTACK_DATA[ability]["element"]
                text_color = COLORS[element] if element != "normal" else COLORS["black"]
            else:
                text_color = COLORS["light"]
            text_surf = self.fonts["regular"].render(ability, False, text_color)

            text_rect = text_surf.get_frect(
                center=bg_rect.midtop
                + vector(0, item_height / 2 + index * item_height + v_offset)
            )
            text_bg_rect = pygame.FRect((0, 0), (width, item_height)).move_to(
                center=text_rect.center
            )

            if bg_rect.collidepoint(text_rect.center):
                if selected:
                    if text_bg_rect.collidepoint(bg_rect.topleft):
                        pygame.draw.rect(
                            self.display_surface,
                            COLORS["dark white"],
                            text_bg_rect,
                            0,
                            0,
                            5,
                            5,
                        )
                    elif text_bg_rect.collidepoint(bg_rect.midbottom + vector(0, -1)):
                        pygame.draw.rect(
                            self.display_surface,
                            COLORS["dark white"],
                            text_bg_rect,
                            0,
                            0,
                            0,
                            0,
                            5,
                            5,
                        )
                    else:
                        pygame.draw.rect(
                            self.display_surface, COLORS["dark white"], text_bg_rect
                        )
                self.display_surface.blit(text_surf, text_rect)

    def draw_switch(self):
        width, height = 300, 320
        visible_monsters = 4
        item_height = height / visible_monsters
        v_offset = (
            0
            if self.indexes["switch"] < visible_monsters
            else -(self.indexes["switch"] - visible_monsters + 1) * item_height
        )
        bg_rect = pygame.FRect((0, 0), (width, height)).move_to(
            midleft=self.current_monster.rect.midright + vector(20, 0)
        )

        pygame.draw.rect(self.display_surface, COLORS["white"], bg_rect, 0, 5)

        # monsters
        active_monsters = [
            (monster_sprite.index, monster_sprite.monster)
            for monster_sprite in self.player_sprites
        ]
        self.available_monsters = {
            index: monster
            for index, monster in self.monster_data["player"].items()
            if (index, monster) not in active_monsters and monster.health > 0
        }

        for index, monster in enumerate(self.available_monsters.values()):
            selected = index == self.indexes["switch"]
            item_bg_rect = pygame.FRect((0, 0), (width, height)).move_to(
                midleft=(
                    bg_rect.left,
                    bg_rect.top + item_height / 2 + index * item_height + v_offset,
                )
            )
            icon_surf = self.monster_frames["icons"][monster.name]
            icon_rect = icon_surf.get_frect(
                midleft=bg_rect.topleft
                + vector(10, item_height / 2 + index * item_height + v_offset)
            )
            text_surf = self.fonts["regular"].render(
                f"{monster.name} ({monster.level})",
                False,
                COLORS["red"] if selected else COLORS["black"],
            )
            text_rect = text_surf.get_frect(topleft=(bg_rect.left + 90, icon_rect.top))

            # selection bg
            if selected:
                if item_bg_rect.collidepoint(bg_rect.topleft):
                    pygame.draw.rect(
                        self.display_surface,
                        COLORS["dark white"],
                        item_bg_rect,
                        0,
                        0,
                        5,
                        5,
                    )
                elif item_bg_rect.collidepoint(bg_rect.midbottom + vector(0, -1)):
                    pygame.draw.rect(
                        self.display_surface,
                        COLORS["dark white"],
                        item_bg_rect,
                        0,
                        0,
                        0,
                        0,
                        5,
                        5,
                    )

                else:
                    pygame.draw.rect(
                        self.display_surface,
                        COLORS["dark white"],
                        item_bg_rect,
                    )
            if bg_rect.collidepoint(item_bg_rect.center):
                for surf, rect in ((icon_surf, icon_rect), (text_surf, text_rect)):
                    self.display_surface.blit(surf, rect)
                health_rect = pygame.FRect(
                    (text_rect.bottomleft + vector(0, 4)), (100, 4)
                )
                energy_rect = pygame.FRect(
                    (health_rect.bottomleft + vector(0, 2)), (80, 4)
                )
                draw_bar(
                    self.display_surface,
                    health_rect,
                    monster.health,
                    monster.get_stat("max_health"),
                    COLORS["red"],
                    COLORS["black"],
                )
                draw_bar(
                    self.display_surface,
                    energy_rect,
                    monster.energy,
                    monster.get_stat("max_energy"),
                    COLORS["blue"],
                    COLORS["black"],
                )

    def update(self, dt):
        self.input()
        self.battle_sprites.update(dt)
        self.check_active()

        self.display_surface.blit(self.bg_surg, (0, 0))
        self.battle_sprites.draw(self.current_monster)
        self.draw_ui()
