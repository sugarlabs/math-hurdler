#!/usr/bin/env python3

from sugar3.activity.activity import get_activity_root
from gi.repository import Gtk
from fractions import Fraction
from question import Question
from objects.button import Button
from option_button import Option_Button
from sprites.horse import Horse
from sprites.sun import Sun

import logging
import pygame
import random
import os
import math
import gi
gi.require_version('Gtk', '3.0')


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    SKYBLUE = (126, 192, 238)
    BROWN = (127, 96, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)


class MathHurdler:
    def __init__(self):
        self.clock = pygame.time.Clock()

        self.x = -100
        self.vx = 5

        self.resume = False
        self.paused = False
        self.direction = -1

        self.volume = 1

        self.circle_size = 150

        self.horse_change_semaphore = 3
        self.horse_change = 0

        pygame.font.init()
        self.font = pygame.font.SysFont('monospace', 36)
        self.lg_font = pygame.font.SysFont('monospace', 60)
        self.xlg_font = pygame.font.SysFont('monospace', 90)

        self.hurdle_number = 0

        self.points = 0
        self.hscore = self.load_highscore()

        self.question = Question()

        self.question_text_label = self.lg_font.render(
            str(self.question),
            1,
            Color.BLACK
        )

        self.question_label = self.font.render(
            'Hurdle #' + str(self.hurdle_number),
            1,
            Color.BLACK
        )

        self.score_label = self.lg_font.render(
            str(self.points),
            1,
            Color.BLACK
        )
        self.hscore_label = self.font.render(
            "High Score: " + str(self.hscore),
            1,
            Color.BLACK
        )

        self.buttons = []

        self.songs = [
            self.get_sound_path('william_tell_overture_intro.wav'),
            self.get_sound_path('william_tell_overture_race.wav')
        ]

        pygame.mixer.init()
        self.death_sfx = pygame.mixer.Sound(
            self.get_sound_path('sad_trombone.wav'))
        self.jump_sfx = pygame.mixer.Sound(self.get_sound_path('success.wav'))

        self.sounds = [self.death_sfx, self.jump_sfx]

    def set_paused(self, paused):
        self.paused = paused
        if paused:
            pygame.mixer.pause()
            pygame.mixer.music.stop()
        else:
            pygame.mixer.unpause()
            pygame.mixer.music.play(-1)

    def set_volume(self, volume):
        self.volume = volume
        for sound in self.sounds:
            sound.set_volume(self.volume)
        pygame.mixer.music.set_volume(self.volume)

    def toggle_mute(self):
        self.set_volume((self.volume + 1) % 2)

    def set_gameover(self, gameover):
        self.gameover = gameover
        if gameover:
            pygame.mixer.music.stop()
            self.death_sfx.play()

    def set_playing(self, playing):
        self.playing = playing
        self.set_paused(False)
        self.set_gameover(False)
        if playing:
            pygame.mixer.music.load(self.songs[1])
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load(self.songs[0])
            pygame.mixer.music.play(-1)

    def get_image_path(self, asset_name):
        return os.path.join('./assets/images', asset_name)

    def get_sound_path(self, sound_name):
        return os.path.join('./assets/sounds', sound_name)

    def write_file(self):
        self.save_highscore()
        return self.points, self.hscore, self.playing, self.hurdle_number

    def restore_game(self, score='', hscore='',
                     play_state='', hurdle_number=''):
        self.resume = True
        self.points = int(score)
        self.hscore = int(hscore)
        self.hurdle_number = int(hurdle_number) - 1
        if play_state == 'True':
            self.playing = True
        else:
            self.playing = False

    def save_highscore(self):
        file_path = os.path.join(get_activity_root(), 'data', 'highscore')
        logging.debug(file_path)
        highscore = []
        if os.path.exists(file_path):
            with open(file_path, "r") as fp:
                highscore = fp.readlines()
                int_highscore = int(highscore[0])
            if int_highscore <  self.points:
                with open(file_path, "w") as fp:
                    fp.write(str(self.points))
        else:
            with open(file_path, "w") as fp:
                fp.write(str(self.points))

    def load_highscore(self):
        file_path = os.path.join(get_activity_root(), 'data', 'highscore')
        highscore = [0]
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as fp:
                    highscore = fp.readlines()
                return int(highscore[0])
            except ValueError or IndexError:
                return 0
        return 0


    def run(self):
        self.start_time = 0
        self.time_since_gameover = 0
        if not self.resume:
            self.playing = False
        self.running = True
        self.gameover = False
        self.paused = False
        self.last_answer = -1
        self.last_answer_index = -1
        question_dirty = True

        pygame.display.init()
        display_info = pygame.display.Info()
        background_color = Color.SKYBLUE

        screen = pygame.display.get_surface()
        screen_size = screen.get_size()
        ground = pygame.image.load('./assets/images/ground.png')
        ground = pygame.transform.scale(ground, (int(screen_size[0]), int(screen_size[1] // 3)))

        grass = pygame.image.load('./assets/images/grass.png')
        grass = pygame.transform.scale(grass, (int(screen_size[0]), int(screen_size[1] // 12)))
        ground.blit(grass, (0,0))

        points_label = self.lg_font.render('POINTS', 1, Color.BLACK)

        sun = Sun()
        sun.rect.topleft = (screen_size[0] - sun.image.get_width(), 0)

        horse = Horse()
        horse.rect.x = display_info.current_h // 3
        horse.rect.y = display_info.current_h - \
            horse.image.get_height() - ground.get_height()

        hurdle = pygame.image.load('./assets/images/hurdle.png')
        hurdle = pygame.transform.scale(
            hurdle,
            (int(hurdle.get_height() // 3), int(hurdle.get_width() // 3)))

        hurdle_y = display_info.current_h - \
            hurdle.get_height() - (2 * ground.get_height() // 3) + 70

        self.buttons = []
        button_width = 200
        button_height = 80
        buttons_x_padding = 50
        buttons_y_padding = (ground.get_rect().height - grass.get_rect().height - button_height) // 4
        buttons_gap = (screen_size[0] - (buttons_x_padding * 2 + button_width * 4)) // 3
        
        for i, choice in enumerate(self.question.choices):
            choice_text = self.lg_font.render(("A", "B", "C", "D")[i] + " " + str(choice), 1, Color.BLACK)
            self.buttons.append(
                Option_Button(
                    buttons_x_padding + button_width * i + buttons_gap * i,
                    screen_size[1] - button_height - buttons_y_padding,
                    button_width, button_height, choice_text, str(choice)
                )
            )

        question_board = pygame.Surface(
            (screen_size[0] // 3, screen_size[1] // 5))
        question_board = question_board.convert()
        question_board.fill(Color.WHITE)

        play_button = Button(
            'Play',
            self.lg_font,
            Color.BLACK,
            200,
            100,
            Color.WHITE,
            Color.BLACK,
            -2
        )

        menu_label = self.xlg_font.render('MATH HURDLER', 1, Color.BLACK)
        gameover_label = self.xlg_font.render('GAME OVER', 1, Color.BLACK)

        pygame.mixer.music.load(self.songs[0])
        pygame.mixer.music.play(-1)

        def reset():
            question_dirty = True

            self.points = 0
            if not self.playing:
                self.hurdle_number = 0

            self.x = -100
            self.vx = 5

            self.direction = -1

            horse.set_horse(Horse.BASE)

        def generate_question():
            next(self.question)

            for i in range(4):
                choice_text = self.lg_font.render(("A", "B", "C", "D")[i] + " " + str(self.question.choices[i]),
                                                  1, Color.BLACK)
                self.buttons[i].set_text(choice_text)
                self.buttons[i].value = str(self.question.choices[i])
                self.buttons[i].set_color((255, 255, 255))

            self.question_text_label = self.lg_font.render(
                str(self.question), 1, Color.BLACK)
            self.hurdle_number += 1
            # start at vx=5 and accelerate towards vx=10
            self.vx = 4 + (self.hurdle_number * 6) // (self.hurdle_number + 5)
            self.score_label = self.lg_font.render(
                str(self.points), 1, Color.BLACK)
            self.question_label = self.font.render(
                "Hurdle #" + str(self.hurdle_number), 1, Color.BLACK)
            question_board.fill(Color.WHITE)
            self.hscore_label = self.font.render(
                "High Score: " + str(self.hscore),
                1,
                Color.BLACK
            )

        def set_answer(answer_index):
            self.vx *= 2
            if self.last_answer_index >= 0:
                self.buttons[self.last_answer_index].set_selected(False)

            if answer_index >= 0:
                self.last_answer = Fraction(self.buttons[answer_index].value)
                self.buttons[answer_index].set_selected(True)
                self.last_answer_index = answer_index
            else:
                self.last_answer = -1
                self.last_answer_index = -1

        def evaluate_answer(answer):
            if self.question.is_answer(answer):
                self.points += 100
                if self.hscore < self.points:
                    self.hscore = self.points
                self.score_label = self.lg_font.render(
                    str(self.points), 1, Color.BLACK)
                self.hscore_label = self.font.render(
                    "High Score: " + str(self.hscore), 1, Color.BLACK)
                self.jump_sfx.play()
            else:
                self.set_gameover(True)
                self.start_time = pygame.time.get_ticks()
                if self.last_answer_index >= 0:
                    self.buttons[self.last_answer_index].set_color(
                        Color.RED)

            self.buttons[self.question.answer_index].set_color(
                Color.GREEN)

        while self.running:
            while Gtk.events_pending():
                Gtk.main_iteration()
            if self.playing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.VIDEORESIZE:
                        pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                        elif event.key == pygame.K_a or event.key == pygame.K_1:
                            set_answer(0)
                        elif event.key == pygame.K_b or event.key == pygame.K_2:
                            set_answer(1)
                        elif event.key == pygame.K_c or event.key == pygame.K_3:
                            set_answer(2)
                        elif event.key == pygame.K_d or event.key == pygame.K_4:
                            set_answer(3)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if not self.gameover:
                            for i in range(0, 4):
                                self.buttons[i].mouse_click(
                                    pygame.mouse.get_pos(),
                                    set_answer,
                                    i
                                )

                screen_size = screen.get_size()

                if not self.paused and not self.gameover:
                    self.x += self.vx * self.direction
                    if self.direction == 1 and self.x > screen.get_width() \
                            + 50:
                        self.x = -50
                    elif self.direction == -1 and self.x < -50:
                        self.x = screen.get_width() + 50

                    hurdle_rect = hurdle.get_rect(topleft=(self.x, hurdle_y))

                    if (horse.active_horse == Horse.JUMP) and (
                            not horse.rect.colliderect(hurdle_rect)):
                        horse.set_horse(Horse.BASE)
                    if (self.horse_change == self.horse_change_semaphore):
                        horse.gallop()
                        self.horse_change = 0

                    self.horse_change += 1

                    horse.rect.x = display_info.current_w // 3
                    horse.rect.y = display_info.current_h - \
                        hurdle.get_height() - (3 * ground.get_height() // 4) + 70

                    # Check if hurdle and horse in same spot.
                    if horse.rect.colliderect(hurdle_rect):
                        # evaluate answer on first frame of hurdle collision
                        if not question_dirty:
                            evaluate_answer(self.last_answer)
                            question_dirty = True

                        # if not gameover, jump the hurdle
                        if not self.gameover:
                            horse.set_horse(Horse.JUMP)
                            horse.rect.x = display_info.current_w // 3
                            horse.rect.y = display_info.current_h \
                                - horse.image.get_height() \
                                - ground.get_height() \
                                - 100

                    # if not colliding with hurdle and question still dirty,
                    # generate new question
                    elif question_dirty:
                        generate_question()
                        question_dirty = False

                if self.gameover:
                    self.save_highscore()
                    horse.set_horse(Horse.DEAD)
                    self.time_since_gameover = pygame.time.get_ticks() - self.start_time

                screen.fill(background_color)

                sun.rect.topleft = (screen_size[0] - sun.image.get_width(), 0)

                screen.blit(
                    question_board,
                    (screen_size[0] // 4,
                     screen_size[1] // 5))
                question_board.blit(self.question_label, (10, 10))
                question_board.blit(
                    self.question_text_label,
                    (10, self.question_label.get_height() + 10))

                screen.blit(ground, (0, screen_size[1] - ground.get_height()))

                screen.blit(hurdle, (self.x, hurdle_y))

                allsprites = pygame.sprite.RenderPlain(sun, horse)
                allsprites.draw(screen)

                for btn in self.buttons:
                    btn.draw()

                screen.blit(
                    self.score_label,
                    (
                        sun.rect.x + sun.image.get_width() // 4,
                        sun.rect.y + sun.image.get_height() // 3
                    )
                )

                screen.blit(
                    points_label,
                    (
                        sun.rect.x + sun.image.get_width() // 4,
                        sun.rect.y + sun.image.get_height() // 3
                        + self.score_label.get_height()
                    )
                )

                screen.blit(self.hscore_label, (10, 20))

                if self.gameover:
                    screen.blit(
                        gameover_label,
                        (
                            (screen_size[0] - gameover_label.get_width()) // 2,
                            (screen_size[1] - gameover_label.get_height()) // 2,
                        )
                    )

                pygame.display.flip()

                if self.gameover and self.time_since_gameover >= 6000:
                    self.set_playing(False)
                    reset()

                self.clock.tick(18)

            else:
                def start_game():
                    reset()
                    self.set_playing(True)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.VIDEORESIZE:
                        pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        play_button.mouse_click(
                            pygame.mouse.get_pos(),
                            start_game
                        )

                screen_size = screen.get_size()

                if (self.horse_change == self.horse_change_semaphore):
                    horse.gallop()
                    self.horse_change = 0

                self.horse_change += 1

                screen.fill(
                    (
                        math.floor(
                            math.sin(
                                pygame.time.get_ticks() * .001) * 55 + 200),
                        math.floor(
                            math.sin(
                                pygame.time.get_ticks() * .001 + math.pi
                                    ) * 55 + 200),
                        math.floor(math.sin(pygame.time.get_ticks()
                                            * .001 + math.pi * .5) * 55 + 200)
                    )
                )

                horse.rect.x = (screen_size[0] - horse.image.get_width()) // 2
                horse.rect.y = (
                    screen_size[1] - horse.image.get_height()) // 2 + 200

                menu_sprites = pygame.sprite.RenderPlain(horse)
                menu_sprites.draw(screen)

                play_button.rect.x = (
                    screen_size[0] - play_button.rect.width) // 2
                play_button.rect.y = (
                    screen_size[1] - play_button.rect.height) // 2
                play_button.draw(screen)

                screen.blit(
                    menu_label,
                    (
                        (screen_size[0] - menu_label.get_width()) // 2,
                        (screen_size[1] - menu_label.get_height()) // 2 - 200,
                    )
                )

                pygame.display.flip()

                self.clock.tick(30)


# This function is called when the game is run directly from the command line:
# ./TestGame.py
def main():
    pygame.init()
    pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    game = MathHurdler()
    game.run()


if __name__ == '__main__':
    main()
