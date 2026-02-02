#!/usr/bin/env python3
"""Action RPG mini game with drops and equipment."""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk


@dataclass
class Equipment:
    name: str
    attack: int = 0
    defense: int = 0


@dataclass
class Player:
    x: float = 400
    y: float = 260
    speed: float = 4.0
    vy: float = 0.0
    on_ground: bool = True
    jump_strength: float = 12.0
    max_hp: int = 120
    hp: int = 120
    level: int = 1
    exp: int = 0
    exp_to_next: int = 30
    gold: int = 0
    base_attack: int = 8
    base_defense: int = 2
    weapon: Equipment | None = None
    armor: Equipment | None = None

    def attack_power(self) -> int:
        bonus = 0
        if self.weapon:
            bonus += self.weapon.attack
        if self.armor:
            bonus += self.armor.attack
        return self.base_attack + bonus

    def defense_power(self) -> int:
        bonus = 0
        if self.weapon:
            bonus += self.weapon.defense
        if self.armor:
            bonus += self.armor.defense
        return self.base_defense + bonus

    def gain_exp(self, amount: int) -> bool:
        self.exp += amount
        leveled = False
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.35 + 5)
            self.max_hp += 15
            self.hp = min(self.max_hp, self.hp + 20)
            self.base_attack += 2
            self.base_defense += 1
            leveled = True
        return leveled


@dataclass
class Monster:
    x: float
    y: float
    hp: int
    max_hp: int
    attack: int
    exp_reward: int
    gold_reward: int
    speed: float


@dataclass
class Drop:
    x: float
    y: float
    kind: str
    amount: int = 0
    equipment: Equipment | None = None


@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    monsters: list[Monster] = field(default_factory=list)
    drops: list[Drop] = field(default_factory=list)
    inventory: list[Equipment] = field(default_factory=list)
    keys: set[str] = field(default_factory=set)
    combo_timer: int = 0


class MapleHuntGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("메이플 훈트: 미니 액션 RPG")
        self.root.geometry("1060x720")
        self.root.resizable(False, False)

        self.ground_y = 440
        self.player_ground_offset = 52
        self.gravity = 0.6

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Apple SD Gothic Neo", 20, "bold"))
        style.configure("Stat.TLabel", font=("Apple SD Gothic Neo", 10, "bold"))
        style.configure("Info.TLabel", font=("Apple SD Gothic Neo", 10))
        style.configure("Action.TButton", font=("Apple SD Gothic Neo", 10, "bold"))

        container = ttk.Frame(root, padding=14)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container)
        header.pack(fill=tk.X)
        ttk.Label(header, text="메이플 훈트: 미니 액션 RPG", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="좌우 이동은 방향키/A,D, 점프는 스페이스, 공격은 J 키! 인벤토리에서 장비를 착용하세요.",
            style="Info.TLabel",
            foreground="#4a4a4a",
        ).pack(anchor=tk.W, pady=(4, 10))

        main = ttk.Frame(container)
        main.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(main)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right_panel = ttk.Frame(main)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.state = GameState()
        self.state.player.y = self.ground_y - self.player_ground_offset
        self.stats_var = tk.StringVar(value="")
        self.hp_var = tk.StringVar(value="")
        self.attack_var = tk.StringVar(value="")
        self.defense_var = tk.StringVar(value="")
        self.gold_var = tk.StringVar(value="")
        self.exp_var = tk.StringVar(value="")
        self.weapon_var = tk.StringVar(value="")
        self.armor_var = tk.StringVar(value="")

        stats_box = ttk.LabelFrame(left_panel, text="용사 정보")
        stats_box.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(stats_box, textvariable=self.stats_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Label(stats_box, textvariable=self.hp_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Label(stats_box, textvariable=self.exp_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Label(stats_box, textvariable=self.attack_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Label(stats_box, textvariable=self.defense_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Label(stats_box, textvariable=self.gold_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Label(stats_box, textvariable=self.weapon_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)
        ttk.Label(stats_box, textvariable=self.armor_var, style="Info.TLabel").pack(anchor=tk.W, padx=8, pady=2)

        inventory_box = ttk.LabelFrame(left_panel, text="인벤토리")
        inventory_box.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(
            inventory_box,
            text="인벤토리 열기 (I)",
            style="Action.TButton",
            command=self.open_inventory,
        ).pack(fill=tk.X, padx=8, pady=8)

        self.log = tk.Text(
            left_panel,
            height=16,
            wrap=tk.WORD,
            state=tk.DISABLED,
            background="#f7f7f7",
            relief=tk.FLAT,
        )
        self.log.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right_panel, width=720, height=520, background="#dff5ff", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.inventory_window: tk.Toplevel | None = None
        self.inventory_list: tk.Listbox | None = None
        self.drop_images = self.create_drop_images()

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        self.spawn_initial_monsters()
        self.append_log("메이플 숲에 오신 것을 환영합니다! 몬스터를 처치하세요.")
        self.update_ui()
        self.loop()

    def create_drop_images(self) -> dict[str, tk.PhotoImage]:
        images: dict[str, tk.PhotoImage] = {}

        def make_icon(base: str, accent: str) -> tk.PhotoImage:
            icon = tk.PhotoImage(width=14, height=14)
            icon.put(base, to=(0, 0, 13, 13))
            icon.put(accent, to=(4, 4, 9, 9))
            icon.put("#ffffff", to=(6, 2, 7, 11))
            icon.put("#ffffff", to=(2, 6, 11, 7))
            return icon

        images["exp"] = make_icon("#74b9ff", "#3c91e6")
        images["gold"] = make_icon("#feca57", "#f5a623")
        images["gem"] = make_icon("#55efc4", "#00b894")
        images["gear"] = make_icon("#a29bfe", "#6c5ce7")
        return images

    def append_log(self, message: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, f"{message}\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def update_ui(self) -> None:
        player = self.state.player
        self.stats_var.set(f"레벨 {player.level} | HP {player.hp}/{player.max_hp}")
        self.hp_var.set(f"이동 속도: {player.speed:.1f}")
        self.exp_var.set(f"EXP {player.exp}/{player.exp_to_next}")
        self.attack_var.set(f"공격력: {player.attack_power()}")
        self.defense_var.set(f"방어력: {player.defense_power()}")
        self.gold_var.set(f"골드: {player.gold}")
        self.weapon_var.set(f"무기: {player.weapon.name if player.weapon else '없음'}")
        self.armor_var.set(f"방어구: {player.armor.name if player.armor else '없음'}")

        if self.inventory_list is not None:
            self.inventory_list.delete(0, tk.END)
            for item in self.state.inventory:
                desc = f"{item.name} (공격 +{item.attack}, 방어 +{item.defense})"
                self.inventory_list.insert(tk.END, desc)

    def on_key_press(self, event: tk.Event) -> None:
        if event.keysym:
            self.state.keys.add(event.keysym.lower())
        if event.keysym == "space":
            self.jump_player()
        if event.keysym and event.keysym.lower() in ("j", "z"):
            self.attack_monsters()
        if event.keysym and event.keysym.lower() == "i":
            self.open_inventory()

    def on_key_release(self, event: tk.Event) -> None:
        if event.keysym:
            self.state.keys.discard(event.keysym.lower())

    def loop(self) -> None:
        self.handle_movement()
        self.update_monsters()
        self.collect_drops()
        self.draw_scene()
        self.update_ui()
        self.root.after(40, self.loop)

    def handle_movement(self) -> None:
        player = self.state.player
        dx = 0.0
        if "left" in self.state.keys or "a" in self.state.keys:
            dx -= player.speed
        if "right" in self.state.keys or "d" in self.state.keys:
            dx += player.speed

        player.x = min(700, max(20, player.x + dx))

        player.vy += self.gravity
        player.y += player.vy

        ground_limit = self.ground_y - self.player_ground_offset
        if player.y >= ground_limit:
            player.y = ground_limit
            player.vy = 0.0
            player.on_ground = True

        player.y = max(40, player.y)

    def jump_player(self) -> None:
        player = self.state.player
        if player.on_ground:
            player.vy = -player.jump_strength
            player.on_ground = False

    def spawn_initial_monsters(self) -> None:
        for _ in range(4):
            self.state.monsters.append(self.create_monster())

    def create_monster(self) -> Monster:
        level = random.randint(1, 3 + self.state.player.level // 2)
        hp = 20 + level * 8
        attack = 4 + level * 2
        exp = 8 + level * 4
        gold = 6 + level * 3
        speed = random.uniform(1.2, 2.0)
        x = random.uniform(80, 640)
        y = self.ground_y - 20
        return Monster(x=x, y=y, hp=hp, max_hp=hp, attack=attack, exp_reward=exp, gold_reward=gold, speed=speed)

    def update_monsters(self) -> None:
        player = self.state.player
        for monster in self.state.monsters:
            dx = player.x - monster.x
            dy = player.y - monster.y
            dist = max(1.0, (dx**2 + dy**2) ** 0.5)
            monster.x += monster.speed * dx / dist
            monster.y += monster.speed * dy / dist

            if dist < 26:
                damage = max(1, monster.attack - player.defense_power())
                player.hp = max(0, player.hp - damage)
                self.state.combo_timer = 15
                if player.hp == 0:
                    self.append_log("용사가 쓰러졌습니다! 휴식 후 다시 도전하세요.")
                    player.hp = player.max_hp
                    player.gold = max(0, player.gold - 20)
                    player.x = 400
                    player.y = self.ground_y - self.player_ground_offset
                    self.state.drops.clear()
                    break

        while len(self.state.monsters) < 6:
            self.state.monsters.append(self.create_monster())

    def attack_monsters(self) -> None:
        player = self.state.player
        hit = False
        for monster in list(self.state.monsters):
            dist = ((monster.x - player.x) ** 2 + (monster.y - player.y) ** 2) ** 0.5
            if dist < 60:
                damage = player.attack_power() + random.randint(0, 4)
                monster.hp = max(0, monster.hp - damage)
                hit = True
                if monster.hp == 0:
                    self.handle_monster_down(monster)
        if hit:
            self.append_log("검을 휘둘렀다!")

    def handle_monster_down(self, monster: Monster) -> None:
        self.state.monsters.remove(monster)
        player = self.state.player
        leveled = player.gain_exp(monster.exp_reward)
        player.gold += monster.gold_reward
        self.append_log(f"몬스터 처치! 경험치 +{monster.exp_reward}, 골드 +{monster.gold_reward}")
        if leveled:
            self.append_log(f"레벨 업! Lv.{player.level} 달성")
        self.spawn_drops(monster.x, monster.y)

    def spawn_drops(self, x: float, y: float) -> None:
        if random.random() < 0.75:
            self.state.drops.append(Drop(x=x + random.uniform(-12, 12), y=y, kind="exp", amount=6))
        if random.random() < 0.7:
            self.state.drops.append(Drop(x=x, y=y + random.uniform(-12, 12), kind="gold", amount=8))
        if random.random() < 0.45:
            self.state.drops.append(Drop(x=x - 8, y=y - 4, kind="gem", amount=12))
        if random.random() < 0.35:
            self.state.drops.append(Drop(x=x + 6, y=y + 6, kind="gear", equipment=self.random_equipment()))

    def random_equipment(self) -> Equipment:
        prefixes = ["빛나는", "단단한", "불꽃", "얼음", "바람", "별빛"]
        weapons = ["검", "창", "활", "마검", "대검"]
        armors = ["망토", "갑옷", "부츠", "장갑"]
        if random.random() < 0.5:
            name = f"{random.choice(prefixes)} {random.choice(weapons)}"
            return Equipment(name=name, attack=random.randint(3, 7), defense=random.randint(0, 2))
        name = f"{random.choice(prefixes)} {random.choice(armors)}"
        return Equipment(name=name, attack=random.randint(0, 2), defense=random.randint(3, 7))

    def collect_drops(self) -> None:
        player = self.state.player
        for drop in list(self.state.drops):
            dist = ((drop.x - player.x) ** 2 + (drop.y - player.y) ** 2) ** 0.5
            if dist < 25:
                if drop.kind == "exp":
                    player.gain_exp(drop.amount)
                    self.append_log(f"경험치 구슬 +{drop.amount}")
                elif drop.kind == "gold":
                    player.gold += drop.amount
                    self.append_log(f"골드 주머니 +{drop.amount}")
                elif drop.kind == "gem":
                    player.gold += drop.amount
                    player.hp = min(player.max_hp, player.hp + 6)
                    self.append_log("생명의 수정! HP 회복")
                elif drop.kind == "gear" and drop.equipment:
                    self.state.inventory.append(drop.equipment)
                    self.append_log(f"장비 획득: {drop.equipment.name}")
                self.state.drops.remove(drop)

    def equip_selected(self) -> None:
        if self.inventory_list is None:
            return
        selection = self.inventory_list.curselection()
        if not selection:
            return
        index = selection[0]
        item = self.state.inventory.pop(index)
        if "갑옷" in item.name or "망토" in item.name or "부츠" in item.name or "장갑" in item.name:
            if self.state.player.armor:
                self.state.inventory.append(self.state.player.armor)
            self.state.player.armor = item
            self.append_log(f"방어구 착용: {item.name}")
        else:
            if self.state.player.weapon:
                self.state.inventory.append(self.state.player.weapon)
            self.state.player.weapon = item
            self.append_log(f"무기 착용: {item.name}")

    def discard_selected(self) -> None:
        if self.inventory_list is None:
            return
        selection = self.inventory_list.curselection()
        if not selection:
            return
        item = self.state.inventory.pop(selection[0])
        self.append_log(f"장비 버림: {item.name}")

    def draw_scene(self) -> None:
        self.canvas.delete("all")
        self.draw_background()
        self.draw_drops()
        self.draw_monsters()
        self.draw_player()
        self.draw_ui_effects()

    def draw_background(self) -> None:
        self.canvas.create_rectangle(0, 0, 720, 200, fill="#b9e6ff", outline="")
        self.canvas.create_rectangle(0, 200, 720, 520, fill="#93d37a", outline="")
        self.canvas.create_rectangle(0, self.ground_y, 720, 520, fill="#6ab04c", outline="")
        for x in range(0, 720, 120):
            self.canvas.create_oval(x + 10, 40, x + 90, 110, fill="#fff0a6", outline="")
        for x in range(60, 720, 160):
            self.canvas.create_rectangle(x, 260, x + 20, 340, fill="#8e5a2a", outline="")
            self.canvas.create_oval(x - 30, 210, x + 50, 290, fill="#4caf50", outline="")
            self.canvas.create_oval(x - 40, 220, x + 60, 310, fill="#43a047", outline="")

        self.canvas.create_rectangle(520, 260, 680, 380, fill="#f5c38a", outline="#d19057")
        self.canvas.create_polygon(500, 260, 600, 200, 700, 260, fill="#d3544a", outline="#d3544a")
        self.canvas.create_rectangle(575, 310, 615, 380, fill="#855c3a", outline="")

    def draw_player(self) -> None:
        player = self.state.player
        self.canvas.create_oval(player.x - 14, player.y - 30, player.x + 14, player.y - 2, fill="#ffdd99", outline="")
        self.canvas.create_rectangle(player.x - 16, player.y - 2, player.x + 16, player.y + 32, fill="#6c5ce7", outline="")
        self.canvas.create_line(player.x - 6, player.y + 12, player.x - 26, player.y + 20, width=4, fill="#6c5ce7")
        self.canvas.create_line(player.x + 6, player.y + 12, player.x + 26, player.y + 20, width=4, fill="#6c5ce7")
        self.canvas.create_line(player.x - 6, player.y + 32, player.x - 12, player.y + 52, width=4, fill="#6c5ce7")
        self.canvas.create_line(player.x + 6, player.y + 32, player.x + 12, player.y + 52, width=4, fill="#6c5ce7")
        self.canvas.create_oval(player.x - 5, player.y - 22, player.x - 1, player.y - 18, fill="#2d3436", outline="")
        self.canvas.create_oval(player.x + 1, player.y - 22, player.x + 5, player.y - 18, fill="#2d3436", outline="")
        self.canvas.create_arc(player.x - 6, player.y - 16, player.x + 6, player.y - 8, start=180, extent=180, style=tk.ARC, width=2)

    def draw_monsters(self) -> None:
        for monster in self.state.monsters:
            color = "#f78fb3" if monster.max_hp < 40 else "#63cdda"
            self.canvas.create_oval(monster.x - 16, monster.y - 16, monster.x + 16, monster.y + 16, fill=color, outline="")
            self.canvas.create_oval(monster.x - 6, monster.y - 4, monster.x - 2, monster.y, fill="#2d3436", outline="")
            self.canvas.create_oval(monster.x + 2, monster.y - 4, monster.x + 6, monster.y, fill="#2d3436", outline="")
            self.canvas.create_line(monster.x - 6, monster.y + 6, monster.x + 6, monster.y + 6, width=2)
            hp_ratio = monster.hp / monster.max_hp
            bar_width = 28
            self.canvas.create_rectangle(
                monster.x - bar_width / 2,
                monster.y - 26,
                monster.x + bar_width / 2,
                monster.y - 20,
                fill="#dfe6e9",
                outline="",
            )
            self.canvas.create_rectangle(
                monster.x - bar_width / 2,
                monster.y - 26,
                monster.x - bar_width / 2 + bar_width * hp_ratio,
                monster.y - 20,
                fill="#ff6b6b",
                outline="",
            )

    def draw_drops(self) -> None:
        for drop in self.state.drops:
            icon = self.drop_images.get(drop.kind)
            if icon is not None:
                self.canvas.create_image(drop.x, drop.y, image=icon)

    def open_inventory(self) -> None:
        if self.inventory_window and self.inventory_window.winfo_exists():
            self.inventory_window.focus()
            return
        self.inventory_window = tk.Toplevel(self.root)
        self.inventory_window.title("인벤토리")
        self.inventory_window.geometry("340x360")
        self.inventory_window.resizable(False, False)

        frame = ttk.Frame(self.inventory_window, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        self.inventory_list = tk.Listbox(frame, height=10)
        self.inventory_list.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(button_frame, text="장비 착용", style="Action.TButton", command=self.equip_selected).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4)
        )
        ttk.Button(button_frame, text="장비 버리기", style="Action.TButton", command=self.discard_selected).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0)
        )

        self.inventory_window.protocol("WM_DELETE_WINDOW", self.close_inventory)
        self.update_ui()

    def close_inventory(self) -> None:
        if self.inventory_window:
            self.inventory_window.destroy()
        self.inventory_window = None
        self.inventory_list = None

    def draw_ui_effects(self) -> None:
        if self.state.combo_timer > 0:
            self.canvas.create_text(
                620,
                40,
                text="콤보!",
                font=("Apple SD Gothic Neo", 16, "bold"),
                fill="#fdcb6e",
            )
            self.state.combo_timer -= 1


def run_game() -> None:
    root = tk.Tk()
    MapleHuntGame(root)
    root.mainloop()


if __name__ == "__main__":
    run_game()
