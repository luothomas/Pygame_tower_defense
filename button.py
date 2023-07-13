import pygame as pg

class Button():
    def __init__(self, x, y, image, single_click):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.single_click = single_click
    def draw(self, surface):
        action = False
        #取得滑鼠位置
        pos = pg.mouse.get_pos()
        #偵測鼠標位置和設定反應
        if self.rect.collidepoint(pos):
            #限制單次點擊只能觸發一次反應
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                #檢測按鈕類型
                if self.single_click:
                    self.clicked = True

            if pg.mouse.get_pressed()[0] == 0:
                self.clicked = False
        #繪製按鈕
        surface.blit(self.image, self.rect)

        return action
