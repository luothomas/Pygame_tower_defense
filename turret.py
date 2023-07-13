#建立砲塔
import pygame as pg
import constants as c
import math
from turret_data import TURRET_DATA

class Turret(pg.sprite.Sprite):
    def __init__(self, sprite_sheets, tile_x, tile_y):
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1#初始為一級砲塔
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None

        
        #位置變數
        self.tile_x = tile_x
        self.tile_y = tile_y
        
        #計算中心座標，手動微調
        self.x = (self.tile_x + 0.5)* c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE
        
        #動畫變數
        self.sprite_sheets = sprite_sheets
        self.animation_list = self.load_images(sprite_sheets[self.upgrade_level-1])
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()

        #動畫更新
        self.angle = 90
        self.original_image = self.animation_list[self.frame_index]#若不是旋轉原圖，會因為多次的transform導致變得模糊
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #標示射程
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def load_images(self, sprite_sheet):
        
        #取得動畫圖中的各張圖片
        size = sprite_sheet.get_height()
        animation_list = []
        for x in range(c.ANIMATION_STEPS):
            temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
            animation_list.append(temp_img)
        return animation_list
    def pick_target(self, enemy_group):
        
        #尋找目標
        x_dist = 0
        y_dist = 0
        
        #逐項檢查距離判斷攻擊目標
        for enemy in enemy_group:
            if enemy.health > 0:
                x_dist = enemy.pos[0] - self.x
                y_dist = enemy.pos[1] - self.y
                dist = math.sqrt(x_dist ** 2 +  y_dist ** 2)
                if dist < self.range:
                    self.target = enemy
                    self.angle = math.degrees(math.atan2(-y_dist, x_dist))

                    #造成傷害
                    self.target.health -= c.DAMAGE * self.upgrade_level
                    break
                
        
    def update(self, enemy_group, world):
        
        #當鎖定目標後，播放射擊動畫
        if self.target:
            self.play_animation()
        else:    
            if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
                self.pick_target(enemy_group)

    def play_animation(self):
        
        #更新圖像
        self.original_image = self.animation_list[self.frame_index]
        
        #確保frame rate(針對動畫)穩定
        if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                self.last_shot = pg.time.get_ticks()
                self.target = None
    def upgrade(self):
        self.upgrade_level += 1
        self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
        self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
        
        #升級時變更圖像
        self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
        self.original_image = self.animation_list[self.frame_index]
        #標示升級射程(透明)
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center
        

    def draw(self, surface):
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)
                
