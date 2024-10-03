# Copyright (C) 2023 Riya Jain
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pygame


class Option_Button:

    def __init__(self, x, y, width, height, text, value):
        self.text = text
        self.text_rect = text.get_rect()
        self.value = value

        self.rect = pygame.Rect(x, y, width, height)

        self.gameDisplay = pygame.display.get_surface()

        self.color = (255, 255, 255)
        self.selected_color = (180, 180, 180)

        self.press = False
        self.draw()

    def set_text(self, text):
        self.text = text
        self.text_rect = text.get_rect()

    def draw(self):
        c_radius = self.rect.height // 2
        c_center = [self.rect.x, self.rect.y + c_radius]
        pygame.draw.circle(self.gameDisplay, self.color, c_center, c_radius)
        c_center[0] += self.rect.width
        pygame.draw.circle(self.gameDisplay, self.color, c_center, c_radius)
        pygame.draw.rect(self.gameDisplay, self.color, self.rect)
        m_x = self.rect.x + self.rect.width // 2 - self.text_rect.width // 2
        m_y = self.rect.y + self.rect.height // 2 - self.text_rect.height // 2
        self.gameDisplay.blit(self.text, (m_x, m_y))

    def set_color(self, color):
        self.color = color

    def hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def mouse_click(self, mouse, action, *args):
        if self.rect.collidepoint(mouse):
            action(*args)

    def set_selected(self, selected):
        if selected:
            self.set_color(self.selected_color)
        else:
            self.set_color((255, 255, 255))
