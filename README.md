# Alert User / 把用户叫回来

[English](#english) · [中文](#中文)

## English

Codex has reached the ancient and terrifying state known as: **waiting for you to click one button**.

`alert-user` is a Codex skill for progressively getting a user's attention when an authorized persistent task is blocked on a confirmation, approval, login, browser interaction, hardware action, or other manual step.

It starts polite. It can become gloriously difficult to ignore. It does not turn your desk into a hearing test or a seizure trigger.

> [!WARNING]
> **This project does not implement injury-oriented alerts.** It will not target hearing damage, induce seizures, set every device to maximum volume, use rapid strobing, or remove its safety limits. Loud sound and flashing light can harm people unexpectedly—including bystanders. The strongest mode is deliberately bounded, opt-in, and stoppable.

### The escalation ladder

| Level | What happens |
| --- | --- |
| 1 | Native notification |
| 2 | Notification and bring Codex forward |
| 3 | Add an original synthesized chime |
| 4 | Add a bounded confirmation dialog and repeated alarm phrase |
| 5 | Add a full-screen, high-contrast **slow** pulse and urgent synthesized alarm at the same time |

Each channel has its own permission boundary. Sound, temporary volume changes, device switching, and visual pulses are never inferred from a generic "remind me" request.

Level 5 is the theatrical maximum: multiple channels, foreground takeover, an original critical score synthesized at runtime, and a high-contrast visual pulse. It remains capped at 75% temporary system volume, 0.4 full-scale generated audio, 1 Hz visual transitions, and 20 seconds. Escape or a click dismisses the visual immediately.

### Try it without surprising yourself

```bash
python3 alert-user/scripts/alert_user.py preflight --json
python3 alert-user/scripts/alert_user.py alert --level 5 \
  --allow-sound --allow-dialog --allow-visual-pulse --dry-run
```

A real, quiet notification:

```bash
python3 alert-user/scripts/alert_user.py alert --level 1 \
  --title "Codex is waiting" \
  --message "Please return and confirm the result."
```

The scripts use only the Python standard library plus operating-system helpers such as `osascript`, `afplay`, `notify-send`, `paplay`, or `aplay` when available.

### Install as a Codex skill

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

Restart Codex or begin a new task so the skill metadata is discovered.

### About the alarm "score"

The repository ships note data, not an MP3. The three bundled jingles are original CC0 scores rendered into WAV data at runtime. You can supply another JSON score that you own or are licensed to use.

Musical notation is still copyrighted expression, so this repository does not smuggle a copyrighted song in through the sheet-music door. The door has been checked. It is not a loophole.

### Safety is part of the feature

- Generated audio is amplitude-limited.
- Temporary volume increases are capped at 75% and restored.
- Output devices are inspected, but never rotated automatically.
- Headphones, hearing aids, virtual meeting devices, and remote outputs are never selected automatically.
- Visual pulses are opt-in, capped at 1 Hz, bounded to 20 seconds, and dismissible with Escape or a click.
- Recurring reminders belong in one stoppable Codex heartbeat, not a hidden infinite daemon.
- Any response from the user pauses escalation; confirmation stops it.

The most dramatic level should feel urgent, absurd, and memorable—not hostile or medically dangerous.

### Development

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py alert-user
du -sh .
```

MIT licensed. The original bundled scores are additionally marked CC0-1.0.

---

## 中文

Codex 已经进入那个古老、可怕、让 AI 急得团团转的状态：**只差你回来点一下按钮**。

`alert-user` 是一个渐进式提醒用户的 Codex skill。当一个经过用户授权的持续任务卡在确认、审批、登录、浏览器操作、硬件操作或其他人工步骤时，它会从礼貌提醒逐步升级，努力把用户叫回来。

它一开始很温柔，最后可以夸张到很难忽略；但它不会把你的桌面变成听力测试中心或癫痫诱发器。

> [!WARNING]
> **本项目不会实现以伤害为目标的提醒。** 它不会以听力损伤、诱发癫痫为设计目标，不会把所有设备轮流调到最大音量，不会快速频闪，也不会移除安全上限。强声音和闪光可能意外伤害用户及旁观者。最高级模式依然是有边界、需明确授权、随时可停止的。

### 五级提醒阶梯

| 级别 | 提醒方式 |
| --- | --- |
| 1 | 系统原生通知 |
| 2 | 通知并把 Codex 切到前台 |
| 3 | 加入原创的程序合成提示音 |
| 4 | 加入限时确认弹窗和重复报警乐句 |
| 5 | 同时启动全屏高对比度**慢速**脉冲和紧急合成报警声 |

每一种通道都需要独立授权。用户只说“提醒我”，不等于自动允许声音、临时修改音量、切换输出设备或显示视觉脉冲。

第 5 级是“戏剧效果拉满”的安全最高档：多通道同时提醒、切回前台、运行时合成原创紧急谱子，再加高对比度视觉脉冲。但临时系统音量仍不超过 75%，生成音频振幅不超过满幅的 0.4，视觉变化不超过 1 Hz，总时长不超过 20 秒。按 Escape 或点击鼠标可以立即关闭视觉提醒。

### 先演习，不要突然吓自己

```bash
python3 alert-user/scripts/alert_user.py preflight --json
python3 alert-user/scripts/alert_user.py alert --level 5 \
  --allow-sound --allow-dialog --allow-visual-pulse --dry-run
```

发送一次真正但温柔的通知：

```bash
python3 alert-user/scripts/alert_user.py alert --level 1 \
  --title "Codex 正在等你" \
  --message "请回来确认结果。"
```

脚本只使用 Python 标准库，以及操作系统已有的 `osascript`、`afplay`、`notify-send`、`paplay` 或 `aplay` 等工具。

### 安装为 Codex skill

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

重启 Codex 或新建一个任务，让 Codex 重新发现 skill 元数据。

### 关于报警“谱子”

仓库内置的是音符数据，不是 MP3。三套提示乐句均为原创 CC0 谱子，运行时才会被合成为 WAV。你也可以传入自己拥有版权或使用授权的 JSON 谱子。

完整乐谱同样属于受版权保护的音乐表达，所以本仓库不会尝试通过“只放谱子”来绕过歌曲版权。换一扇门，并不会让版权墙消失。

### 安全本身就是功能

- 合成音频有硬编码的振幅限制。
- 临时提高音量时最高为 75%，结束后恢复原音量。
- 会检查输出设备，但不会自动轮换播放。
- 不会自动选择耳机、助听器、会议软件虚拟设备或远程输出。
- 视觉脉冲必须明确授权，最高 1 Hz、最长 20 秒，并可用 Escape 或鼠标点击关闭。
- 持续提醒应使用一个可以停止的 Codex heartbeat，而不是隐藏的无限后台进程。
- 用户只要有任何回应就暂停升级；确认后立即停止提醒。

最高级提醒应该让人觉得紧急、荒诞、记忆深刻，而不是带有敌意或医学危险。

### 开发与验证

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py alert-user
du -sh .
```

代码采用 MIT 许可证；仓库内置的原创谱子额外采用 CC0-1.0。
