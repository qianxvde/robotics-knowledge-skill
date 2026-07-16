---
name: robotics-tutorial
description: Search and apply the Robotics_Tutorial Markdown knowledge base and Robotics_Theory LaTeX knowledge base when working on robotics engineering, robot learning, RL/AMP/PPO, locomotion, humanoids, manipulation, motion control, simulation, sim-to-real, perception, SLAM, planning, ROS2, or robotics C++ infrastructure. For robotics code changes, debugging, architecture, reward/observation design, deployment, and validation, use this skill to search both knowledge bases by task-specific Chinese and English keywords before editing, read the relevant sections, and incorporate their engineering experience without overriding repository contracts or user requirements.
---

# Robotics Tutorial and Theory

Use two live knowledge bases discovered by the bundled search helper:

- `Robotics_Tutorial`: Markdown engineering tutorials.
- `Robotics_Theory`: LaTeX theory and practice chapters under `src/`.

Do not preload either repository. Search them progressively so the model context
stays focused and local updates are picked up automatically.

## Mandatory coding workflow

For every robotics task that creates or changes code:

1. Classify the task by subsystem, algorithm, failure mode, and lifecycle stage.
2. Inspect the target repository before assuming its framework or contracts.
3. Derive 2-6 narrow Chinese/English search terms from the request and code. Include:
   - the mechanism, such as `AMP`, `teacher student`, or `接触奖励`;
   - the framework or subsystem, such as `mjlab`, `MuJoCo`, or `ROS2`;
   - the failure or goal, such as `reward hacking`, `延迟`, or `sim2real`.
4. Search both knowledge bases before editing.
5. Read the complete relevant sections around the best hits. Do not rely on a
   one-line match or search snippet.
6. Translate the sources into repository-specific decisions, then implement.
7. Validate progressively and report which source files materially influenced
   the result.

For read-only robotics analysis, use the same search workflow whenever the answer
depends on engineering judgment. A simple stable fact may need only local inspection.

Announce when this skill triggers a knowledge search or when a source changes the
implementation plan.

## Search procedure

Prefer the bundled deterministic helper. Resolve the installed skill directory from
the host skill home instead of assuming a machine-specific path:

- Codex: `${CODEX_HOME:-$HOME/.codex}/skills/robotics-tutorial`
- Cursor personal: `$HOME/.cursor/skills/robotics-tutorial`
- Cursor project: `<repo>/.cursor/skills/robotics-tutorial`
- Override: `ROBOTICS_TUTORIAL_SKILL_ROOT`

```bash
SKILL_ROOT="${ROBOTICS_TUTORIAL_SKILL_ROOT:-}"
if [ -z "$SKILL_ROOT" ]; then
  for candidate in \
    "${CODEX_HOME:-$HOME/.codex}/skills/robotics-tutorial" \
    "$HOME/.cursor/skills/robotics-tutorial"
  do
    if [ -f "$candidate/scripts/search_robotics_knowledge.py" ]; then
      SKILL_ROOT=$candidate
      break
    fi
  done
fi
python "$SKILL_ROOT/scripts/search_robotics_knowledge.py" \
  "AMP" "adversarial motion prior" "模仿学习"
```

Useful options:

```bash
python "$SKILL_ROOT/scripts/search_robotics_knowledge.py" \
  --root theory "teacher student" "privileged learning"

python "$SKILL_ROOT/scripts/search_robotics_knowledge.py" \
  --regex --context 2 'sim.?to.?real|域随机化|domain randomization'

python "$SKILL_ROOT/scripts/search_robotics_knowledge.py" \
  --print-roots
```

The helper searches tutorial Markdown and theory source Markdown/LaTeX. It
excludes Git metadata, build products, generated figures, PDFs, logs, and LaTeX
auxiliary files. It finds roots through CLI overrides, environment variables,
repository-relative discovery, or a user configuration file; use `--help` for
the complete interface.

If the helper is unavailable, locate the two roots first. Prefer
`ROBOTICS_TUTORIAL_ROOT` and `ROBOTICS_THEORY_ROOT`, or the repository's
`knowledge/` directory. Then use `rg` with narrow bilingual terms and source-only
globs. Broaden with synonyms and filename search only when initial matches fail.

## Reading Markdown and LaTeX

For Markdown:

- Use `SUMMARY.md` and `00_项目导航/项目总导航.md` only for routing.
- Read the matching heading and its complete subsection.
- Follow direct links only when required to understand the recommendation.

For LaTeX:

- Treat `src/book.tex` and `src/vol_*.tex` as routing files.
- Prefer chapter sources under `src/parts/`.
- Use `\\chapter`, `\\section`, and `\\subsection` boundaries for context.
- Trace a nearby `\\input{...}` when a match is in a part or volume file.
- Ignore formatting macros and build artifacts unless the task concerns LaTeX.

Do not claim knowledge-base support unless the relevant source section was read.

## Topic routing

| Task | Tutorial areas | Theory areas |
|---|---|---|
| RL, PPO, rewards, observations, curricula | `01_数学/70_强化学习数学`, `06_具身智能`, `05_运动控制` | `src/parts/P6_rl`, `src/parts/P8_rl_motion_control` |
| AMP, imitation, privileged learning, distillation | `06_具身智能`, `05_运动控制` | `P8_rl_motion_control/prac_motion_imitation.tex`, `prac_imitation.tex`, `prac_privileged.tex` |
| Humanoid or legged locomotion, recovery, WBC | `05_运动控制`, `06_具身智能` | `src/parts/P7_legged`, `P8_rl_motion_control/prac_humanoid_loco.tex`, `prac_humanoid_wbc.tex` |
| MuJoCo, mjlab, Isaac, contacts, actuators | `05_运动控制`, `01_数学/80_接触力学` | `P8_rl_motion_control/prac_ecosystem.tex`, `prac_physics.tex`, `prac_actuator.tex`, `P4_control/contact_mechanics.tex` |
| Sim-to-real, DR, deployment, diagnostics | `05_运动控制`, `06_具身智能`, `02_C++基础与进阶` | `P8_rl_motion_control/prac_sim2real.tex`, `prac_domain_rand.tex`, `prac_diagnostics.tex` |
| Vision, visuomotor, embodied perception | `06_具身智能`, `03_SLAM` | `P8_rl_motion_control/prac_visuomotor.tex`, `prac_tennis_perception.tex`, `P2_slam` |
| Dynamics, MPC, optimal control, safety | `01_数学/40_控制理论`, `01_数学/50_刚体动力学`, `04_移动机器人规控` | `src/parts/P4_control`, `src/parts/P3_planning` |
| Manipulation, mobile manipulation | `05_运动控制` | `src/parts/P3b_manipulator`, `src/parts/P9_mobile_manip` |
| SLAM and estimation | `03_SLAM`, `01_数学/60_概率与估计` | `src/parts/P1_estimation`, `P2_slam`, `P5_frontier` |
| C++, ROS2, real-time systems, testing | `02_C++基础与进阶` | `src/parts/P5_engineering`, practice sections in relevant chapters |

Treat this table as routing help, not a substitute for keyword search.

## Applying source guidance

Use this priority order when sources differ:

1. Explicit user requirements and safety constraints.
2. Repository APIs, tests, assets, deployment contracts, and measured logs.
3. Task-specific guidance from the two knowledge bases.
4. General robotics conventions.

The sources provide methodology, not guaranteed compatibility with an installed
library version. Verify every API, dimension, frame convention, frequency, and
file path in the target repository.

For conflicts, identify whether they are theoretical, framework-specific, or
empirical; prefer measured repository behavior for implementation details;
preserve the theoretical invariant where possible; explain the tradeoff.

## Engineering checklist

Before editing, establish:

- observation, action, command, reward, termination, event, and curriculum contracts;
- coordinate frames, units, rates, latency, history, and reset semantics;
- train/play/deploy parity and privileged-versus-deployable observations;
- dataset provenance, mirroring, contact labels, and action/joint ordering;
- checkpoint compatibility and migration requirements;
- success metrics and failure diagnostics.

Validate in increasing cost order:

1. Static imports, paths, shapes, and config construction.
2. Focused unit or contract tests.
3. Zero/random policy checks for new RL environments.
4. Short smoke training or rollout when authorized.
5. Per-term rewards, episode length, terminations, KL, entropy/noise, value loss,
   critic advantages, and discriminator diagnostics.
6. Sim-to-sim and deployment-frequency/latency checks before real hardware.

Do not tune from total reward alone. Do not broaden the task distribution before
the prerequisite behavior is measurable.

## Reporting

For substantial work, include a compact note naming the tutorial and theory source
files that influenced the implementation, the applied point, validation performed,
and any remaining unvalidated risk. If searches find no relevant guidance, say so
and continue from repository evidence. Never invent a chapter or recommendation.
