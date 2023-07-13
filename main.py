import pygame as pg
import json
import constants as c
from enemy import Enemy
from world import World
from turret import Turret
from button import Button

#初始化
pg.init()

#創建時鐘，計FPS用
clock = pg.time.Clock()

#創建視窗
screen = pg.display.set_mode((c.WIDTH + c.SIDE_PANEL, c.HEIGHT))
pg.display.set_caption("TOWER DEFENCE")

#遊戲參數
game_over = False
game_outcome = 0#-1為失敗，1為勝利
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None

#載入圖片
#地圖
map_image = pg.image.load('levels/Map_1.png').convert_alpha()

#砲塔
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()

#砲塔動畫圖
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)

#敵人
enemy_images = {
    "weak":pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(), 
    "medium":pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
    "strong":pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
    "elite":pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha(),
    }



#按鈕
#購買砲塔按鈕
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()

#取消選定按鈕
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()

#升級砲塔按鈕
upgrade_turret_image = pg.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()

#開始按鈕
begin_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()

#重試按鈕
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()

#二倍速
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()

#GUI
heart_image = pg.image.load('assets/images/gui/heart.png').convert_alpha()
coin_image = pg.image.load('assets/images/gui/coin.png').convert_alpha()
logo_image = pg.image.load('assets/images/gui/logo.png').convert_alpha()


#製作關卡，載入json檔案
with open('levels/Map_1.tmj') as file:
    world_data = json.load(file)

#字體相關設定
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#在螢幕上印出文字
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)#將文字轉換為圖片
    screen.blit(img, (x, y))

def display_data():
    pg.draw.rect(screen, "maroon", (c.WIDTH, 0, c.SIDE_PANEL, c.HEIGHT))
    pg.draw.rect(screen, "grey0", (c.WIDTH, 0, c.SIDE_PANEL, 400), 2)
    screen.blit(logo_image, (c.WIDTH, 400))
    
    #顯示當前數據
    draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.WIDTH + 10, 10)
    draw_text(str(world.money), text_font, "grey100", c.WIDTH + 50, 70)
    draw_text(str(world.health), text_font, "grey100", c.WIDTH + 50, 40)
    screen.blit(coin_image, (c.WIDTH + 10, 65))
    screen.blit(heart_image, (c.WIDTH + 10, 35))

#架設砲塔
def create_turret(mouse_pos):
    
    #取得換算後的座標
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    
    #使用換算後的座標取得該地塊的數字(對應json檔)
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    
    #判斷是否為草地
    if world.tile_map[mouse_tile_num] == 25:
        
        #檢測當前位置是否已有砲台
        space_is_free = True
        for turret in turret_group:
            if(mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
                
        #若是空的則架設砲塔
        if space_is_free == True:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y)
            turret_group.add(new_turret)

            #支付費用以購買砲塔
            world.money -= c.BUY_COST
            
def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if(mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret
def clear_selection():
    for turret in turret_group:
        turret.selected = False
        
    
#創建世界
world = World(world_data, map_image)
world.process_data()
world.process_enemies()


#創建敵人&砲塔群組
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()


#創建按鈕
turret_button = Button(c.WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.WIDTH + 60, 300, begin_image, True)
fast_forward_button = Button(c.WIDTH + 50, 300, fast_forward_image, False)
restart_button = Button(310, 300, restart_image, True)

#遊戲迴圈
run = True

while run:

    clock.tick(c.FPS)

    if game_over == False:
        if world.health <= 0:
            game_over = True
            game_outcome = -1
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1

    #更新群組以確保不會有影像疊合
    enemy_group.update(world)
    turret_group.update(enemy_group, world)

    if selected_turret:
        selected_turret.selected = True
    
    #繪製關卡
    world.draw(screen)

    #繪製群組
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data()

    if game_over == False:
        
        if level_started == False:
            if begin_button.draw(screen):
                level_started = True
        else:
            #遊戲速度調整
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2
                
            #生成敵軍
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        #檢測關卡結束
        if world.check_level_complete() == True:
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()
        

        #顯示砲塔購買與升級金額
        draw_text(str(c.BUY_COST), text_font, "grey100", c.WIDTH + 215, 135)
        screen.blit(coin_image, (c.WIDTH + 260, 130))
        #繪製按鈕
        if turret_button.draw(screen):
            placing_turrets = True
            
        #當要放置砲塔時，取消按鈕才會出現
        if placing_turrets == True:
            
            #將鼠標位置圖案替換為砲塔
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= c.WIDTH :
                screen.blit(cursor_turret, cursor_rect)
            
            if cancel_button.draw(screen):
                placing_turrets = False

        #當砲塔被選定時，顯示升級按鈕
        if selected_turret:
            if selected_turret.upgrade_level < c.TURRET_LEVELS:#限制升級上限
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.WIDTH + 215, 195)
                screen.blit(coin_image, (c.WIDTH + 260, 190))
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST

    else:
        pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius = 30)
        if game_outcome == -1:
            draw_text("GAMEOVER", large_font, "grey0", 310, 230)
        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
        #重試
        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()

            #清空群組
            enemy_group.empty()
            turret_group.empty()
    #事件控制
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        #滑鼠點擊
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            
            #取得滑鼠位置(座標)
            mouse_pos = pg.mouse.get_pos()#回傳一組座標
            
            #確認滑鼠位置是否在地圖上
            if mouse_pos[0] < c.WIDTH and mouse_pos[1] < c.HEIGHT:
                selected_turret = None
                clear_selection()
                if placing_turrets == True:
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)
    #更新顯示/視窗
    pg.display.flip()
            
pg.quit()
    
