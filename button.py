import pygame
from settings import *

pygame.mixer.init()

class Button():
    def __init__(self, screen, image, pos_x, pos_y):
        self.image = image
        self.rect = self.image.get_frect()
        self.rect.topleft = (pos_x,pos_y)
        self.screen = screen
        self.hovered = False
        self.clicked = False
        self.mask = pygame.mask.from_surface(self.image)

        # Loads all the button sound effects once
        try:
            self.hover_sound = pygame.mixer.Sound("Assets/Sounds/Button_Hover.wav")
            self.click_sound = pygame.mixer.Sound("Assets/Sounds/Button_Click.wav")
        except Exception:
            self.hover_sound = None
            self.click_sound = None

    def draw(self):
        # puts the buttons on screen at the rect topleft coordinates
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

    def button_outline(self, img, pos):
        mask = pygame.mask.from_surface(img)
        mask_outline = mask.outline()
        mask_surf = pygame.Surface(img.get_size())
        for pixel in mask_outline:
            mask_surf.set_at(pixel,(255,255,255))
        mask_surf.set_colorkey((0,0,0))
        self.screen.blit(mask_surf,(pos[0] - 1, pos[1]))
        self.screen.blit(mask_surf,(pos[0] + 1, pos[1]))
        self.screen.blit(mask_surf,(pos[0], pos[1] - 1))
        self.screen.blit(mask_surf,(pos[0], pos[1] + 1))

    def is_clicked(self) -> bool:
        # gets mouse position
        pos = pygame.mouse.get_pos()
        action = False
        # checks if mouse is over the button, draws the outline and checks if player clicked the button
        if self.rect.collidepoint(pos):
            self.button_outline(self.image, (self.rect.x, self.rect.y))
            # play hover sound only once when the mouse enters the button area
            if not self.hovered:
                if self.hover_sound:
                    self.hover_sound.play()
                self.hovered = True
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True    
                self.click_sound.play()  

        else:
            # reset hover state when mouse leaves
            self.hovered = False
             
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action