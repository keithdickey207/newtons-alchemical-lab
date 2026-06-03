#!/usr/bin/env python3
"""
Newton's Alchmictacle Lab - Interactive Explorer
A text-based virtual reconstruction of Isaac Newton's alchemical laboratory.
"""

import json
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Load data
def load_json(name):
    path = DATA_DIR / f"{name}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

ROOMS_DATA = load_json("rooms")
SUBSTANCES = load_json("substances")
EXPERIMENTS = load_json("experiments")

# State
state = {
    "current_room": "chambers",
    "inventory": ["quill", "notebook_fragment", "antimony_sample"],
    "visited": set(),
    "experiments_performed": set(),
    "decknamen_decoded": set(),
}

def get_room(room_id):
    for r in ROOMS_DATA["rooms"]:
        if r["id"] == room_id:
            return r
    return None

def print_slow(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   NEWTON'S ALCHMICTACLE LAB                                      ║
║   Trinity College, Cambridge — circa 1680s–1690s                 ║
║   "The true Alchymist is the true Natural Philosopher."          ║
╚══════════════════════════════════════════════════════════════════╝
""")

def help_text():
    return """
Commands:
  look / l                    — Describe current location
  go <direction or room>      — Move (e.g., go down, go laboratory)
  examine <object>            — Look closely at something
  perform <experiment>        — Attempt a chymical process
  read <item>                 — Read a notebook or manuscript
  decode <deckname>           — Reveal the modern meaning of a cover name
  symbols                     — Display common alchemical glyphs
  inventory / i               — What you carry
  experiments                 — List known processes
  decknamen                   — List decoded cover names
  help                        — This message
  quit / exit                 — Leave the lab

Tips:
- Type partial names (e.g., "go lab" or "examine star").
- Many objects and experiments are hidden until you look around.
- The notebooks contain real historical language from Newton's papers.
"""

def show_symbols():
    print("\nCommon Alchemical Symbols (from the Chymistry of Isaac Newton font):")
    print("""
Elements:     🜁 Air     🜂 Fire    🜄 Water   🜃 Earth
Mercury:      ☿ (quicksilver / sophic mercury)
Sulfur:       🜍
Salt:         🜔
Gold/Sun:     ☉
Silver/Moon:  ☽
Iron/Mars:    ♂
Copper/Venus: ♀
Antimony:     ♁     (key to the Star Regulus)
Lead/Saturn:  ♄
...and dozens more in the project's custom Unicode font.
""")

def decode_deckname(term):
    term = term.lower().strip()
    d = SUBSTANCES.get("decknamen", {})
    for key, val in d.items():
        if term in key or key in term:
            state["decknamen_decoded"].add(key)
            print(f"\n**{key.title()}**")
            print(f"Modern interpretation: {val['modern']}")
            print(f"Notes: {val['notes']}")
            return
    print(f"No entry found for '{term}'. Try 'green lion', 'star regulus', 'sophic mercury', etc.")

def list_decknamen():
    print("\nDecoded cover names so far:")
    if not state["decknamen_decoded"]:
        print("  (none yet — use 'decode <name>' on things you encounter)")
    else:
        for name in sorted(state["decknamen_decoded"]):
            print(f"  • {name}")

def perform_experiment(name):
    name = name.lower().strip()
    exps = EXPERIMENTS.get("experiments", [])
    for exp in exps:
        if name in exp["name"].lower() or name in exp["id"]:
            if exp["id"] in state["experiments_performed"]:
                print(f"You have already performed: {exp['name']}")
                print(f"Effect: {exp['effect']}")
                return
            print(f"\n=== {exp['name']} ===")
            print_slow(exp["description"], 0.01)
            print(f"\nHistorical note: {exp['historical_note']}")
            print(f"\nModern procedure: {exp['modern_procedure']}")
            print(f"\nEffect in the lab: {exp['effect']}")
            state["experiments_performed"].add(exp["id"])
            if "regulus" in exp["id"]:
                state["inventory"].append("star_regulus_crystal")
                print("\n[You carefully collect a few beautiful crystalline shards.]")
            return
    print("No such experiment known here. Type 'experiments' to list available processes.")

def list_experiments():
    print("\nKnown chymical processes you can attempt:")
    for exp in EXPERIMENTS.get("experiments", []):
        status = "✓" if exp["id"] in state["experiments_performed"] else "○"
        print(f"  {status} {exp['name']}  (try: perform {exp['id']})")

def examine(obj):
    obj = obj.lower().strip()
    room = get_room(state["current_room"])
    
    # Room-specific objects
    if state["current_room"] == "garden_lab" and "furnace" in obj:
        print("The brick furnaces you designed yourself. Multiple units for different heats and durations.")
        return
    if "star" in obj or "regulus" in obj:
        print("Beautiful radiating crystals of antimony regulus. They catch the light like metallic stars. Newton was deeply struck by this 'vegetation' of metals.")
        if "star_regulus_crystal" not in state["inventory"]:
            state["inventory"].append("star_regulus_crystal")
            print("[You pocket a small specimen.]")
        return
    if "notebook" in obj or "lab_notebook" in obj:
        print("\nOne of your laboratory notebooks lies open. The entries are precise but often use cover names.")
        print("A recent entry describes repeated attempts at the 'Star Regulus of Antimony' with varying success depending on the iron used.")
        print("Another section transcribes a long recipe from Eirenaeus Philalethes.")
        return
    if "silica" in obj or "garden" in obj:
        print("A tall glass jar contains a solution in which delicate colored mineral growths are slowly forming — a 'silica garden'. The forms look disturbingly plant-like.")
        return
    if "retort" in obj or "apparatus" in obj:
        print("Glass distillation apparatus of your own specification. Some pieces show the stains of many firings.")
        return
    
    # Generic
    print(f"You examine the {obj} carefully. It yields no immediate new insight, but the act of close observation is itself part of the Work.")

def read_item(item):
    item = item.lower().strip()
    if "notebook" in item or "lab" in item:
        print("\n--- Laboratory Notebook (excerpt, normalized) ---")
        print("I took 1 part ♁ [antimony] & 2 parts fine ♂ filings. Mixed & put into a good crucible.")
        print("Urged with strong fire for 1 hour. Upon cooling found a fine Regulus with several bright stars.")
        print("Repeated the fusion with fresh ♂. The stars were larger and more perfect.")
        print("This Regulus I believe to be of great virtue for the Work.")
        print("--- (Cambridge University Library, Add. 3975 or similar) ---")
        return
    if "index" in item:
        print("\nYour *Index Chemicus* — a massive alphabetical catalogue of substances, authors, and processes drawn from hundreds of alchemical sources.")
        print("Thousands of entries. A lifetime of reading compressed into one volume.")
        return
    if "philalethes" in item or "american" in item:
        print("\nTranscription from Eirenaeus Philalethes (George Starkey / the 'American Philosopher').")
        print("Newton valued this author highly. The recipes are among the most opaque and powerful he encountered.")
        return
    if "praxis" in item:
        print("\nYour *Praxis* manuscript — one of the most cryptic and important of your own compositions on the preparation of the Stone.")
        print("Even you sometimes struggle to reconstruct the exact sequence from these densely symbolic notes.")
        return
    print("You read for a time. The language is veiled, but the underlying experimental intelligence is unmistakable.")

def move(direction):
    room = get_room(state["current_room"])
    direction = direction.lower().strip()
    
    # Flexible matching
    for exit_key, target in room.get("exits", {}).items():
        if direction in exit_key or direction == target or direction in target:
            state["current_room"] = target
            state["visited"].add(target)
            describe_room()
            return
    
    # Try matching room name
    for r in ROOMS_DATA["rooms"]:
        if direction in r["name"].lower() or direction == r["id"]:
            state["current_room"] = r["id"]
            state["visited"].add(r["id"])
            describe_room()
            return
    
    print(f"Cannot go '{direction}' from here. Available exits: {list(room.get('exits', {}).keys())}")

def describe_room():
    room = get_room(state["current_room"])
    if not room:
        print("You are in a strange liminal space between furnaces and manuscripts.")
        return
    
    print(f"\n=== {room['name']} ===")
    print_slow(room["description"], 0.012)
    
    if room["objects"]:
        print("\nThings you notice:", ", ".join(room["objects"]))
    
    print("\nExits:", ", ".join(room.get("exits", {}).keys()) or "none obvious")

def inventory():
    print("\nInventory:")
    for item in state["inventory"]:
        print(f"  • {item.replace('_', ' ')}")
    if not state["inventory"]:
        print("  (empty hands)")

def main_loop():
    banner()
    print("You have returned to your chambers at Trinity. The furnaces below call to you.")
    print("Type 'help' for commands. Type 'quit' to leave the Work for now.\n")
    
    state["visited"].add("chambers")
    describe_room()
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nThe fires are banked. You step away from the Work.")
            break
        
        if not cmd:
            continue
        if cmd in ("quit", "exit", "q"):
            print("The retorts cool. The stars on the regulus fade into memory. Until next time, chymist.")
            break
        if cmd in ("help", "h", "?"):
            print(help_text())
            continue
        if cmd in ("look", "l", "describe"):
            describe_room()
            continue
        if cmd.startswith("go "):
            move(cmd[3:])
            continue
        if cmd.startswith(("examine ", "x ", "look at ")):
            obj = cmd.split(maxsplit=1)[1] if " " in cmd else ""
            examine(obj)
            continue
        if cmd.startswith("perform "):
            perform_experiment(cmd[8:])
            continue
        if cmd.startswith("read "):
            read_item(cmd[5:])
            continue
        if cmd.startswith("decode "):
            decode_deckname(cmd[7:])
            continue
        if cmd in ("symbols", "glyphs", "font"):
            show_symbols()
            continue
        if cmd in ("inventory", "i", "inv"):
            inventory()
            continue
        if cmd in ("experiments", "procs", "processes"):
            list_experiments()
            continue
        if cmd in ("decknamen", "decknames", "cover names"):
            list_decknamen()
            continue
        if cmd in ("where", "location"):
            room = get_room(state["current_room"])
            print(f"You are in the {room['name']}.")
            continue
        
        # Easter eggs / direct references
        if "diamond" in cmd:
            print("The dog Diamond is nowhere to be seen. (The candle story is probably apocryphal anyway.)")
            continue
        if "green lion" in cmd:
            decode_deckname("green lion")
            continue
        if "regulus" in cmd:
            decode_deckname("star regulus")
            continue
        
        print("The Work does not understand that command. Try 'help'.")

if __name__ == "__main__":
    main_loop()
