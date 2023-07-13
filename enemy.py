import pygame as pg
from pygame.math import Vector2
from enemy_data import ENEMY_DATA
import constants as c
import math

class Enemy(pg.sprite.Sprite):
  def __init__(self, enemy_type, waypoints, images):
    pg.sprite.Sprite.__init__(self)
    self.waypoints = waypoints
    self.pos = Vector2(self.waypoints[0])
    self.target_waypoint = 1
    self.health = ENEMY_DATA.get(enemy_type)["health"]
    self.speed = ENEMY_DATA.get(enemy_type)["speed"]
    self.angle = 0
    self.original_image = images.get(enemy_type)
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

  def update(self, world):
    self.move(world)
    self.rotate()
    self.check_alive(world)

  def move(self, world):
    #設定紀錄點
    if self.target_waypoint < len(self.waypoints):
      self.target = Vector2(self.waypoints[self.target_waypoint])
      self.movement = self.target - self.pos
    else:
      #如果走到終點則刪除物件
      self.kill()
      world.health -= 1
      world.missed_enemies += 1

    #計算目標與當前位置距離
    dist = self.movement.length()
    
    if dist >= (self.speed * world.game_speed):
      self.pos += self.movement.normalize() * (self.speed * world.game_speed)
    else:
      if dist != 0:#如果距離等於零，會無法標準化
        self.pos += self.movement.normalize() * dist
      self.target_waypoint += 1

  def rotate(self):
    dist = self.target - self.pos
    #計算旋轉角度
    self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
    #旋轉圖像和外框
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

  def check_alive(self, world):
    if self.health <= 0:
      world.killed_enemies += 1
      world.money += c.KILL_REWARD
      self.kill()
    
