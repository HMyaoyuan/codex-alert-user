# Alert User / 把用户叫回来

[English](#english) · [中文](#中文)

## English

Codex has reached the ancient and terrifying state known as: **waiting for you to click one button**.

`alert-user` is a Codex skill for progressively getting a user's attention when an authorized persistent task is blocked on a confirmation, approval, login, browser interaction, hardware action, or other manual step.

It starts polite. It escalates to a full-scale fire-truck siren and a rapid full-screen strobe. This fork is tuned for a user who attested to healthy hearing, no photosensitivity, and sound-isolating earmuffs — subtlety would literally cost them income.

> [!WARNING]
> **This fork runs in maximum-intensity mode.** Level 5 synthesizes near-full-scale fire-truck sirens, may temporarily set system volume to 100%, and strobes the screen at 8-12 Hz — inside the photosensitive-seizure risk band for susceptible people. Use it only for the attesting user, never around bystanders, and always with the explicit opt-in flags. Escape or a click dismisses the visual immediately; volume is restored after every run.

### Install it by talking to Codex

Send this one sentence to Codex:

> Install the `alert-user` skill from https://github.com/HMyaoyuan/codex-alert-user/tree/main/alert-user

That is the normal installation flow. Codex's `skill-installer` downloads the public skill into your skills directory, and it becomes available on the next turn.

### The escalation ladder

| Level | What happens |
| --- | --- |
| 1 | Native notification |
| 2 | Notification and bring Codex forward |
| 3 | Add a fire-truck **yelp** siren burst |
| 4 | Add a bounded confirmation dialog and a repeated fire-truck **wail** |
| 5 | Add a full-screen, high-contrast **8-12 Hz strobe** and the **hi-lo** siren at full volume at the same time |

Each channel has its own permission boundary. Sound, temporary volume changes, device switching, and visual strobes are never inferred from a generic "remind me" request.

Level 5 is the theatrical maximum: multiple channels, foreground takeover, an original hi-lo siren synthesized at runtime at near full scale, temporary system volume up to 100% (restored afterwards), and a rapid red/black/white/yellow visual strobe for up to 60 seconds. Escape or a click dismisses the visual immediately.

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

### Manual installation fallback

Use this only when `skill-installer` is unavailable:

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

Restart Codex or begin a new task so the skill metadata is discovered.

### About the alarm "score"

The repository ships score data, not an MP3. The three bundled fire-truck sirens (yelp, wail, hi-lo) are original CC0 scores rendered into WAV data at runtime. You can supply another JSON score that you own or are licensed to use.

Musical notation is still copyrighted expression, so this repository does not smuggle a copyrighted song in through the sheet-music door. The door has been checked. It is not a loophole.

### Bounded, not tame

- Generated audio is amplitude-limited to 0.95 full scale.
- Temporary volume increases may reach 100% when authorized and are always restored.
- Output devices are inspected, but never rotated automatically.
- Headphones, hearing aids, virtual meeting devices, and remote outputs are never selected automatically.
- Visual strobes are opt-in, capped at 12 Hz, bounded to 60 seconds, and dismissible with Escape or a click.
- Recurring reminders belong in one stoppable Codex heartbeat, not a hidden infinite daemon.
- Any response from the user pauses escalation; confirmation stops it.

The most dramatic level is meant to punch through sound-isolating earmuffs and a turned-around chair. Keep it away from anyone who did not sign up for that.

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

它一开始很温柔，最后会升级到满幅消防车警笛加全屏高频爆闪。本仓库为一位确认听力健康、无光敏癫痫、且日常戴隔音耳罩的用户调校——对它来说，太温柔就意味着错过工作、损失收入。

> [!WARNING]
> **本仓库运行在最大强度模式。** 第 5 级会合成接近满幅的消防车警笛、可能把系统音量临时拉到 100%，并以 8-12 Hz 全屏频闪——这个频率落在易感人群的光敏癫痫风险区间内。只限已确认身体状况的用户本人使用，切勿在旁观者周围使用，并且始终通过明确的授权开关启用。按 Escape 或点击鼠标可立即关闭视觉提醒；每次运行结束后都会恢复原音量。

### 对 Codex 说一句话就能安装

把下面这句话发给 Codex：

> 安装这个 `alert-user` skill：https://github.com/HMyaoyuan/codex-alert-user/tree/main/alert-user

这样就完成了正常的安装流程。Codex 会自动调用 `skill-installer`，把公开仓库中的 skill 下载到本机 skills 目录；下一轮对话即可使用。

### 五级提醒阶梯

| 级别 | 提醒方式 |
| --- | --- |
| 1 | 系统原生通知 |
| 2 | 通知并把 Codex 切到前台 |
| 3 | 加入消防车 **yelp** 急促警笛 |
| 4 | 加入限时确认弹窗和反复的消防车 **wail** 长鸣警笛 |
| 5 | 同时启动全屏高对比度 **8-12 Hz 爆闪** 和满音量 **hi-lo** 双音警笛 |

每一种通道都需要独立授权。用户只说“提醒我”，不等于自动允许声音、临时修改音量、切换输出设备或显示视觉爆闪。

第 5 级是“戏剧效果拉满”的最高档：多通道同时提醒、切回前台、运行时合成接近满幅的原创 hi-lo 警笛、临时系统音量最高 100%（结束后恢复），再加红/黑/白/黄高频视觉爆闪，最长 60 秒。按 Escape 或点击鼠标可以立即关闭视觉提醒。

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

### 手动安装备用方案

只有在 `skill-installer` 不可用时才需要下面这些命令：

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

重启 Codex 或新建一个任务，让 Codex 重新发现 skill 元数据。

### 关于报警“谱子”

仓库内置的是谱子数据，不是 MP3。三套消防车警笛（yelp 急促、wail 长鸣、hi-lo 双音）均为原创 CC0 谱子，运行时才会被合成为 WAV。你也可以传入自己拥有版权或使用授权的 JSON 谱子。

完整乐谱同样属于受版权保护的音乐表达，所以本仓库不会尝试通过“只放谱子”来绕过歌曲版权。换一扇门，并不会让版权墙消失。

### 有边界，但不温柔

- 合成音频振幅最高为满幅的 0.95。
- 临时提高音量时最高可到 100%，结束后恢复原音量。
- 会检查输出设备，但不会自动轮换播放。
- 不会自动选择耳机、助听器、会议软件虚拟设备或远程输出。
- 视觉爆闪必须明确授权，最高 12 Hz、最长 60 秒，并可用 Escape 或鼠标点击关闭。
- 持续提醒应使用一个可以停止的 Codex heartbeat，而不是隐藏的无限后台进程。
- 用户只要有任何回应就暂停升级；确认后立即停止提醒。

最高级提醒的目标是穿透隔音耳罩和转过去的椅子。请勿让任何没有签署这份“夸张协议”的人靠近屏幕和音箱。

### 开发与验证

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py alert-user
du -sh .
```

代码采用 MIT 许可证；仓库内置的原创谱子额外采用 CC0-1.0。
