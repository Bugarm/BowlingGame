# AGENTS.md

Instructions for any coding agent working in this repository.

This project is a **XR For Meta Quest 3 Bowling Game** game built in Unity. Work is done **one phase at a time**. Do not implement the whole game in a single pass. Every completed step must be written up in `Journey/` so the folder becomes a tutorial of how the game was built.

---

## What this project is

A demonstration of a bowling game for Meta Quest 3 Single Player game. 

---

## Non-negotiable rules

1. **One phase per stretch of work.** Implement the next unfinished phase from the roadmap below. Stop when that phase is playable or visibly done. Do not start the following phase unless the user explicitly asks. So stick to the prompt.
2. **Do not "just finish the game."** A request like "keep going" still means *the next phase*, not the rest of the roadmap.
3. **Log the work in `Journey/`** before considering a phase complete. The log is part of the deliverable, not a nice-to-have.
4. **Use `ConceptArt/` as the look target.** 
5. **Do not invent extra modes.** No local multiplayer, no online, no extra characters, no menus beyond what the current phase needs, no mobile touch controls.
6. **Prefer small, named C# scripts** over one god object. New runtime code goes under `Assets/Scripts/`.
7. **Do not rewrite working systems** from an earlier phase unless the current phase cannot proceed without it. If you must change an older system, say so in the Journey entry and why.
8. **Drive Unity programmatically**

   Use Unity automation in this order of preference:

   1. **Unity CLI MCP** — Prefer the MCP tools exposed by the new Unity CLI when they are available to the agent.
   2. **New Unity CLI + `com.unity.pipeline`** — If an appropriate MCP tool is unavailable, use the standalone `unity` CLI and Pipeline commands. Discover available commands and their current syntax from the installed CLI rather than guessing them. Prefer built-in Pipeline commands and project-specific `[CliCommand]` tools; use live C# evaluation only when no suitable structured command exists.
   3. **Legacy Unity CLI** — If the new Unity CLI, Pipeline, or required capability is unavailable, fall back to the installed Unity Editor executable (`Unity.exe` on Windows) using `-batchmode`, `-projectPath`, `-executeMethod`, `-runTests`, build arguments, and scripts under `Assets/Editor/` as appropriate.
   4. **Stop on automation failure** — If neither the new nor legacy automation path can perform the required operation, notify the user and stop. Do not silently replace automation with instructions to click through the Unity Editor.

   Scene setup, asset import/refresh, Play-mode checks, screenshots, tests, validation, and player builds should therefore be performed through the highest available automation layer.

   See [Unity CLI](#unity-cli).
10. Test using the XR Interaction Simulator GameObject.
11. Operational CLI and editor **gotchas** (not gameplay, not the roadmap) live in [`memory.md`](memory.md).

---

## Gameplay rules

Derived from a normal Bowling Game with one Lane

### Court and space

- Wolrd is 3D
- Game is single-player


### Movement and hitting

- Joystick of the controller (not hands)

---

## Visual direction

Look in the ConceptArt folder.


## Journey log (required)

`Journey/` is a public tutorial of the build. Write so a stranger can follow along.

### When to write

After every phase, and after any other meaningful step (a hard physics fix, a control change, a visual milestone).

### File naming

```
Journey/NNN-short-kebab-title.md
```

Zero-pad the number (`001`, `002`, …). Numbers are chronological, not phase numbers (a phase may take more than one entry).

Screenshots go in `Journey/screenshots/` as `NNN-short-description.png` (or `.jpg`) and are linked from the matching entry.

### Entry template

Copy this into each new file:

```markdown
# NNN — Title

- **Date:** YYYY-MM-DD
- **Phase:** N — name
- **Goal:** one sentence

## Why this step

A short paragraph a future reader needs.

## What I did

- Bullet the concrete changes (files, scene objects, rules implemented).
- Call out non-obvious decisions and rejected alternatives.
- If Unity CLI was used: the exact command and the log path.
- If Blender MCP was used: which tools, what was exported, and where.

## How to try it

1. The Unity CLI command to refresh / open / verify (copy-pasteable).
2. Open `Assets/Scenes/SampleScene.unity` (or the scene you used) if the user wants to look in the Editor.
3. Press Play.
4. Exact keys / what to look for.

## Screenshot

![description](screenshots/NNN-description.png)

What the image is showing.

## What works / what does not

- Works: …
- Not yet: … (this is the next phase, not leftover chores inside this one)

## Next

One sentence: the next phase and nothing else.
```

### Screenshots

Take them when something becomes visible: first court, first bounce, first jump, first rally, first AI hit, HUD, art pass.

Prefer a real Game view / Play mode capture over a mock. If the Unity editor is available, capture from there. If not, note that in the entry and skip the image rather than faking one.

Do **not** generate concept-style images with an image model and present them as game screenshots.

---

---

## What "done" means for a session

A session is done when **all** of the following are true:

1. Only the agreed phase (or a clearly scoped fix) changed.
2. Play mode was thought through: the exit check can actually be performed.
3. Unity CLI was used for any compile, import, scene save, test, or screenshot the phase needed. The command is in the Journey entry.
4. Any new visible mesh was authored through the Blender MCP (or the phase needed no new mesh).
5. A new `Journey/NNN-*.md` entry is written, with a screenshot if anything visual changed.
6. The "Next" line of that entry names the following roadmap phase.

Do not leave placeholder comments like `// TODO: add AI later` as a substitute for the roadmap. The roadmap already knows.

---

## Starting a new session

1. Read this file.
2. Open `ConceptArt'
3. Read `Journey/README.md` and the **latest** Journey entry.
4. Identify the next unfinished phase.
5  Read memory.md files for any gotchas. (In the Unity Scenes folder there is a base template called 'ExampleTemplate.unity' to help you understand how the Simulartor and XR origin are setup.)
6. Build project as per prompt and test. 
7. Write the Journey entry.
