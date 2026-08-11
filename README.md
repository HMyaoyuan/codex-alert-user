# Alert User / 把用户叫回来

> ## ⚠️ WARNING · 警告
>
> **DO NOT USE this project if you have photosensitive epilepsy.**
> **光敏癫痫患者禁止使用本项目。**
>
> **DO NOT USE this project around anyone with photosensitive epilepsy, hearing conditions, a pacemaker-era sense of calm, or a cat you actually like.**
> **请不要在任何光敏癫痫患者、听力敏感者、心脏不太好的朋友、或你真心喜欢的猫旁边使用本项目。**
>
> This is not legal boilerplate. **It is the product spec.**
> 这不是免责声明。**这是产品参数。**
>
> Level 5 strobes your entire screen at up to **24 Hz** and plays a near-full-scale synthesized fire-truck siren at up to **100% system volume**.
> 第 5 级会以最高 **24 Hz** 爆闪你的整个屏幕，并以最高 **100% 系统音量**播放接近满幅的合成消防车警笛。
>
> If that sentence sounds like a reason to close this tab — it is.
> 如果这句话让你想关掉这个页面——那就对了，请关。

[English](#english) · [中文](#中文)

---

## English

Codex has reached the ancient and terrifying state known as: **waiting for you to click one button**.

Most notification tools are designed to be "unobtrusive". This one was built for a very specific person: a developer who wears **sound-isolating earmuffs**, whose hearing is perfectly healthy, and who **loses real income** every time a polite little "ding" fails to penetrate the foam.

For that person, subtlety is not a feature. **Subtlety is a pay cut.**

`alert-user` is a Codex skill that escalates from a polite notification to a full-scale audiovisual emergency when an authorized persistent task is blocked on a confirmation, approval, login, browser interaction, hardware action, or other manual step.

### The five stages of "WHERE ARE YOU"

Forget "levels". Each stage has a name, because numbers are not urgent enough:

| Stage | Name | What happens |
| --- | --- | --- |
| 1 | **The Polite Cough** | Native notification. "Ahem." |
| 2 | **The Desk Slam** | Notification, and Codex jumps to the foreground. |
| 3 | **Fire Truck Incoming** | Adds a synthesized fire-truck **yelp** siren. Your earmuffs start to notice. |
| 4 | **Citywide Meltdown** | Adds a confirmation dialog and a repeated fire-truck **wail**. Your neighbors start to notice. |
| 5 | **TOTAL APOCALYPSE** | Everything at once: dialog, foreground takeover, the **hi-lo** siren at up to 100% volume for ~50 seconds, and a full-screen red/black/white/yellow strobe at up to **24 Hz**. There is no level 6 because there is nothing left. |

Each channel has its own permission flag. Sound, temporary volume changes, device switching, and the visual strobe are never inferred from a generic "remind me" request. The CLI still takes `--level 1` through `--level 5` — the drama is in the output.

### Install it by talking to Codex

Send this one sentence to Codex:

> Install the `alert-user` skill from https://github.com/HMyaoyuan/codex-alert-user/tree/main/alert-user

That is the normal installation flow. Codex's `skill-installer` downloads the public skill into your skills directory, and it becomes available on the next turn.

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

### The warnings are real (this part is not a joke)

- **Photosensitive epilepsy: do not use the visual strobe, at all, ever.** The 8-24 Hz range sits squarely inside the known risk band. This project is configured for one specific user who attested they do not have photosensitivity. If that is not you, or anyone else might see your screen, never pass `--allow-visual-pulse`.
- **Hearing:** level 3+ synthesizes audio near full scale and level 5 may temporarily set system volume to 100%. Built for a user with healthy hearing behind industrial earmuffs. Volume is always restored afterwards, but your relationship with your roommates may not be.
- The visual strobe always has an instant off-switch: **Escape or any mouse click** kills it.
- Devices are inspected but never rotated automatically; headphones, hearing aids, and virtual meeting devices are never selected on their own.
- Recurring reminders live in one stoppable Codex heartbeat, not a hidden daemon. Any response from the user pauses escalation; confirmation stops it.

### Manual installation fallback

Use this only when `skill-installer` is unavailable:

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

Restart Codex or begin a new task so the skill metadata is discovered.

### About the siren "scores"

The repository ships score data, not an MP3. The three bundled fire-truck sirens (yelp, wail, hi-lo) are original CC0 scores rendered into WAV data at runtime with a harsh harmonic-rich waveform, peak-normalized to 0.95 full scale. You can supply another JSON score that you own or are licensed to use.

Musical notation is still copyrighted expression, so this repository does not smuggle a copyrighted song in through the sheet-music door. The door has been checked. It is not a loophole.

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

市面上大多数提醒工具的设计目标是"不打扰"。这个项目不是。它为一位非常具体的用户而生：一个平时戴着**隔音耳罩**、听力完全健康、并且每一次被"叮"一声礼貌地失败、都会**真金白银损失收入**的开发者。

对这个人来说，温柔不是优点。**温柔等于扣工资。**

`alert-user` 是一个渐进式提醒的 Codex skill：当一个经过授权的持续任务卡在确认、审批、登录、浏览器操作、硬件操作等人工步骤时，它会从礼貌通知一路升级到全面的视听紧急状态。

### "你在哪"的五个阶段

不叫"层级"了，数字不够着急。每个阶段都有名字：

| 阶段 | 名称 | 会发生什么 |
| --- | --- | --- |
| 1 | **礼貌咳嗽** | 系统原生通知。"咳。" |
| 2 | **拍桌子** | 通知 + 把 Codex 猛地切到前台。 |
| 3 | **消防车出警** | 加入合成消防车 **yelp** 急促警笛。你的耳罩开始察觉异常。 |
| 4 | **全城警报** | 加入确认弹窗 + 反复的消防车 **wail** 长鸣。你的邻居开始察觉异常。 |
| 5 | **世界末日** | 全部一起上：弹窗、前台接管、满音量 **hi-lo** 双音警笛连播约 50 秒，加上全屏红/黑/白/黄最高 **24 Hz** 爆闪。没有第 6 级，因为没有东西了。 |

每种通道都有独立的授权开关。只说"提醒我"，不会自动获得声音、临时改音量、切换输出设备或视觉爆闪的权限。CLI 参数仍然是 `--level 1` 到 `--level 5`——戏剧性体现在输出里。

### 对 Codex 说一句话就能安装

把下面这句话发给 Codex：

> 安装这个 `alert-user` skill：https://github.com/HMyaoyuan/codex-alert-user/tree/main/alert-user

这样就完成了正常的安装流程。Codex 会自动调用 `skill-installer`，把公开仓库中的 skill 下载到本机 skills 目录；下一轮对话即可使用。

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

### 警告是认真的（这一段不是玩笑）

- **光敏癫痫患者：永远、绝对、不要使用视觉爆闪。** 8-24 Hz 正好落在已知风险区间的正中央。本项目是为一位明确确认自己没有光敏问题的用户调校的。如果那个人不是你，或者你的屏幕可能被其他人看到，永远不要加 `--allow-visual-pulse`。
- **听力：** 第 3 级以上合成音频接近满幅，第 5 级可能把系统音量临时拉到 100%。这是为"健康听力 + 工业级耳罩"的用户设计的。音量结束后一定会恢复，但你和室友的关系不一定。
- 视觉爆闪永远有一键关闭：**按 Escape 或随便点一下鼠标**立刻消失。
- 输出设备只检查、不自动轮换；绝不自动选择耳机、助听器或会议软件虚拟设备。
- 持续提醒只存在于一个可停止的 Codex heartbeat 里，不是隐藏的后台进程。你有任何回应就暂停升级；确认后立即停止。

### 手动安装备用方案

只有在 `skill-installer` 不可用时才需要下面这些命令：

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

重启 Codex 或新建一个任务，让 Codex 重新发现 skill 元数据。

### 关于警笛"谱子"

仓库内置的是谱子数据，不是 MP3。三套消防车警笛（yelp 急促、wail 长鸣、hi-lo 双音）均为原创 CC0 谱子，运行时用谐波叠层的刺耳波形合成 WAV，并做了 0.95 满幅的峰值归一化。你也可以传入自己拥有版权或使用授权的 JSON 谱子。

完整乐谱同样属于受版权保护的音乐表达，所以本仓库不会尝试通过"只放谱子"来绕过歌曲版权。换一扇门，并不会让版权墙消失。

### 开发与验证

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py alert-user
du -sh .
```

代码采用 MIT 许可证；仓库内置的原创谱子额外采用 CC0-1.0。
