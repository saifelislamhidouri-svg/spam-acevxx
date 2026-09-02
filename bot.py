import os, requests, threading, time, sys, jwt, socket, urllib3, json, ssl, http.client, gzip, random, asyncio
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from io import BytesIO
from AceCore import *

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          CallbackQueryHandler, ContextTypes, filters)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "8544968291:AAF6hKzTE55zG3sTDx7U3IzaJK0Uw1f0aHk"
OWNER_ID  =      8378737863
BOT_NAME  = "ㅤ𝗔𝗰𝗲ㅤ"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, 'accounts.json')
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')
BOT_PHOTO = os.path.join(BASE_DIR, 'ace.jpg')

connected_clients = {}
connected_clients_lock = threading.Lock()
all_accounts = {}
all_accounts_lock = threading.Lock()
ACCOUNTS = []

spam_speed = 3.0
spam_running = False
current_target = None
current_target_info = None
last_target_info = None
target_info_lock = threading.Lock()
state_lock = threading.Lock()

GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'; RESET = '\033[0m'


def load_settings():
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"maintenance": False, "force_channels": []}

def save_settings(s):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

SETTINGS = load_settings()
settings_lock = threading.Lock()


def set_acc_status(acc_id, status):
    with all_accounts_lock:
        if acc_id in all_accounts:
            all_accounts[acc_id]['status'] = status


class MyMessage:
    def __init__(self):
        self.field21 = 0
        self.field22 = b''
        self.field23 = b''

    def ParseFromString(self, data):
        try:
            from AceCore import MyMessage as RealMyMessage
            msg = RealMyMessage()
            msg.ParseFromString(data)
            self.field21 = msg.field21
            self.field22 = msg.field22
            self.field23 = msg.field23
        except Exception:
            if len(data) > 0:
                self.field21 = int.from_bytes(data[:8], 'little') if len(data) >= 8 else 0
                self.field22 = data[8:24] if len(data) >= 24 else b''
                self.field23 = data[24:40] if len(data) >= 40 else b''


class FF_CLient:
    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.CliEnts = None
        self.CliEnts2 = None
        self.running = True
        self.target_id = None
        self.room_opened = False
        self.spam_thread_started = False
        self.send_lock = threading.Lock()
        self.account_uid = None
        threading.Thread(target=self.start_client, daemon=True).start()

    def start_client(self):
        set_acc_status(self.id, 'connecting')
        try:
            self.Get_FiNal_ToKen_0115()
        except Exception:
            time.sleep(2)
            self.start_client()

    def Get_FiNal_ToKen_0115(self):
        while self.running:
            try:
                result = self.Guest_GeneRaTe(self.id, self.password)
                if not result:
                    set_acc_status(self.id, 'connecting')
                    time.sleep(2)
                    continue

                token, key, iv, ts, ip, port, ip2, port2 = result
                if not all([ip, port, ip2, port2]):
                    time.sleep(2)
                    continue

                self.JwT_ToKen = token

                try:
                    self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
                    self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
                    if not self.AccounT_Uid:
                        raise ValueError("No account_id in JWT")
                    self.account_uid = self.AccounT_Uid
                    self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
                    self.HeX_VaLue = DecodE_HeX(ts)
                    self.TimE_HEx = self.HeX_VaLue
                    self.JwT_ToKen_ = token.encode().hex()
                except Exception:
                    time.sleep(1)
                    continue

                try:
                    encrypted_token = EnC_PacKeT(self.JwT_ToKen_, key, iv)
                    header_length = hex(len(encrypted_token) // 2)[2:]
                    uid_length = len(self.EncoDed_AccounT)
                    prefix_map = {7: '000000000', 8: '00000000', 9: '0000000', 10: '000000'}
                    prefix = prefix_map.get(uid_length, '00000000')
                    self.Header = f'0115{prefix}{self.EncoDed_AccounT}{self.TimE_HEx}00000{header_length}'
                    self.FiNal_ToKen_0115 = self.Header + encrypted_token
                except Exception:
                    time.sleep(1)
                    continue

                self.AutH_ToKen = self.FiNal_ToKen_0115
                connection_thread = threading.Thread(
                    target=self.Connect_SerVer,
                    args=(self.JwT_ToKen, self.AutH_ToKen, ip, port, key, iv, ip2, port2),
                    daemon=True
                )
                connection_thread.start()
                connection_thread.join(timeout=30)
                return
            except Exception:
                set_acc_status(self.id, 'connecting')
                time.sleep(2)

    def Connect_SerVer_OnLine(self, Token, tok, host, port, key, iv, host2, port2):
        try:
            self.AutH_ToKen_0115 = tok
            self.CliEnts2 = socket.create_connection((host2, int(port2)))
            self.CliEnts2.settimeout(10)
            self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))

            if not self.room_opened:
                self.CliEnts2.send(openroom(self.key, self.iv))
                self.room_opened = True
                print(f"{GREEN}Bot {self.id} Is Online ✅{RESET}")

            self.start_continuous_spam()
        except Exception:
            return

        while self.running:
            try:
                self.DaTa2 = self.CliEnts2.recv(99999)
                if self.DaTa2:
                    if '0500' in self.DaTa2.hex()[0:4] and len(self.DaTa2.hex()) > 30:
                        try:
                            self.packet = json.loads(DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}'))
                            self.AutH = self.packet['5']['data']['7']['data']
                        except Exception:
                            pass
            except socket.timeout:
                continue
            except Exception:
                time.sleep(0.5)

    def start_continuous_spam(self):
        if self.spam_thread_started:
            return
        self.spam_thread_started = True

        def spam_loop():
            while self.running:
                with state_lock:
                    running = spam_running
                if not (running and self.target_id):
                    time.sleep(0.05)
                    continue
                try:
                    current = self.target_id
                    with self.send_lock:
                        if self.CliEnts2 and self.key and self.iv:
                            self.CliEnts2.send(spmroom(self.key, self.iv, current))
                            self.CliEnts2.send(SEnd_InV(1, current, self.key, self.iv))
                        else:
                            time.sleep(0.5)
                            continue
                    print(f"{YELLOW}from {self.id} => to {current}{RESET}")
                except Exception:
                    print(f"{RED}from {self.id} => to {self.target_id} ERROR{RESET}")
                    time.sleep(0.5)
                    continue
                time.sleep(spam_speed)

        threading.Thread(target=spam_loop, daemon=True).start()

    def set_target(self, target_id):
        self.target_id = target_id

    def Connect_SerVer(self, Token, tok, host, port, key, iv, host2, port2):
        try:
            self.AutH_ToKen_0115 = tok
            self.CliEnts = socket.create_connection((host, int(port)))
            self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))
            self.DaTa = self.CliEnts.recv(1024)

            online_thread = threading.Thread(
                target=self.Connect_SerVer_OnLine,
                args=(Token, tok, host, port, key, iv, host2, port2),
                daemon=True
            )
            online_thread.start()

            self.key = key
            self.iv = iv

            with connected_clients_lock:
                connected_clients[self.id] = self
            set_acc_status(self.id, 'online')

            while self.running:
                try:
                    self.DaTa = self.CliEnts.recv(1024)
                    if len(self.DaTa) == 0:
                        break
                except Exception:
                    break

            with connected_clients_lock:
                connected_clients.pop(self.id, None)
            set_acc_status(self.id, 'connecting')

            if self.running:
                time.sleep(1)
                self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)
        except Exception:
            with connected_clients_lock:
                connected_clients.pop(self.id, None)
            set_acc_status(self.id, 'connecting')
            if self.running:
                time.sleep(1)
                self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)

    def GeT_Key_Iv(self, serialized_data):
        my_message = MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp = my_message.field21
        key = my_message.field22
        iv = my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        combined_timestamp = timestamp_obj.seconds * 1_000_000_000 + timestamp_obj.nanos
        return combined_timestamp, key, iv

    def Guest_GeneRaTe(self, uid, password):
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close"
        }
        dataa = {
            "uid": f"{uid}", "password": f"{password}", "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }
        try:
            response = requests.post(url, headers=headers, data=dataa, timeout=10)
            response.raise_for_status()
            resp = response.json()
            if 'access_token' not in resp:
                return None
            return self.ToKen_GeneRaTe(resp['access_token'], resp['open_id'])
        except Exception:
            time.sleep(1)
            return None

    def GeT_LoGin_PorTs(self, JwT_ToKen, PayLoad):
        url = 'https://clientbp.ggpolarbear.com/GetLoginData'
        headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2022.3.47f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
            'Host': 'clientbp.ggpolarbear.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip'
        }
        for attempt in range(3):
            try:
                res = requests.post(url, headers=headers, data=PayLoad, verify=False, timeout=10)
                if res.status_code == 503:
                    time.sleep(1)
                    continue
                res.raise_for_status()
                besto = json.loads(DeCode_PackEt(res.content.hex()))
                if '32' not in besto or '14' not in besto:
                    continue
                address = besto['32']['data']
                address2 = besto['14']['data']
                ip, ip2 = address[:len(address) - 6], address2[:len(address2) - 6]
                port, port2 = address[len(address) - 5:], address2[len(address2) - 5:]
                return ip, port, ip2, port2
            except Exception:
                time.sleep(1)
                continue
        return None, None, None, None

    def ToKen_GeneRaTe(self, Access_ToKen, Access_Uid):
        try:
            self.PLaFTrom = "4"
            self.Version, self.V = '2024010012', '1.130.1'
            pyl = {
                3: str(datetime.now())[:-7], 4: "free fire", 5: 2, 7: self.V,
                8: "Android OS 11 / API-30 (RQ3A.210805.001)", 9: "Handheld", 10: "Verizon",
                11: "WIFI", 12: 1080, 13: 2400, 14: "440", 15: "ARMv8", 16: 6144,
                17: "Adreno (TM) 650", 18: "OpenGL ES 3.2 V@1.50",
                19: "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57", 20: "", 21: "en",
                22: Access_Uid, 23: self.PLaFTrom, 24: "Handheld", 25: "google G011A",
                29: Access_ToKen, 30: 3, 41: "Verizon", 42: "WIFI",
                57: "1ac4b80ecf0478a44203bf8fac6120f5", 60: 32966, 61: 29779, 62: 2479,
                63: 914, 64: 31176, 65: 32966, 66: 31176, 67: 32966, 70: 4, 73: 2,
                74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
                76: 1, 77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
                78: 6, 79: 1, 81: "64", 83: self.Version, 86: "OpenGLES3", 87: 255,
                88: self.PLaFTrom,
                89: "J\u0003FD\u0004\r_UH\u0003\u000b\u0016_\u0003D^J>\u000fWT\u0000\\=\nQ_;\u0000\r;Z\u0005a",
                90: "Phoenix", 91: "AZ", 92: 10214, 93: "3rd_party",
                94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
                95: 111207, 97: 1, 98: 1, 99: f"{self.PLaFTrom}", 100: f"{self.PLaFTrom}"
            }
            pyl_hex = CrEaTe_ProTo(pyl).hex()
            payload = bytes.fromhex(EnC_AEs(pyl_hex))

            context = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=10)
            headers = {
                'X-Unity-Version': '2018.4.11f1', 'ReleaseVersion': 'OB54',
                'Content-Type': 'application/x-www-form-urlencoded', 'X-GA': 'v1 1',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
                'Host': 'loginbp.ggpolarbear.com', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
            }
            conn.request("POST", "/MajorLogin", body=payload, headers=headers)
            response = conn.getresponse()
            raw_data = response.read()
            if response.getheader('Content-Encoding') == 'gzip':
                with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                    raw_data = f.read()
            if response.status not in [200, 201]:
                return None

            besto = json.loads(DeCode_PackEt(raw_data.hex()))
            jwt_token = besto['8']['data']
            combined_timestamp, key, iv = self.GeT_Key_Iv(raw_data)
            ip, port, ip2, port2 = self.GeT_LoGin_PorTs(jwt_token, payload)
            return jwt_token, key, iv, combined_timestamp, ip, port, ip2, port2
        except Exception:
            return None


def load_accounts_from_file(filename=None):
    filename = filename or ACCOUNTS_FILE
    accounts = []
    try:
        if not os.path.exists(filename):
            print(f"{RED}File not found: {filename}{RESET}")
            return accounts
        
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    uid, password = line.split(':', 1)
                    uid = uid.strip()
                    password = password.strip()
                    if uid and password:
                        accounts.append({'id': uid, 'password': password})
        
        print(f"{GREEN}Loaded {len(accounts)} accounts from {filename}{RESET}")
        return accounts
    except Exception as e:
        print(f"{RED}Error loading accounts: {e}{RESET}")
        return accounts


def start_account(account):
    try:
        FF_CLient(account['id'], account['password'])
    except Exception:
        set_acc_status(account['id'], 'offline')
        time.sleep(1)


def start_accounts():
    global ACCOUNTS
    time.sleep(1)
    print(f"Loading accounts from: {ACCOUNTS_FILE}")
    ACCOUNTS = load_accounts_from_file()
    if not ACCOUNTS:
        print(f"{RED}No accounts found in accounts.json{RESET}")
        return
    with all_accounts_lock:
        for a in ACCOUNTS:
            all_accounts[a['id']] = {'id': a['id'], 'password': a['password'], 'status': 'offline'}
    for account in ACCOUNTS:
        threading.Thread(target=start_account, args=(account,), daemon=True).start()
        time.sleep(0.05)


def fetch_target_info(uid):
    global current_target_info
    token = None
    with connected_clients_lock:
        for _, c in connected_clients.items():
            if getattr(c, 'JwT_ToKen', None):
                token = c.JwT_ToKen
                break
    info = None
    if token:
        info = GeT_PLayer_InFo(uid, token)
    with target_info_lock:
        current_target_info = info
    return info


def set_target_for_all(target_id):
    global current_target
    current_target = target_id
    with connected_clients_lock:
        for _, client in connected_clients.items():
            client.set_target(target_id)
    threading.Thread(target=fetch_target_info, args=(target_id,), daemon=True).start()


def is_owner(user_id):
    return user_id == OWNER_ID


def fmt_info(info, uid):
    if not info:
        return f"<b>UID:</b> <code>{uid}</code>\n<b>Info:</b> Fetching..."
    name = info.get('nickname') or '-'
    iuid = info.get('uid') or uid
    level = info.get('level') if info.get('level') is not None else '-'
    likes = info.get('likes') if info.get('likes') is not None else '-'
    server = info.get('server') or '-'
    login = info.get('last_login') or '-'
    return (f"<b>👤 Name:</b> <b>{name}</b>\n"
            f"<b>🆔 UID:</b> <code>{iuid}</code>\n"
            f"<b>⭐ Level:</b> <b>{level}</b>\n"
            f"<b>❤️ Likes:</b> <b>{likes}</b>\n"
            f"<b>🌍 Server:</b> <b>{server}</b>\n"
            f"<b>🕐 Last Login:</b> <b>{login}</b>")


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


_info_loop = None


def _info_loop_worker(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def start_info_engine():
    """Direct info engine - fetches player info straight from game servers (NO API)."""
    global _info_loop
    try:
        import Ace_app as Ace
        Ace.Ace_token_manager = Ace.Ace_TokenManager()
        Ace.Ace_load_request_cache()
        _info_loop = asyncio.new_event_loop()
        threading.Thread(target=_info_loop_worker, args=(_info_loop,), daemon=True).start()

        def _warm():
            try:
                fut = asyncio.run_coroutine_threadsafe(
                    Ace.Ace_token_manager.Ace_get_token(), _info_loop)
                tok = fut.result(timeout=90)
                if tok:
                    print(f"{GREEN}Info engine ready (direct, no API) [OK]{RESET}")
                else:
                    print(f"{YELLOW}Info engine: no token yet, will retry on demand{RESET}")
            except Exception as e:
                print(f"{YELLOW}Info engine warm-up: {e}{RESET}")
        threading.Thread(target=_warm, daemon=True).start()
    except Exception as e:
        print(f"{RED}Info engine failed to start: {e}{RESET}")


def fetch_full_info(uid):
    """Fetch player info directly from game servers - no API needed."""
    try:
        import Ace_app as Ace
        if _info_loop is None or Ace.Ace_token_manager is None:
            return None
        fut = asyncio.run_coroutine_threadsafe(
            Ace.Ace_get_account_information(str(uid)), _info_loop)
        data = fut.result(timeout=60)
        if data:
            return Ace.Ace_format_response(data)
    except Exception:
        pass
    return None


def fmt_full_info(data, uid):
    if not data or data.get('error'):
        return None
    acc = data.get('AccountInfo', {})
    rank = data.get('RankInfo', {})
    guild = data.get('GuildInfo', {})
    owner = data.get('GuildOwnerInfo', {})
    social = data.get('SocialInfo', {})
    pet = data.get('PetInfo', {})
    credit = data.get('CreditScoreInfo', {})
    diamond = data.get('DiamondInfo', {})
    parts = []
    parts.append(f"<b>━━━ 🎮 {esc(BOT_NAME)} 🎮 ━━━</b>")
    parts.append(f"\n<b>👤 Account Info:</b>")
    parts.append(f"<b>• Name:</b> <b>{esc(acc.get('AccountName', 'Unknown'))}</b>")
    parts.append(f"<b>• UID:</b> <code>{esc(acc.get('AccountUID', uid))}</code>")
    parts.append(f"<b>• Region:</b> <b>{esc(acc.get('AccountRegion', 'Unknown'))}</b>")
    parts.append(f"<b>• Level:</b> <b>{esc(acc.get('AccountLevel', '0'))}</b>")
    parts.append(f"<b>• EXP:</b> <b>{esc(acc.get('AccountEXP', '0'))}</b>")
    parts.append(f"<b>• Likes:</b> <b>{esc(acc.get('AccountLikes', '0'))}</b>")
    parts.append(f"<b>• Created:</b> <b>{esc(acc.get('AccountCreateTime', '0'))}</b>")
    parts.append(f"<b>• Account Age:</b> <b>{esc(acc.get('AccountAge', 'Unknown'))}</b>")
    parts.append(f"<b>• Last Login:</b> <b>{esc(acc.get('AccountLastLogin', '0'))}</b>")
    parts.append(f"<b>• Last Login Ago:</b> <b>{esc(acc.get('AccountLastLoginAgo', 'Unknown'))}</b>")
    parts.append(f"<b>• Elite Pass:</b> <b>{'Yes ✅' if acc.get('HasElitePass') == '1' else 'No ❌'}</b>")
    parts.append(f"<b>• Banned:</b> <b>{'Yes 🚫' if acc.get('IsBanned') == '1' else 'No ✅'}</b>")
    parts.append(f"\n<b>🏆 Rank Info:</b>")
    parts.append(f"<b>• BR Rank:</b> <b>{esc(rank.get('BrRank', '0'))}</b> (<b>{esc(rank.get('BrRankPoint', '0'))}</b> pts)")
    parts.append(f"<b>• BR Max Rank:</b> <b>{esc(rank.get('BrMaxRank', '0'))}</b>")
    parts.append(f"<b>• CS Rank:</b> <b>{esc(rank.get('CsRank', '0'))}</b> (<b>{esc(rank.get('CsRankPoint', '0'))}</b> pts)")
    parts.append(f"<b>• CS Max Rank:</b> <b>{esc(rank.get('CsMaxRank', '0'))}</b>")
    parts.append(f"\n<b>🛡 Guild Info:</b>")
    parts.append(f"<b>• Guild:</b> <b>{esc(guild.get('GuildName', 'No Guild'))}</b>")
    parts.append(f"<b>• Guild ID:</b> <code>{esc(guild.get('GuildID', '0'))}</code>")
    parts.append(f"<b>• Guild Level:</b> <b>{esc(guild.get('GuildLevel', '0'))}</b>")
    parts.append(f"<b>• Members:</b> <b>{esc(guild.get('GuildMember', '0'))}/{esc(guild.get('GuildCapacity', '0'))}</b>")
    if guild.get('GuildName', 'No Guild') != 'No Guild':
        parts.append(f"<b>• Owner:</b> <b>{esc(owner.get('OwnerName', 'Unknown'))}</b> (<code>{esc(owner.get('OwnerUID', '0'))}</code>)")
    parts.append(f"\n<b>💬 Social Info:</b>")
    sig = social.get('Signature', '') or ''
    if sig:
        parts.append(f"<b>• Signature:</b> <b>{esc(sig)}</b>")
    parts.append(f"<b>• Language:</b> <b>{esc(social.get('Language', '0'))}</b>")
    parts.append(f"\n<b>🐾 Pet Info:</b>")
    parts.append(f"<b>• Pet:</b> <b>{esc(pet.get('PetName', 'None'))}</b> | <b>Level:</b> <b>{esc(pet.get('PetLevel', '0'))}</b>")
    parts.append(f"\n<b>📊 Other:</b>")
    parts.append(f"<b>• Credit Score:</b> <b>{esc(credit.get('CreditScore', '0'))}</b>")
    parts.append(f"<b>• Diamond Cost:</b> <b>{esc(diamond.get('DiamondCost', '0'))}</b>")
    parts.append(f"\n<b>━━━ ⚡ {esc(BOT_NAME)} ⚡ ━━━</b>")
    return "\n".join(parts)


async def send_reply(update_or_msg, text, reply_markup=None):
    try:
        if os.path.exists(BOT_PHOTO):
            with open(BOT_PHOTO, 'rb') as ph:
                return await update_or_msg.reply_photo(
                    photo=ph, caption=text, parse_mode=ParseMode.HTML,
                    has_spoiler=True, reply_markup=reply_markup)
    except Exception:
        pass
    return await update_or_msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user or is_owner(user.id):
        return True
    with settings_lock:
        channels = list(SETTINGS.get('force_channels', []))
    if not channels:
        return True
    missing = []
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(ch['id'], user.id)
            if member.status in ('left', 'kicked'):
                missing.append(ch)
        except Exception:
            missing.append(ch)
    if not missing:
        return True
    buttons = []
    for ch in missing:
        link = ch.get('link') or (f"https://t.me/{ch['id'].lstrip('@')}" if str(ch['id']).startswith('@') else None)
        if link:
            buttons.append([InlineKeyboardButton(f"📢 Join {ch.get('title') or ch['id']}", url=link)])
    buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="fj_verify")])
    text = "<b>⚠️ You must join our channel(s)/group(s) to use this bot:</b>"
    if update.callback_query:
        await update.callback_query.answer("❌ You have not joined all channels yet!", show_alert=True)
        await send_reply(update.callback_query.message, text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await send_reply(update.message, text, reply_markup=InlineKeyboardMarkup(buttons))
    return False


async def guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    if is_owner(user.id):
        return True
    with settings_lock:
        maint = SETTINGS.get('maintenance', False)
    if maint:
        await send_reply(update.message, "<b>𝘼𝘾𝙀ㅤ𖤐𝙇𝙞𝙫𝙚 𝙞𝙣 𝙨𝙞𝙡𝙚𝙣𝙘𝙚.𝙈𝙤𝙫𝙚 𝙬𝙞𝙩𝙝 𝙥𝙤𝙬𝙚𝙧. ⚡</b>")
        return False
    return await check_force_join(update, context)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    text = (f"<b>⚡ Welcome to {esc(BOT_NAME)} ⚡</b>\n\n"
            "<b>Commands:</b>\n"
            "<b>++ uid</b> ➜ <b>Start room requests</b> (ex: <code>++ 123456789</code>)\n"
            "<b>-- uid</b> ➜ <b>Stop room requests</b> (ex: <code>-- 123456789</code>)\n"
            "<b>/info uid</b> ➜ <b>Full player info</b> (ex: <code>/info 123456789</code>)\n"
            "<b>/status</b> ➜ <b>Bot &amp; accounts status</b>\n"
            "<b>/list</b> ➜ <b>Accounts sending room requests</b>")
    if is_owner(update.effective_user.id):
        text += "\n<b>/panel</b> ➜ <b>Owner panel</b>"
    await send_reply(update.message, text)


async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    uid = None
    if context.args:
        uid = context.args[0].strip()
    elif update.message.text:
        parts = update.message.text.strip().split()
        if len(parts) > 1:
            uid = parts[1].strip()
    if not uid or not uid.isdigit():
        await send_reply(update.message,
                         "<b>⚠️ Usage:</b> <code>/info 123456789</code>")
        return
    wait = await send_reply(update.message,
                            f"<b>🔍 Fetching full info for UID:</b> <code>{uid}</code>\n<b>⏳ Please wait...</b>")
    data = await asyncio.to_thread(fetch_full_info, uid)
    text = fmt_full_info(data, uid)
    if not text:
        text = (f"<b>❌ Could not fetch info for UID:</b> <code>{uid}</code>\n"
                f"<b>Make sure the player exists (ME region) and inFo.txt accounts are valid.</b>")
    try:
        await wait.delete()
    except Exception:
        pass
    await send_reply(update.message, text)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    with connected_clients_lock:
        online = len(connected_clients)
    with all_accounts_lock:
        total = len(all_accounts)
        connecting = sum(1 for a in all_accounts.values() if a['status'] == 'connecting')
    offline = total - online - connecting
    if offline < 0:
        offline = 0
    with state_lock:
        running = spam_running
        target = current_target
    with target_info_lock:
        info = current_target_info

    spam_txt = "<b>Running ⚡</b>" if running else "<b>Stopped ⏹</b>"
    text = (f"<b>📊 {esc(BOT_NAME)} Status</b>\n\n"
            f"<b>👥 Total accounts:</b> <b>{total}</b>\n"
            f"<b>🟢 Online:</b> <b>{online}</b>\n"
            f"<b>🟡 Connecting:</b> <b>{connecting}</b>\n"
            f"<b>🔴 Offline:</b> <b>{offline}</b>\n"
            f"<b>⚡ Spam:</b> {spam_txt}\n"
            f"<b>🎯 Target:</b> <code>{target or '-'}</code>\n"
            f"<b>⏱ Interval:</b> <b>{spam_speed}s</b>")
    if running and (info or target):
        text += "\n\n<b>🎯 Target Player:</b>\n" + fmt_info(info, target)
    await send_reply(update.message, text)


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    with connected_clients_lock:
        clients = list(connected_clients.values())
    if not clients:
        await send_reply(update.message, "<b>📋 No online accounts sending room requests right now.</b>")
        return
    lines = ["<b>📋 Accounts Sending Room Requests:</b>\n"]
    for i, c in enumerate(clients, 1):
        puid = getattr(c, 'account_uid', None) or '-'
        lines.append(f"<b>{i}.</b> <code>{c.id}</code> ➜ <b>Player UID:</b> <code>{puid}</code> 🟢")
    lines.append(f"\n<b>Total online:</b> <b>{len(clients)}</b>")
    await send_reply(update.message, "\n".join(lines))


async def handle_plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    global spam_running
    uid = update.message.text.strip()[2:].strip()
    if not uid.isdigit():
        await send_reply(update.message, "<b>⚠️ Invalid UID. Use numbers only.</b>")
        return
    with connected_clients_lock:
        if not connected_clients:
            await send_reply(update.message, "<b>❌ No accounts are online right now. Try again later.</b>")
            return
    with state_lock:
        spam_running = True
    set_target_for_all(uid)
    info = None
    for _ in range(10):
        with target_info_lock:
            info = current_target_info
        if info:
            break
        await asyncio.sleep(0.4)
    text = ("<b>✅ Room requests have been STARTED on the target player! ⚡</b>\n\n"
            + fmt_info(info, uid))
    await send_reply(update.message, text)


async def handle_minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update, context):
        return
    global spam_running, current_target, current_target_info, last_target_info
    uid = update.message.text.strip()[2:].strip()
    with target_info_lock:
        info = current_target_info or last_target_info
    with state_lock:
        was_running = spam_running
        spam_running = False
        current_target = None
    with connected_clients_lock:
        for _, client in connected_clients.items():
            client.target_id = None
    with target_info_lock:
        if current_target_info:
            last_target_info = current_target_info
        current_target_info = None
    if not was_running:
        await send_reply(update.message, "<b>ℹ️ Room requests are already stopped.</b>")
        return
    text = ("<b>⏹ Room requests have been STOPPED on the target player!</b>\n\n"
            + fmt_info(info, uid if uid.isdigit() else (info.get('uid') if info else uid)))
    await send_reply(update.message, text)


def panel_keyboard():
    with settings_lock:
        maint = SETTINGS.get('maintenance', False)
        ch_count = len(SETTINGS.get('force_channels', []))
    mtxt = "🛠 Maintenance: ON ✅" if maint else "🛠 Maintenance: OFF ❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(mtxt, callback_data="pn_maint")],
        [InlineKeyboardButton(f"📢 Force Join Channels ({ch_count})", callback_data="pn_fj")],
        [InlineKeyboardButton("📊 Status", callback_data="pn_status")],
        [InlineKeyboardButton("❌ Close", callback_data="pn_close")],
    ])


async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await send_reply(update.message,
                     f"<b>👑 Owner Panel - {esc(BOT_NAME)}</b>\n<b>Choose an option:</b>",
                     reply_markup=panel_keyboard())


async def fj_keyboard():
    with settings_lock:
        channels = list(SETTINGS.get('force_channels', []))
    buttons = []
    for i, ch in enumerate(channels):
        buttons.append([InlineKeyboardButton(f"🗑 Remove {ch.get('title') or ch['id']}",
                                             callback_data=f"fj_del_{i}")])
    buttons.append([InlineKeyboardButton("➕ Add Channel / Group", callback_data="fj_add")])
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="pn_back")])
    return InlineKeyboardMarkup(buttons)


async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user = q.from_user

    if data == "fj_verify":
        ok = await check_force_join(update, context)
        if ok:
            await q.answer("✅ Verified! You can use the bot now.", show_alert=True)
            try:
                await q.message.delete()
            except Exception:
                pass
        return

    if not is_owner(user.id):
        await q.answer("❌ Owner only.", show_alert=True)
        return

    if data == "pn_maint":
        with settings_lock:
            SETTINGS['maintenance'] = not SETTINGS.get('maintenance', False)
            save_settings(SETTINGS)
            st = SETTINGS['maintenance']
        await q.answer(f"Maintenance {'ON 🛠' if st else 'OFF ✅'}", show_alert=True)
        await q.message.edit_text(f"<b>👑 Owner Panel - {esc(BOT_NAME)}</b>\n<b>Choose an option:</b>",
                                  parse_mode=ParseMode.HTML, reply_markup=panel_keyboard())

    elif data == "pn_status":
        with connected_clients_lock:
            online = len(connected_clients)
        with all_accounts_lock:
            total = len(all_accounts)
        with state_lock:
            running = spam_running
        await q.answer(f"Total: {total} | Online: {online} | Spam: {'ON' if running else 'OFF'}",
                       show_alert=True)

    elif data == "pn_fj":
        await q.answer()
        await q.message.edit_text("<b>📢 Force Join Management</b>\n"
                                  "<b>Add or remove channels/groups users must join:</b>",
                                  parse_mode=ParseMode.HTML, reply_markup=await fj_keyboard())

    elif data == "fj_add":
        await q.answer()
        context.user_data['awaiting_channel'] = True
        await q.message.edit_text("<b>➕ Send the channel/group now:</b>\n"
                                  "<b>• @username (public channel/group)</b>\n"
                                  "<b>• or forward-free invite link https://t.me/xxxx</b>\n\n"
                                  "<b>⚠️ Bot must be admin in the channel/group.</b>\n"
                                  "<b>Send /cancel to abort.</b>",
                                  parse_mode=ParseMode.HTML)

    elif data.startswith("fj_del_"):
        idx = int(data.split("_")[-1])
        with settings_lock:
            chs = SETTINGS.get('force_channels', [])
            removed = chs.pop(idx) if 0 <= idx < len(chs) else None
            save_settings(SETTINGS)
        await q.answer(f"Removed {removed.get('title') or removed.get('id')}" if removed else "Not found",
                       show_alert=True)
        await q.message.edit_text("<b>📢 Force Join Management</b>\n"
                                  "<b>Add or remove channels/groups users must join:</b>",
                                  parse_mode=ParseMode.HTML, reply_markup=await fj_keyboard())

    elif data == "pn_back":
        await q.answer()
        await q.message.edit_text(f"<b>👑 Owner Panel - {esc(BOT_NAME)}</b>\n<b>Choose an option:</b>",
                                  parse_mode=ParseMode.HTML, reply_markup=panel_keyboard())

    elif data == "pn_close":
        await q.answer()
        try:
            await q.message.delete()
        except Exception:
            pass


async def owner_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    if not context.user_data.get('awaiting_channel'):
        return
    context.user_data['awaiting_channel'] = False
    raw = update.message.text.strip()

    ch_id = None
    link = None
    if raw.startswith('@'):
        ch_id = raw
        link = f"https://t.me/{raw.lstrip('@')}"
    elif 't.me/' in raw:
        uname = raw.split('t.me/')[-1].strip('/').split('/')[0]
        if uname and not uname.startswith('+'):
            ch_id = '@' + uname
            link = f"https://t.me/{uname}"
        else:
            ch_id = None
            link = raw
    elif raw.lstrip('-').isdigit():
        ch_id = int(raw)

    if ch_id is None:
        await send_reply(update.message,
            "<b>⚠️ Private invite link detected.</b>\n"
            "<b>Please send the numeric chat ID (ex: -1001234567890) instead, or use a public @username.</b>")
        return

    try:
        chat = await context.bot.get_chat(ch_id)
        title = chat.title or str(ch_id)
        if not link and getattr(chat, 'username', None):
            link = f"https://t.me/{chat.username}"
    except Exception:
        await send_reply(update.message,
            "<b>❌ Cannot access this chat. Make sure the bot is added and admin there.</b>")
        return

    with settings_lock:
        SETTINGS.setdefault('force_channels', []).append(
            {"id": str(ch_id), "title": title, "link": link or ""})
        save_settings(SETTINGS)
    await send_reply(update.message,
        f"<b>✅ Added:</b> <b>{esc(title)}</b> (<code>{ch_id}</code>)",
        reply_markup=await fj_keyboard())


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_channel'] = False
    await send_reply(update.message, "<b>❌ Cancelled.</b>")


def run_bot():
    print(f"{GREEN}[START]{RESET} {BOT_NAME} ... (interval={spam_speed}s per invite)")
    start_info_engine()
    threading.Thread(target=start_accounts, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("info", cmd_info))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("panel", cmd_panel))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CallbackQueryHandler(panel_callback))
    app.add_handler(MessageHandler(filters.Regex(r'^\+\+\s*\d+\s*$'), handle_plus))
    app.add_handler(MessageHandler(filters.Regex(r'^--\s*\d+\s*$'), handle_minus))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, owner_text_input))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()