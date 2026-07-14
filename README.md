# Robotics Knowledge Skill

A portable Codex skill that searches two complementary robotics knowledge bases
before robotics engineering work:

- [Robotics_Tutorial](https://github.com/Michael-Jetson/Robotics_Tutorial):
  Markdown tutorials and practical engineering notes.
- [Robotics_Theory](https://github.com/Michael-Jetson/Robotics_Theory): LaTeX
  sources covering robotics theory and implementation practice.

The references are pinned as Git submodules. The skill searches the source files
on demand instead of loading the full corpus into the model context.

## Repository layout

```text
.
├── knowledge/
│   ├── Robotics_Tutorial/       # Git submodule
│   └── Robotics_Theory/         # Git submodule
├── scripts/
│   └── install.sh
└── skill/
    └── robotics-tutorial/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── scripts/search_robotics_knowledge.py
```

## Install

Requirements: Git, Python 3.10 or later, and Codex. `ripgrep` is recommended
for speed, but the search helper has a Python fallback.

```bash
git clone --recurse-submodules git@github.com:qianxvde/robotics-knowledge-skill.git
cd robotics-knowledge-skill
./scripts/install.sh
```

The installer creates a symbolic link under
`${CODEX_HOME:-$HOME/.codex}/skills`, so the skill continues to see the bundled
submodules after repository updates. Start a new Codex session after installing.

If a skill with the same name already exists, review it first and then replace
it explicitly:

```bash
./scripts/install.sh --force
```

The old installation is moved to a timestamped backup; it is not deleted.

## Use with Codex

Invoke it explicitly when desired:

```text
Use $robotics-tutorial to review this humanoid locomotion reward design before editing.
```

The skill also allows implicit invocation for robotics code, debugging,
architecture, reward and observation design, deployment, and validation tasks.
It instructs Codex to search in both Chinese and English, read the complete
relevant sections, and validate suggestions against the target repository.

## Use the search helper directly

```bash
python skill/robotics-tutorial/scripts/search_robotics_knowledge.py \
  "AMP" "adversarial motion prior" "模仿学习"

python skill/robotics-tutorial/scripts/search_robotics_knowledge.py \
  --root theory --context 2 "teacher student" "privileged learning"

python skill/robotics-tutorial/scripts/search_robotics_knowledge.py --print-roots
```

Literal queries are OR-combined by default. Add `--regex` for an intentional
regular expression, `--case-sensitive` for exact case, or `--limit` to control
the maximum output per knowledge base.

## Path discovery

No machine-specific path is embedded in the skill. Each knowledge root is
resolved independently in this order:

1. `--tutorial-root` or `--theory-root` command-line argument;
2. `ROBOTICS_TUTORIAL_ROOT` or `ROBOTICS_THEORY_ROOT` environment variable;
3. the `knowledge/` directory found relative to this repository or the current
   working directory;
4. a JSON configuration file.

The default configuration location is
`${XDG_CONFIG_HOME:-$HOME/.config}/robotics-knowledge-skill/paths.json`. Override
it with `ROBOTICS_KNOWLEDGE_CONFIG`. Example:

```json
{
  "tutorial_root": "/path/to/Robotics_Tutorial",
  "theory_root": "/path/to/Robotics_Theory"
}
```

This makes the skill usable with the bundled submodules or with separately
managed clones.

## Update the references

```bash
git submodule update --remote --merge
git add knowledge/Robotics_Tutorial knowledge/Robotics_Theory
git commit -m "chore: update robotics references"
```

Submodule updates are explicit so a given revision of this repository always
uses reproducible reference versions.

## 中文说明

该仓库把两个机器人知识库作为子模块固定版本，并提供一个 Codex skill。
安装后，在机器人代码修改、奖励/观测设计、强化学习、运动控制、仿真到实机、
感知和 ROS2 等任务中，skill 会先按中英文关键词检索 Markdown 与 LaTeX
源码，再把相关工程经验结合到当前项目，而不是盲目套用文档中的 API。

快速使用：

```bash
git clone --recurse-submodules git@github.com:qianxvde/robotics-knowledge-skill.git
cd robotics-knowledge-skill
./scripts/install.sh
```

然后在新的 Codex 会话中说：

```text
请使用 $robotics-tutorial 检索相关经验后，审查并修改这个机器人任务。
```

仓库没有写死本机路径。默认使用随仓库下载的子模块；也可以通过环境变量、
命令行参数或 JSON 配置指向已有的知识库克隆。

## License and upstream content

The MIT license in this repository covers the wrapper skill, helper, installer,
and documentation authored here. Each submodule remains an independent upstream
project and retains its own copyright and licensing terms. Review those terms
before redistributing upstream content.

