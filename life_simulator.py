#!/usr/bin/env python3
"""Simple life simulator raising game (GUI)."""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable


@dataclass
class Stats:
    age: int = 6
    health: int = 70
    happiness: int = 70
    knowledge: int = 30
    money: int = 20

    def clamp(self) -> None:
        self.health = max(0, min(100, self.health))
        self.happiness = max(0, min(100, self.happiness))
        self.knowledge = max(0, min(100, self.knowledge))
        self.money = max(0, min(200, self.money))


Action = Callable[[Stats], str]


def study(stats: Stats) -> str:
    stats.knowledge += 12
    stats.happiness -= 6
    stats.money -= 2
    return "공부했다. 지식 +12, 행복 -6, 용돈 -2"


def play(stats: Stats) -> str:
    stats.happiness += 12
    stats.health += 4
    stats.money -= 3
    return "놀았다. 행복 +12, 건강 +4, 용돈 -3"


def part_time(stats: Stats) -> str:
    stats.money += 15
    stats.health -= 6
    stats.happiness -= 4
    return "아르바이트를 했다. 돈 +15, 건강 -6, 행복 -4"


def exercise(stats: Stats) -> str:
    stats.health += 12
    stats.happiness += 2
    stats.money -= 2
    return "운동했다. 건강 +12, 행복 +2, 용돈 -2"


def rest(stats: Stats) -> str:
    stats.health += 8
    stats.happiness += 6
    return "쉬었다. 건강 +8, 행복 +6"


def yearly_event(stats: Stats) -> str:
    events = [
        ("감기에 걸렸다.", -8, -3, 0, 0),
        ("친구와 좋은 추억을 만들었다.", 0, 10, 0, -2),
        ("책을 읽고 영감을 얻었다.", 0, 3, 8, -1),
        ("경품에 당첨됐다!", 0, 6, 0, 12),
        ("스트레스를 받았다.", -4, -10, 0, 0),
        ("가족과 시간을 보냈다.", 2, 8, 0, -1),
    ]
    text, health, happiness, knowledge, money = random.choice(events)
    stats.health += health
    stats.happiness += happiness
    stats.knowledge += knowledge
    stats.money += money
    return f"연간 이벤트: {text}"


def end_summary(stats: Stats) -> str:
    score = stats.health + stats.happiness + stats.knowledge + stats.money
    if score >= 320:
        ending = "당신은 균형 잡힌 인생을 살아냈다!"
    elif stats.knowledge >= 85:
        ending = "학자로 성장했다!"
    elif stats.money >= 140:
        ending = "부자가 되었다!"
    elif stats.happiness >= 85:
        ending = "행복한 인생을 살았다!"
    elif stats.health <= 20:
        ending = "건강을 돌보는 법을 배웠다."
    else:
        ending = "평범하지만 소중한 삶이었다."
    return f"\n최종 나이: {stats.age}살\n{ending}"


def stats_line(stats: Stats) -> str:
    return (
        f"나이: {stats.age}살 | 건강 {stats.health:3d} | 행복 {stats.happiness:3d} | "
        f"지식 {stats.knowledge:3d} | 돈 {stats.money:3d}"
    )


class LifeSimulatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.stats = Stats()
        self.actions: dict[str, Action] = {
            "공부": study,
            "놀기": play,
            "아르바이트": part_time,
            "운동": exercise,
            "휴식": rest,
        }

        self.root.title("간단한 인생 시뮬레이터 키우기")
        self.root.geometry("640x420")
        self.root.resizable(False, False)

        container = ttk.Frame(root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            container,
            text="간단한 인생 시뮬레이터 키우기",
            font=("Apple SD Gothic Neo", 18, "bold"),
        )
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            container,
            text="6살부터 25살까지, 매년 하나의 행동을 선택합니다.",
            foreground="#444",
        )
        subtitle.pack(anchor=tk.W, pady=(4, 10))

        self.stats_var = tk.StringVar(value=stats_line(self.stats))
        stats_label = ttk.Label(container, textvariable=self.stats_var, font=("Arial", 11))
        stats_label.pack(anchor=tk.W, pady=(0, 8))

        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(0, 12))

        self.action_buttons: list[ttk.Button] = []
        for idx, (label, action) in enumerate(self.actions.items()):
            button = ttk.Button(
                button_frame,
                text=label,
                command=lambda act=action: self.handle_action(act),
            )
            button.grid(row=0, column=idx, padx=4, sticky=tk.EW)
            self.action_buttons.append(button)
            button_frame.columnconfigure(idx, weight=1)

        self.quit_button = ttk.Button(button_frame, text="저장 없이 종료", command=self.quit_game)
        self.quit_button.grid(row=1, column=0, columnspan=5, pady=(8, 0), sticky=tk.EW)

        self.log = tk.Text(
            container,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED,
            background="#f7f7f7",
        )
        self.log.pack(fill=tk.BOTH, expand=True)

        self.append_log("게임을 시작합니다! 매년 행동을 선택하세요.")

    def append_log(self, message: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, f"{message}\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def update_stats(self) -> None:
        self.stats_var.set(stats_line(self.stats))

    def handle_action(self, action: Action) -> None:
        if self.stats.age > 25:
            return
        result = action(self.stats)
        event_result = yearly_event(self.stats)
        self.stats.clamp()
        self.append_log(result)
        self.append_log(event_result)
        self.stats.age += 1
        self.update_stats()

        if self.stats.health == 0 or self.stats.happiness == 0:
            self.append_log("체력 또는 행복이 0이 되어 게임이 종료되었습니다.")
            self.finish_game()
        elif self.stats.age > 25:
            self.finish_game()

    def finish_game(self) -> None:
        summary = end_summary(self.stats)
        self.append_log(summary.strip())
        for button in self.action_buttons:
            button.configure(state=tk.DISABLED)
        self.quit_button.configure(state=tk.DISABLED)
        messagebox.showinfo("게임 종료", summary)

    def quit_game(self) -> None:
        if messagebox.askyesno("종료", "저장하지 않고 종료할까요?"):
            self.append_log("게임을 저장하지 않고 종료합니다.")
            self.finish_game()


def run_game() -> None:
    root = tk.Tk()
    ttk.Style(root).theme_use("clam")
    LifeSimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_game()
