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

Most notification tools are designed to be "unobtrusive". This one was built for people who keep missing alerts anyway: deep-focus work, noisy rooms, speakers that might as well be off. When a polite little "ding" fails, the task sits there and waits.

For that person, subtlety is not a feature. **Subtlety is a pay cut.**

`alert-user` is a Codex skill that escalates from a polite notification to a full-scale audiovisual emergency when an authorized persistent task is blocked on a confirmation, approval, login, browser interaction, hardware action, or other manual step.

### The five stages of "WHERE ARE YOU"

Forget "levels". Each stage has a name, because numbers are not urgent enough:

| Stage | Name | What happens | What it sounds like |
| --- | --- | --- | --- |
| 1 | **The Serenade** | Native notification, plus the bundled `1.mp3` clip played once when sound is allowed | A polite 5-second audio clip. Civilized. Almost friendly. |
| 2 | **The Infinite Loop** | Notification, Codex jumps to the foreground, and `2.mp3` loops back-to-back for up to 5 minutes | A one-minute clip. Again. And again. And again. |
| 3 | **Fire Truck Incoming** | Adds the fire-truck **yelp** siren | A fast sweep, 600↔1600 Hz twice per second. Urgent. |
| 4 | **Citywide Meltdown** | Adds a confirmation dialog and the fire-truck **wail** siren | A slow, deep 3-second sweep, 500↔1700 Hz. Menacing. |
| 5 | **TOTAL APOCALYPSE** | Everything at once: dialog, foreground takeover, **hi-lo** siren at up to 100% volume for ~50 seconds, full-screen strobe at up to **24 Hz** | Two hard-switching tones (660/990 Hz), the classic European fire engine. Plus your screen seizing in red, black, white, and yellow. There is no level 6 because there is nothing left. |

Each channel has its own permission flag. Sound, temporary volume changes, device switching, and the visual strobe are never inferred from a generic "remind me" request. The CLI still takes `--level 1` through `--level 5` — the drama is in the output.

### When it fires, and how fast it escalates

It only fires when a task is genuinely stuck on something only you can do — a confirmation, an approval, a credential, a browser step, a hardware action. Ordinary progress updates do not qualify.

While a stage goes unanswered, it re-alerts at that stage's rhythm, then escalates exactly one stage:

| Stage | Re-alerts every | Escalates after | Total elapsed |
| --- | --- | --- | --- |
| 1 The Serenade | 3 minutes | 6 minutes (2 unanswered) | 6 min |
| 2 The Infinite Loop | 4 minutes | 8 minutes (2 unanswered) | 14 min |
| 3 Fire Truck Incoming | 4 minutes | 8 minutes (2 unanswered) | 22 min |
| 4 Citywide Meltdown | 4 minutes | 8 minutes (2 unanswered) | 30 min |
| 5 TOTAL APOCALYPSE | 5 minutes, at most 3 bursts | Then one reminder every 15 minutes | — |

Thirty minutes of silence means TOTAL APOCALYPSE. Any reply pauses the ladder; a confirmation stops it instantly and restores your volume.

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
- **Hearing:** level 3+ synthesizes audio near full scale and level 5 may temporarily set system volume to 100%. Volume is always restored afterwards, but your relationship with your roommates may not be.
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

### About the scores

The repository ships both audio clips and score data. Stages 1-2 play bundled MP3 clips (`assets/audio/1.mp3`, `assets/audio/2.mp3`), and stages 3-5 play three bundled fire-truck sirens (yelp, wail, hi-lo) rendered at runtime with a harsh harmonic-rich waveform, peak-normalized to 0.95 full scale. You can supply another JSON score that you own or are licensed to use with `--score PATH`.

One honest note: the sirens are original CC0 scores. If you replace the bundled MP3s or add your own scores, make sure you have the right to use and redistribute them. A converter writing "CC0 format" into a filename does not relicense the underlying melody — that door has been checked, and it is not a loophole.

### Development

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py alert-user
du -sh .
```

MIT licensed. The original bundled scores are additionally marked CC0-1.0.

---

## 中文

Codex 又卡住了。卡在那种最原始、最让人没脾气的状态：**等你回来点一个按钮**。

市面上的提醒工具，个个把"不打扰"当美德。这个项目不管这套。它就是给"提醒了也看不见"的场景准备的：干活干得太投入、环境太吵、音箱跟没开一样。轻轻"叮"一声没用，任务就在那儿干等。

所以它的思路很朴素：你不回来，它就一级一级加码，加到你回来为止。

### 五个阶段

每个阶段都有名字，因为光报数字实在不够着急：

| 阶段 | 名称 | 会做什么 | 听起来什么效果 |
| --- | --- | --- | --- |
| 1 | **点歌台** | 系统通知；允许出声的话，把内置的 `1.mp3` 放一遍 | 一段 5 秒的小音频，客客气气 |
| 2 | **单曲循环** | 通知，Codex 跳到前台，`2.mp3` 首尾相接循环着放 | 一段一分钟的音频来回放，放到你嫌烦为止 |
| 3 | **消防车出警** | 上面这些之外，加消防车 yelp 警笛 | 每秒两个来回的扫频（600↔1600 Hz），催命 |
| 4 | **全城警报** | 再加确认弹窗和消防车 wail 长鸣 | 三秒一个来回的低沉长鸣（500↔1700 Hz），压迫感 |
| 5 | **世界末日** | 全上：弹窗、前台接管、满音量 hi-lo 警笛 50 秒、最高 24 Hz 全屏爆闪 | 欧式消防车那种"滴嘟滴嘟"（660/990 Hz 硬切换），屏幕在红黑白黄里抽搐。没有第六级，没东西了 |

每种通道都要单独授权。你只说一句"提醒我"，它不会自作主张开声音、改音量、切设备或者闪屏幕。命令行参数还是 `--level 1` 到 `--level 5`，戏都在名字和动静里。

### 什么时候响，多久升一级

只有任务真的卡住、必须你本人动手的时候它才响：点确认、过审批、输凭据、操作浏览器、动硬件，诸如此类。普通的进度汇报不配响。

没人理它的时候，每个阶段按自己的节奏反复提醒，等够了就升一级，一次只升一级：

| 阶段 | 每隔多久提醒一次 | 没人理就升级 | 累计等了 |
| --- | --- | --- | --- |
| 1 点歌台 | 3 分钟 | 6 分钟（两次没理） | 6 分钟 |
| 2 单曲循环 | 4 分钟 | 8 分钟（两次没理） | 14 分钟 |
| 3 消防车出警 | 4 分钟 | 8 分钟（两次没理） | 22 分钟 |
| 4 全城警报 | 4 分钟 | 8 分钟（两次没理） | 30 分钟 |
| 5 世界末日 | 5 分钟，最多三轮 | 之后每 15 分钟提醒一次 | — |

三十分钟没人回来，世界末日。你随便回一句话它就暂停；确认了，它立刻收工，音量什么的都恢复原样。

### 怎么装

对 Codex 说一句话就行：

> 安装这个 `alert-user` skill：https://github.com/HMyaoyuan/codex-alert-user/tree/main/alert-user

它自己会走 `skill-installer` 把 skill 下载到本机，下一轮对话就能用。

### 先演习，别吓着自己

```bash
python3 alert-user/scripts/alert_user.py preflight --json
python3 alert-user/scripts/alert_user.py alert --level 5 \
  --allow-sound --allow-dialog --allow-visual-pulse --dry-run
```

发一次正经但安静的通知：

```bash
python3 alert-user/scripts/alert_user.py alert --level 1 \
  --title "Codex 正在等你" \
  --message "请回来确认结果。"
```

脚本只用 Python 标准库，播放器用的是系统自带的 `afplay`（macOS）或 `mpg123`、`ffplay`、`paplay`（Linux），通知走 `osascript` 或 `notify-send`。

### 丑话说在前头（这段是认真的）

- **光敏癫痫患者别用视觉爆闪，一次都别。** 8-24 Hz 正卡在已知风险区间里。这个项目是按"用户本人确认过没有光敏问题"调的。不是你本人用，或者屏幕边上有别人，就永远别加 `--allow-visual-pulse`。
- **听力：** 3 级往上合成音频接近满幅，5 级会把系统音量临时拉到 100%。音量用完会恢复，你和室友的关系自己看着办。
- 爆闪随时能关：**Esc 或者鼠标点一下**，立刻停。
- 设备只读不折腾：不会自动轮换输出，不会自动选耳机、助听器、会议虚拟设备。
- 循环提醒跑在一个可以随时停止的 heartbeat 里，不是藏起来的后台进程。

### 手动装（备用）

`skill-installer` 不可用的时候再用这个：

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

重启 Codex 或者新开一个任务，让它重新发现 skill。

### 关于声音素材

第 1、2 阶段放的是仓库自带的两个 MP3（`assets/audio/1.mp3`、`2.mp3`）。第 3-5 阶段不放现成音频，是运行时现合成的消防车警笛：一段谐波叠层的刺耳波形，峰值归一化到 0.95 满幅。想换自己的声音，可以用 `--score PATH` 传 JSON 谱子。

一句实话：三套警笛谱子是原创 CC0；你要替换 MP3 或者谱子的话，确认你有权使用、有权再分发。转谱工具在文件名里写"CC0 格式"，改变不了旋律本身的版权归属。

### 开发

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py alert-user
du -sh .
```

代码 MIT 许可；原创警笛谱子额外标注 CC0-1.0。
