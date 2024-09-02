import sys
from settings import *
from support import *
from game.sprites import Generic, Animated, Particle, Coin, Spikes, Tooth, Shell, Block, Player
from pygame.math import Vector2 as vector


class Level:
    def __init__(self, grid, switch, asset_dict):
        self.display_surface = pygame.display.get_surface()
        self.switch = switch

        # groups
        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.build_level(grid, asset_dict)

        self.particle_surfs = asset_dict['particle']

    def build_level(self, grid, asset_dict):
        for layer_name, layer in grid.items():
            for pos, data in layer.items():
                if layer_name == 'terrain':
                    Generic(pos, asset_dict['land'][data], [self.all_sprites, self.collision_sprites])
                if layer_name == 'water':
                    if data == 'top':
                        Animated(pos, asset_dict['water top'], self.all_sprites, LEVEL_LAYERS['water'])
                    else:
                        Generic(pos, asset_dict['water bottom'], self.all_sprites, LEVEL_LAYERS['water'])

                match data:
                    case 0: self.player = Player(pos, asset_dict['player'], self.all_sprites, self.collision_sprites)

                    # coins
                    case 4: Coin('gold', pos, asset_dict['gold'], [self.all_sprites, self.coin_sprites])
                    case 5: Coin('silver', pos, asset_dict['silver'], [self.all_sprites, self.coin_sprites])
                    case 6: Coin('diamond', pos, asset_dict['diamond'], [self.all_sprites, self.coin_sprites])

                    # enemies
                    case 7: Spikes(pos, asset_dict['spikes'], [self.all_sprites, self.damage_sprites])
                    case 8: Tooth(pos, asset_dict['tooth'], [self.all_sprites, self.damage_sprites])
                    case 9: Shell('left', pos, asset_dict['shell'], [self.all_sprites, self.collision_sprites])
                    case 10: Shell('right', pos, asset_dict['shell'], [self.all_sprites, self.collision_sprites])

                    # palm trees
                    case 11:
                        Animated(pos, asset_dict['palms']['small_fg'], self.all_sprites)
                        Block(pos, (76, 50), self.collision_sprites)
                    case 12:
                        Animated(pos, asset_dict['palms']['large_fg'], self.all_sprites)
                        Block(pos, (76, 50), self.collision_sprites)
                    case 13:
                        Animated(pos, asset_dict['palms']['left_fg'], self.all_sprites)
                        Block(pos, (76, 50), self.collision_sprites)
                    case 14:
                        Animated(pos, asset_dict['palms']['right_fg'], self.all_sprites)
                        Block(pos + vector(50, 0), (76, 50), [self.all_sprites, self.collision_sprites])
                    case 15: Animated(pos, asset_dict['palms']['small_bg'], self.all_sprites, LEVEL_LAYERS['bg'])
                    case 16: Animated(pos, asset_dict['palms']['large_bg'], self.all_sprites, LEVEL_LAYERS['bg'])
                    case 17: Animated(pos, asset_dict['palms']['left_bg'], self.all_sprites, LEVEL_LAYERS['bg'])
                    case 18: Animated(pos, asset_dict['palms']['right_bg'], self.all_sprites, LEVEL_LAYERS['bg'])

    def get_coins(self):
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)
        for sprite in collided_coins:
            Particle(sprite.rect.center, self.particle_surfs, self.all_sprites)

    def run(self, dt):
        self.event_loop()
        self.all_sprites.update(dt)
        self.get_coins()

        self.display_surface.fill(SKY_COLOUR)
        self.all_sprites.custom_draw(self.player)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2
        for sprite in self:
            for layer in LEVEL_LAYERS.values():
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
