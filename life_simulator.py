#!/usr/bin/env python3
"""Simple life simulator raising game (CLI)."""

from __future__ import annotations

import random
from dataclasses import dataclass
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


def print_stats(stats: Stats) -> None:
    bar = lambda value: "█" * (value // 10) + "·" * (10 - value // 10)
    print(
        f"나이: {stats.age}살 | 건강 {stats.health:3d} {bar(stats.health)} | "
        f"행복 {stats.happiness:3d} {bar(stats.happiness)} | "
        f"지식 {stats.knowledge:3d} {bar(stats.knowledge)} | "
        f"돈 {stats.money:3d}"
    )


def choose_action() -> str:
    print("\n행동을 선택하세요:")
    print("1) 공부  2) 놀기  3) 아르바이트  4) 운동  5) 휴식  6) 저장하고 종료")
    return input("> ").strip()


def run_game() -> None:
    stats = Stats()
    print("\n==== 간단한 인생 시뮬레이터 키우기 ====")
    print("6살부터 25살까지, 매년 하나의 행동을 선택합니다.")

    actions: dict[str, Action] = {
        "1": study,
        "2": play,
        "3": part_time,
        "4": exercise,
        "5": rest,
    }

    while stats.age <= 25:
        print("\n-------------------------------------")
        print_stats(stats)
        choice = choose_action()
        if choice == "6":
            print("게임을 저장하지 않고 종료합니다.")
            break
        if choice not in actions:
            print("올바른 번호를 입력해주세요.")
            continue

        result = actions[choice](stats)
        print(result)
        print(yearly_event(stats))
        stats.clamp()
        stats.age += 1

        if stats.health == 0 or stats.happiness == 0:
            print("체력 또는 행복이 0이 되어 게임이 종료되었습니다.")
            break

    print(end_summary(stats))


if __name__ == "__main__":
    run_game()
