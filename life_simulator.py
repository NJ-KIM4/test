#!/usr/bin/env python3
"""Upgraded life simulator with richer GUI and visuals."""

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
        self.money = max(0, min(300, self.money))


Action = Callable[[Stats], str]


@dataclass
class ActionEntry:
    label: str
    action: Action
    min_age: int = 6
    hint: str = ""


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
    stats.money += 18
    stats.health -= 6
    stats.happiness -= 4
    return "아르바이트를 했다. 돈 +18, 건강 -6, 행복 -4"


def exercise(stats: Stats) -> str:
    stats.health += 12
    stats.happiness += 2
    stats.money -= 2
    return "운동했다. 건강 +12, 행복 +2, 용돈 -2"


def rest(stats: Stats) -> str:
    stats.health += 8
    stats.happiness += 6
    return "쉬었다. 건강 +8, 행복 +6"


def travel(stats: Stats) -> str:
    stats.happiness += 16
    stats.knowledge += 4
    stats.money -= 12
    return "여행을 다녀왔다. 행복 +16, 지식 +4, 돈 -12"


def start_business(stats: Stats) -> str:
    outcome = random.choice(["boom", "steady", "bust"])
    if outcome == "boom":
        stats.money += 30
        stats.happiness += 6
        stats.health -= 4
        return "창업이 대성공! 돈 +30, 행복 +6, 건강 -4"
    if outcome == "steady":
        stats.money += 12
        stats.happiness += 2
        stats.health -= 2
        return "창업이 안정적으로 성장했다. 돈 +12, 행복 +2, 건강 -2"
    stats.money -= 8
    stats.happiness -= 6
    stats.health -= 4
    return "창업이 실패했다. 돈 -8, 행복 -6, 건강 -4"


def yearly_event(stats: Stats) -> str:
    events = [
        ("감기에 걸렸다.", -8, -3, 0, 0),
        ("친구와 좋은 추억을 만들었다.", 0, 10, 0, -2),
        ("책을 읽고 영감을 얻었다.", 0, 3, 8, -1),
        ("경품에 당첨됐다!", 0, 6, 0, 12),
        ("스트레스를 받았다.", -4, -10, 0, 0),
        ("가족과 시간을 보냈다.", 2, 8, 0, -1),
        ("새로운 멘토를 만났다.", 0, 4, 6, -2),
        ("큰 공연을 보고 감동했다.", 0, 8, 3, -4),
    ]
    text, health, happiness, knowledge, money = random.choice(events)
    stats.health += health
    stats.happiness += happiness
    stats.knowledge += knowledge
    stats.money += money
    return f"연간 이벤트: {text}"


def milestone_event(stats: Stats) -> str | None:
    milestones = {
        10: ("학교 발표회에서 상을 받았다!", 0, 6, 6, 2),
        13: ("첫 동아리에 가입했다.", 0, 8, 4, -1),
        16: ("진로를 고민하기 시작했다.", 0, -2, 8, 0),
        19: ("첫 직장 면접에 합격했다!", 0, 6, 4, 10),
        22: ("독립하여 자취를 시작했다.", -2, 4, 0, -8),
        25: ("인생의 방향을 다시 정리했다.", 2, 4, 4, 0),
    }
    if stats.age in milestones:
        text, health, happiness, knowledge, money = milestones[stats.age]
        stats.health += health
        stats.happiness += happiness
        stats.knowledge += knowledge
        stats.money += money
        return f"인생 이벤트: {text}"
    return None


def end_summary(stats: Stats) -> str:
    score = stats.health + stats.happiness + stats.knowledge + stats.money
    if score >= 340:
        ending = "당신은 균형 잡힌 인생을 살아냈다!"
    elif stats.knowledge >= 85:
        ending = "학자로 성장했다!"
    elif stats.money >= 180:
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
        self.actions: list[ActionEntry] = [
            ActionEntry("공부", study, hint="지식 상승"),
            ActionEntry("놀기", play, hint="행복 상승"),
            ActionEntry("아르바이트", part_time, min_age=12, hint="돈 상승"),
            ActionEntry("운동", exercise, hint="건강 상승"),
            ActionEntry("휴식", rest, hint="회복"),
            ActionEntry("여행", travel, min_age=15, hint="행복/지식"),
            ActionEntry("창업", start_business, min_age=18, hint="큰 수익"),
        ]

        self.root.title("인생 시뮬레이터: 드림 라이프")
        self.root.geometry("980x640")
        self.root.resizable(False, False)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Apple SD Gothic Neo", 20, "bold"))
        style.configure("Subtitle.TLabel", font=("Apple SD Gothic Neo", 11))
        style.configure("StatName.TLabel", font=("Apple SD Gothic Neo", 10, "bold"))
        style.configure("Action.TButton", font=("Apple SD Gothic Neo", 10, "bold"))

        container = ttk.Frame(root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container)
        header.pack(fill=tk.X)

        title = ttk.Label(header, text="인생 시뮬레이터: 드림 라이프", style="Title.TLabel")
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            header,
            text="6살부터 25살까지 매년 선택이 당신의 삶을 결정합니다.",
            style="Subtitle.TLabel",
            foreground="#4a4a4a",
        )
        subtitle.pack(anchor=tk.W, pady=(4, 10))

        main = ttk.Frame(container)
        main.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(main)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        right_panel = ttk.Frame(main)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.stats_var = tk.StringVar(value=stats_line(self.stats))
        stats_label = ttk.Label(left_panel, textvariable=self.stats_var, font=("Arial", 11))
        stats_label.pack(anchor=tk.W, pady=(0, 8))

        stat_box = ttk.LabelFrame(left_panel, text="상태 지표")
        stat_box.pack(fill=tk.X, pady=(0, 12))

        self.health_bar = self._build_bar(stat_box, "건강", 100)
        self.happiness_bar = self._build_bar(stat_box, "행복", 100)
        self.knowledge_bar = self._build_bar(stat_box, "지식", 100)
        self.money_bar = self._build_bar(stat_box, "돈", 300)

        action_box = ttk.LabelFrame(left_panel, text="행동 선택")
        action_box.pack(fill=tk.X, pady=(0, 12))

        self.action_buttons: list[ttk.Button] = []
        for entry in self.actions:
            button = ttk.Button(
                action_box,
                text=f"{entry.label} ({entry.hint})" if entry.hint else entry.label,
                style="Action.TButton",
                command=lambda act=entry: self.handle_action(act),
            )
            button.pack(fill=tk.X, pady=3)
            self.action_buttons.append(button)

        self.quit_button = ttk.Button(left_panel, text="저장 없이 종료", command=self.quit_game)
        self.quit_button.pack(fill=tk.X)

        self.canvas = tk.Canvas(right_panel, width=520, height=320, background="#dcecff", highlightthickness=0)
        self.canvas.pack(fill=tk.X)

        log_box = ttk.LabelFrame(right_panel, text="연간 기록")
        log_box.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.log = tk.Text(
            log_box,
            height=12,
            wrap=tk.WORD,
            state=tk.DISABLED,
            background="#f7f7f7",
            relief=tk.FLAT,
        )
        self.log.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.append_log("게임을 시작합니다! 매년 행동을 선택하세요.")
        self.update_stats()
        self.draw_scene()

    def _build_bar(self, parent: ttk.Frame, label: str, maximum: int) -> ttk.Progressbar:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(frame, text=label, style="StatName.TLabel").pack(anchor=tk.W)
        bar = ttk.Progressbar(frame, maximum=maximum)
        bar.pack(fill=tk.X, pady=(2, 0))
        return bar

    def append_log(self, message: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, f"{message}\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def update_stats(self) -> None:
        self.stats_var.set(stats_line(self.stats))
        self.health_bar["value"] = self.stats.health
        self.happiness_bar["value"] = self.stats.happiness
        self.knowledge_bar["value"] = self.stats.knowledge
        self.money_bar["value"] = self.stats.money
        self.update_action_states()
        self.draw_scene()

    def update_action_states(self) -> None:
        for button, entry in zip(self.action_buttons, self.actions):
            if self.stats.age < entry.min_age:
                button.configure(state=tk.DISABLED)
            else:
                button.configure(state=tk.NORMAL)

    def draw_scene(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 520, 220, fill="#b9e6ff", outline="")
        self.canvas.create_rectangle(0, 220, 520, 320, fill="#9ad16f", outline="")
        self.canvas.create_oval(30, 20, 90, 80, fill="#ffe066", outline="")
        self.canvas.create_rectangle(360, 140, 470, 240, fill="#f8c291", outline="#c97c4f")
        self.canvas.create_polygon(350, 140, 420, 90, 490, 140, fill="#c44536", outline="#c44536")
        self.canvas.create_rectangle(395, 180, 430, 240, fill="#704214", outline="")
        self.canvas.create_rectangle(380, 160, 400, 180, fill="#dff9fb", outline="")
        self.canvas.create_rectangle(435, 160, 455, 180, fill="#dff9fb", outline="")

        mood = self._mood_level()
        body_color = "#6c5ce7" if mood == "good" else "#0984e3" if mood == "okay" else "#b2bec3"
        face_color = "#ffeaa7"

        self.canvas.create_oval(230, 150, 290, 210, fill=face_color, outline="")
        self.canvas.create_rectangle(245, 210, 275, 270, fill=body_color, outline="")
        self.canvas.create_line(255, 230, 230, 250, width=4, fill=body_color)
        self.canvas.create_line(265, 230, 300, 250, width=4, fill=body_color)
        self.canvas.create_line(255, 270, 240, 305, width=4, fill=body_color)
        self.canvas.create_line(270, 270, 285, 305, width=4, fill=body_color)

        if mood == "good":
            self.canvas.create_arc(245, 175, 275, 200, start=180, extent=180, style=tk.ARC, width=2)
        elif mood == "okay":
            self.canvas.create_line(245, 190, 275, 190, width=2)
        else:
            self.canvas.create_arc(245, 190, 275, 215, start=0, extent=180, style=tk.ARC, width=2)

        self.canvas.create_oval(250, 170, 255, 175, fill="#2d3436", outline="")
        self.canvas.create_oval(265, 170, 270, 175, fill="#2d3436", outline="")

        self.canvas.create_text(
            260,
            20,
            text=f"{self.stats.age}살 드림 라이프",
            font=("Apple SD Gothic Neo", 12, "bold"),
            fill="#2d3436",
        )

    def _mood_level(self) -> str:
        if self.stats.health >= 70 and self.stats.happiness >= 70:
            return "good"
        if self.stats.health >= 40 and self.stats.happiness >= 40:
            return "okay"
        return "low"

    def handle_action(self, entry: ActionEntry) -> None:
        if self.stats.age > 25:
            return
        if self.stats.age < entry.min_age:
            self.append_log(f"{entry.label}은(는) {entry.min_age}살 이후에 가능합니다.")
            return
        self.append_log(f"{self.stats.age}살: {entry.label} 선택")
        result = entry.action(self.stats)
        event_result = yearly_event(self.stats)
        milestone = milestone_event(self.stats)
        self.stats.clamp()
        self.append_log(result)
        self.append_log(event_result)
        if milestone:
            self.append_log(milestone)
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
    LifeSimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_game()
