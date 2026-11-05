<div align="center">

<img src="assets/banner.png" alt="S1M0N_X_H4SS4N Ultra Bomber" width="100%">

# S1M0N_X_H4SS4N ULTRA BOMBER v1.0

**অসীম রাউন্ড SMS + কল বোম্বিং ইঞ্জিন — ১৭০+ লাইভ এন্ডপয়েন্ট**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Windows-2ea44f?style=flat-square&logo=linux&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)]()
[![Version](https://img.shields.io/badge/Version-1.0-ff2e97?style=flat-square)]()

</div>

---

## 📖 পরিচিতি

**Ultra Bomber** হলো একটা সিঙ্গেল-ফাইল, ডিপেন্ডেন্সি-লাইট পাইথন ইঞ্জিন যা বাংলাদেশি ও আন্তর্জাতিক **১৭০+ লাইভ সার্ভিস**-এর OTP/লগইন এন্ডপয়েন্টে একসাথে হিট করে। প্রতিটা হিট আলাদা থ্রেডে যায়, ব্যর্থ এন্ডপয়েন্ট অটো-রিট্রাই হয় অল্টারনেট নাম্বার ফরম্যাটে, আর সফল এন্ডপয়েন্ট প্রায়োরিটি শিডিউলারে উপরে উঠে আসে।

**মূল বৈশিষ্ট্য:**

| ফিচার | বর্ণনা |
|---|---|
| ♾️ অসীম রাউন্ড | Ctrl+C না চাপা পর্যন্ত লুপ চলতেই থাকে |
| 🧵 মাল্টি-থ্রেডেড | ডিফল্ট ৪০ কনকারেন্ট ওয়ার্কার |
| 🎯 স্মার্ট প্রায়োরিটি | যে API কাজ করে, সেটা পরের রাউন্ডে আগে যায় |
| 🔁 অটো রিট্রাই | `+88` / `880` / `88` ফরম্যাট ভ্যারিয়েন্টে রি-ট্রাই |
| 🎭 UA রোটেশন | প্রতিটা থ্রেডে র‍্যান্ডম ইউজার-এজেন্ট |
| 📊 লাইভ ড্যাশবোর্ড | প্রতি ১০ সেকেন্ডে সাকসেস রেট |
| 📝 রিপোর্ট এক্সপোর্ট | `-o` দিয়ে JSON রিপোর্ট, `--log` দিয়ে হিট লগ |
| 📞 কল বোম্বার | আলাদা `--calls` মোড |
| 🎨 কালারড আউটপুট | ANSI টার্মিনাল UI |

> ⚠️ **এন্ডপয়েন্টগুলো থার্ড-পার্টি সার্ভিসের।** ওরা যেকোনো সময় URL/টোকেন বদলাতে পারে — কিছু এন্ডপয়েন্ট মরে যাওয়া স্বাভাবিক। স্ক্রিপ্ট ডিজাইনই করা হয়েছে যাতে একটা-দুইটা মরা এন্ডপয়েন্ট পুরো রান নষ্ট না করে।

----

## ⚙️ ইনস্টলেশন

### Linux (Debian / Ubuntu / Kali)

```bash
sudo apt update && sudo apt install -y python3 python3-pip git
git clone https://github.com/irfaanahmed2026/s1mon-x-h4ss4n-bomber.git
cd s1mon-x-h4ss4n-bomber
pip3 install -r requirements.txt
```

### Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install -y python git
termux-setup-storage
git clone https://github.com/irfaanahmed2026/s1mon-x-h4ss4n-bomber.git
cd s1mon-x-h4ss4n-bomber
pip install -r requirements.txt
```

> Termux **F-Droid** থেকে ইনস্টল করো, Play Store ভার্সনটা পুরনো। `pip install` এ এরর এলে আগে `pkg install -y python-pip` চালাও।

### Windows

```powershell
git clone https://github.com/irfaanahmed2026/s1mon-x-h4ss4n-bomber.git
cd s1mon-x-h4ss4n-bomber
pip install -r requirements.txt
python bomber.py 01XXXXXXXXX
```

---

## 🚀 ব্যবহার

```bash
# বেসিক — ইনফিনিট মোড
python bomber.py 017XXXXXXXX

# ১০ রাউন্ড, শুধু SMS, ৮০ থ্রেড
python bomber.py 017XXXXXXXX -n 10 --sms -w 80

# শুধু কল বোম্বার
python bomber.py 017XXXXXXXX --calls

# নির্দিষ্ট এন্ডপয়েন্ট (১, ৫, ৯ এবং ২০-৩০)
python bomber.py 017XXXXXXXX -a 1,5,9,20-30

# প্রতি API ৩ বার হিট, প্রতি রাউন্ডে ৫ সেকেন্ড বিরতি
python bomber.py 017XXXXXXXX -l 3 -c 5

# সব এন্ডপয়েন্টের লিস্ট দেখো
python bomber.py --list
```

### সব অপশন

| ফ্ল্যাগ | ডিফল্ট | কাজ |
|---|---|---|
| `phone` | *(প্রম্পট)* | টার্গেট নাম্বার |
| `-l, --loops` | `1` | প্রতি রাউন্ডে প্রতি API কতবার হিট |
| `-w, --workers` | `40` | কনকারেন্ট থ্রেড সংখ্যা |
| `-t, --timeout` | `12` | HTTP টাইমআউট (সেকেন্ড) |
| `-r, --retries` | `1` | নেটওয়ার্ক রিট্রাই |
| `-c, --cooldown` | `3` | রাউন্ডের মাঝে বিরতি |
| `-n, --rounds` | `0` | রাউন্ড সংখ্যা (`0` = অসীম) |
| `-a, --api` | `all` | `all` \| `list` \| `1,5,9` \| `1-20` |
| `--sms` / `--calls` | — | শুধু SMS / শুধু কল |
| `--no-priority` | off | প্রায়োরিটি শিডিউলার বন্ধ |
| `--no-alt` | off | অল্টারনেট ফরম্যাট রিট্রাই বন্ধ |
| `-o, --output` | — | শেষে JSON রিপোর্ট সেভ |
| `--log` | — | প্রতি হিটের লগ ফাইল |
| `-q, --quiet` | off | শুধু সামারি |
| `--list` | — | সব এন্ডপয়েন্ট দেখাও |

### থামানোর নিয়ম

- **Ctrl+C একবার** → চলমান রাউন্ড শেষ করে থামবে, সামারি দেখাবে
- **Ctrl+C দুইবার** → সাথে সাথে হার্ড স্টপ

---

## 🧠 কীভাবে কাজ করে

```
নাম্বার নরমালাইজ → এন্ডপয়েন্ট সিলেক্ট → শাফল → প্রায়োরিটি সর্ট
        ↓
   থ্রেড পুলে হিট (৪০ ওয়ার্কার)
        ↓
  OK? → স্কোর +১        FAIL? → অল্ট ফরম্যাটে রিট্রাই → স্কোর −১
        ↓
   কুলডাউন → পরের রাউন্ড (অসীম)
```

সফল এন্ডপয়েন্টের স্কোর বাড়ে, তাই পরের রাউন্ডে সেগুলো আগে যায়। মরা এন্ডপয়েন্টের স্কোর কমে, ফলে সেগুলো পিছিয়ে পড়ে — এতে সিগন্যাল-টু-নয়েজ ভালো থাকে।

---

## 🩺 ট্রাবলশুটিং

| সমস্যা | সমাধান |
|---|---|
| `ModuleNotFoundError: requests` | `pip install -r requirements.txt` |
| সব এন্ডপয়েন্ট ERR | ইন্টারনেট চেক করো, `-t 20` দিয়ে টাইমআউট বাড়াও |
| Termux-এ `pip` নেই | `pkg install -y python-pip` |
| SSL এরর | স্ক্রিপ্টে `verify=False` আছে, `pkg install -y ca-certificates` চালাও |
| আউটপুট এলোমেলো | `-w 20` দিয়ে থ্রেড কমানো |
| SMS আসছে কম | `-l 3` দিয়ে লুপ বাড়াও, `--calls` আলাদা করে চালাও |

---

## 📊 রিপোর্ট ফরম্যাট

```bash
python bomber.py 017XXXXXXXX -n 5 -o report.json
```

```json
{
  "brand": "S1M0N_X_H4SS4N",
  "target": "017XXXXXXXX",
  "rounds": 5,
  "summary": { "total": 850, "ok": 612, "fail": 238 },
  "apis": [ { "name": "RedX Signup", "ok": 5, "fail": 0 } ]
}
```

---

## 🤝 কন্ট্রিবিউট

নতুন এন্ডপয়েন্ট যোগ করতে `@api("নাম")` ডেকোরেটর দিয়ে একটা ফাংশন লেখো:

```python
@api("My New Service")
def a999(c, x):
    return c.post("https://example.com/api/otp",
                  json={"phone": x.full}, headers=J)
```

`x` অবজেক্টে আছে: `x.full`, `x.bare`, `x.p88`, `x.plus88`, `x.dash88`, `x.n88` — যেটা লাগে ব্যবহার করো।

---

## ⚖️ ডিসক্লেইমার

শিক্ষামূলক প্রজেক্ট। এন্ডপয়েন্টগুলো থার্ড-পার্টি এবং কোনো SLA নেই। একই নাম্বারে ঘন ঘন হিট করলে সার্ভিস সাইডে রেট লিমিট হতে পারে — এটা স্ক্রিপ্টের বাগ নয়।

---

<div align="center">

**crafted by S1M0N_X_H4SS4N**

⭐ কাজে লাগলে স্টার দিও

</div>0N_X_H4SS4N**

⭐ কাজে লাগলে স্টার দিও

</div>
