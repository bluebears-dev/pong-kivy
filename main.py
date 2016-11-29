from time import sleep

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector

kivy.require('1.9.1')

green = [0, 1, 0, 1]
white = [1, 1, 1, 1]
initial_velocity = Window.width / 100


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongPaddle(Widget):
    team = ObjectProperty([0, 0, 0, 0])
    score = NumericProperty(0)
    score_color = ObjectProperty([1, 1, 1, 1])
    velocity = NumericProperty(5)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)

            if offset > 1:
                vy *= -1

            if -20 < vx < 20:
                vx *= 1.1
            if -20 < vy < 20:
                vy *= 1.1

            ball.velocity = -vx, vy + offset

    def auto_move(self, ball):
        if ball.velocity_x > 0:
            if ball.center_y > self.center_y:
                self.center_y += self.velocity
            elif ball.center_y < self.center_y:
                self.center_y -= self.velocity


class PongGame(Widget):
    end = ObjectProperty(True)
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    pressed_keys = {
        'w': False,
        's': False,
        'up': False,
        'down': False,
        'escape': False,
        'g': False
     }

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down = self._on_keyboard_down)
        self.keyboard.bind(on_key_up = self._on_keyboard_up)

    def serve_ball(self, velocity = (initial_velocity, 0)):
        self.ball.center = self.center
        self.ball.velocity = velocity
        self.player1.center_y = self.player2.center_y = self.center_y

    def update(self, dt):
        if self.end:
            self.serve_ball(velocity = (0, 0))

        self.ball.move()
        self.handle_keyboard()

        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        # player1 loses
        if self.ball.x <= self.x:
            self.set_point(self, self.player2)
            sleep(dt * 30)
            self.serve_ball(velocity = (initial_velocity, 0))

        # player2 loses
        if self.ball.x >= self.width:
            self.set_point(self, self.player1)
            sleep(dt * 30)
            self.serve_ball(velocity = (-initial_velocity, 0))

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        self.player2.auto_move(self.ball)

    @staticmethod
    def set_point(self, player, points = 1):
        player.score += points
        difference = self.player1.score - self.player2.score

        if player.score >= 10 and (difference > 1 or difference < -1):
            self.end = True

        if self.player1.score > self.player2.score:
            self.player1.score_color = green
            self.player2.score_color = white
        elif self.player1.score == self.player2.score:
            self.player1.score_color = green
            self.player1.score_color = green
        else:
            self.player1.score_color = white
            self.player2.score_color = green

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        elif touch.x > 2 * self.width / 3:
            self.player2.center_y = touch.y

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        pressed_key = keycode[1]
        self.pressed_keys[pressed_key] = True
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        released_key = keycode[1]
        self.pressed_keys[released_key] = False
        return True

    def _keyboard_closed(self):
        self.keyboard.unbind(on_key_down = self._on_keyboard_down)
        self.keyboard = None

    def handle_keyboard(self):
        if self.pressed_keys['escape']:
            quit()
        if self.end and self.pressed_keys['g']:
            self.serve_ball(velocity = (initial_velocity, 0))
            self.player1.score = 0
            self.player2.score = 0
            self.player1.score_color = self.player2.score_color = white
            self.end = False
        else:
            for key in self.pressed_keys:
                if self.pressed_keys[key]:
                    if key == 'w':
                        self.player1.center_y += self.player1.velocity
                    elif key == 's':
                        self.player1.center_y -= self.player1.velocity
                    elif key == 'up':
                        self.player2.center_y += self.player2.velocity
                    elif key == 'down':
                        self.player2.center_y -= self.player2.velocity


class PongApp(App):
    fps = NumericProperty(1.0 / 60.0)

    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, self.fps)
        return game

if __name__ == '__main__':
    PongApp().run()
