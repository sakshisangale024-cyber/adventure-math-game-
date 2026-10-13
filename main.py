# Adventure Math Game - Android-friendly Kivy prototype
# Install/test on a computer with: pip install kivy
# This is a playable prototype, not yet a signed Play Store release.
# Google AdMob requires a separate Android SDK integration and ad-unit IDs.

import random
from collections import deque

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

N = 5
WALLS = {(1, 1), (1, 2), (2, 2), (3, 3)}
START = (0, 0)
ROBOT_START = (4, 0)
GOAL = (4, 4)
KEY_POS = (2, 4)
INITIAL_COINS = {(0, 2), (1, 3), (3, 1), (4, 2)}
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def bfs(start, target, blocked):
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        pos, path = queue.popleft()
        if pos == target:
            return path
        r, c = pos
        for dr, dc in DIRECTIONS:
            nxt = (r + dr, c + dc)
            if (0 <= nxt[0] < N and 0 <= nxt[1] < N
                    and nxt not in blocked and nxt not in seen):
                seen.add(nxt)
                queue.append((nxt, path + [nxt]))
    return []


class AdventureMathApp(App):
    def build(self):
        self.title = "Adventure Math Game"
        Window.clearcolor = (0.06, 0.08, 0.13, 1)

        self.player = START
        self.robot = ROBOT_START
        self.goal = GOAL
        self.coins_on_board = set(INITIAL_COINS)
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.level = 1
        self.has_key = False
        self.game_finished = False
        self.robot_step = 0
        self.user_answer = ""

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        self.status = Label(text="", size_hint_y=None, height=dp(42),
                            font_size="18sp", bold=True)
        root.add_widget(Label(text="ADVENTURE MATH GAME", size_hint_y=None,
                              height=dp(45), font_size="24sp", bold=True,
                              color=(1, .83, .2, 1)))
        root.add_widget(self.status)

        self.board = GridLayout(cols=N, spacing=dp(4), size_hint_y=None,
                                height=dp(300))
        self.cells = []
        for r in range(N):
            row = []
            for c in range(N):
                btn = Button(text="", font_size="20sp", bold=True,
                             background_normal="", background_color=(.22, .55, .32, 1))
                btn.bind(on_release=lambda _btn, rr=r, cc=c: self.tap_cell(rr, cc))
                self.board.add_widget(btn)
                row.append(btn)
            self.cells.append(row)
        root.add_widget(self.board)

        self.question_label = Label(text="", size_hint_y=None, height=dp(38),
                                    font_size="20sp", color=(1, .83, .2, 1))
        root.add_widget(self.question_label)

        answer_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(6))
        self.answer_input = TextInput(hint_text="Type answer", multiline=False,
                                      input_filter="int", font_size="18sp")
        self.answer_input.bind(on_text_validate=self.submit_answer)
        answer_row.add_widget(self.answer_input)
        answer_row.add_widget(Button(text="Submit", size_hint_x=.35,
                                     on_release=self.submit_answer))
        root.add_widget(answer_row)

        controls = GridLayout(cols=3, rows=2, spacing=dp(5),
                              size_hint_y=None, height=dp(100))
        controls.add_widget(Label(text=""))
        controls.add_widget(Button(text="▲", font_size="22sp",
                                   on_release=lambda *_: self.move_player(-1, 0)))
        controls.add_widget(Label(text=""))
        controls.add_widget(Button(text="◀", font_size="22sp",
                                   on_release=lambda *_: self.move_player(0, -1)))
        controls.add_widget(Button(text="▼", font_size="22sp",
                                   on_release=lambda *_: self.move_player(1, 0)))
        controls.add_widget(Button(text="▶", font_size="22sp",
                                   on_release=lambda *_: self.move_player(0, 1)))
        root.add_widget(controls)

        root.add_widget(Label(
            text="Tap a neighbouring tile or use the arrows. Reach 🏆 to advance.",
            size_hint_y=None, height=dp(32), font_size="12sp"
        ))

        self.make_question()
        self.refresh_board()
        Clock.schedule_interval(self.robot_turn, 0.75)
        return root

    def make_question(self):
        if self.level == 1:
            a, b = random.randint(1, 10), random.randint(1, 10)
        elif self.level == 2:
            a, b = random.randint(5, 20), random.randint(2, 12)
        else:
            a, b = random.randint(10, 30), random.randint(2, 15)
        op = random.choice(["+", "-", "*"])
        self.answer_value = a + b if op == "+" else a - b if op == "-" else a * b
        self.question_label.text = f"Solve to earn points: {a} {op} {b} = ?"

    def refresh_board(self):
        self.status.text = (
            f"Level {self.level}   Score {self.score}   Coins {self.coins}   "
            f"Lives {self.lives}   Key {'✓' if self.has_key else '—'}"
        )
        for r in range(N):
            for c in range(N):
                pos = (r, c)
                btn = self.cells[r][c]
                if pos in WALLS:
                    btn.text, btn.background_color = "✖", (.35, .37, .4, 1)
                elif pos == self.player and pos == self.robot:
                    btn.text, btn.background_color = "P+AI", (.65, .3, .8, 1)
                elif pos == self.player:
                    btn.text, btn.background_color = "🧑", (.2, .48, .9, 1)
                elif pos == self.robot:
                    btn.text, btn.background_color = "🤖", (.62, .3, .85, 1)
                elif pos == self.goal:
                    btn.text, btn.background_color = "🏆", (.95, .65, .12, 1)
                elif pos == KEY_POS and not self.has_key:
                    btn.text, btn.background_color = "🔑", (.18, .55, .35, 1)
                elif pos in self.coins_on_board:
                    btn.text, btn.background_color = "🪙", (.18, .55, .35, 1)
                else:
                    btn.text, btn.background_color = "", (.18, .55, .35, 1)

    def tap_cell(self, r, c):
        if self.game_finished:
            return
        dr, dc = r - self.player[0], c - self.player[1]
        if abs(dr) + abs(dc) == 1:
            self.move_player(dr, dc)

    def move_player(self, dr, dc):
        if self.game_finished:
            return
        r, c = self.player
        nxt = (r + dr, c + dc)
        if not (0 <= nxt[0] < N and 0 <= nxt[1] < N) or nxt in WALLS:
            return
        self.player = nxt
        self.score += 10
        if nxt in self.coins_on_board:
            self.coins_on_board.remove(nxt)
            self.coins += 1
            self.score += 20
        if nxt == KEY_POS and not self.has_key:
            self.has_key = True
            self.score += 50
        if nxt == self.goal:
            if self.level < 3:
                self.level += 1
                self.player = START
                self.robot = ROBOT_START
                self.has_key = False
                self.coins_on_board = set(INITIAL_COINS)
                self.make_question()
            else:
                self.finish("🏆 Treasure found! You won!")
                return
        self.refresh_board()

    def submit_answer(self, *_):
        if self.game_finished:
            return
        raw = self.answer_input.text.strip()
        if not raw:
            return
        try:
            value = int(raw)
        except ValueError:
            return
        if value == self.answer_value:
            self.score += 30
            self.question_label.text = "Correct! +30 points"
        else:
            self.lives -= 1
            self.question_label.text = "Not quite! Try the next question."
        self.answer_input.text = ""
        if self.lives <= 0:
            self.finish("Game over!")
            return
        self.make_question()
        self.refresh_board()

    def robot_turn(self, _dt):
        if self.game_finished:
            return
        path = bfs(self.robot, self.goal, WALLS)
        if len(path) > 1:
            self.robot = path[1]
        if self.robot == self.goal:
            # The robot is an AI rival; it resets after reaching the treasure.
            self.robot = ROBOT_START
        self.refresh_board()

    def finish(self, message):
        self.game_finished = True
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(Label(text=f"{message}\nFinal score: {self.score}",
                                 font_size="20sp"))
        btn = Button(text="Play Again", size_hint_y=None, height=dp(48))
        popup = Popup(title="Adventure Math Game", content=content,
                      size_hint=(.85, .45), auto_dismiss=False)
        btn.bind(on_release=lambda *_: (popup.dismiss(), self.restart()))
        content.add_widget(btn)
        popup.open()

    def restart(self):
        self.player = START
        self.robot = ROBOT_START
        self.coins_on_board = set(INITIAL_COINS)
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.level = 1
        self.has_key = False
        self.game_finished = False
        self.make_question()
        self.refresh_board()


if __name__ == "__main__":
    AdventureMathApp().run()
