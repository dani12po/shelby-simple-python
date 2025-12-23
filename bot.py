#!/usr/bin/env python3
"""
Shelby Menu Bot (Python) - Create Wallet + Auto Sync to pk.txt (NO yaml dependency)

Run:
  python bot.py

Menu:
  1) Check balance
  2) Claim ShelbyUSD faucet (best-effort)
  3) Claim APT faucet (best-effort)
  4) Upload file (auto dst)
  5) Upload file (custom dst)
  6) Create wallet (then auto sync pk.txt)
  7) Sync pk.txt from config.yaml (no create)
  8) Exit

pk.txt format:
accounts:
  alias:
    address: "0x..."
    private_key: ed25519-priv-0x...

Security:
- pk.txt contains PRIVATE KEYS. Keep it secret. DO NOT COMMIT.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Optional

import requests
from dotenv import load_dotenv


# ----------------------------
# Models
# ----------------------------
@dataclass
class Balance:
    address: Optional[str] = None
    apt: Optional[Decimal] = None
    shelbyusd: Optional[Decimal] = None
    raw_text: str = ""


# ----------------------------
# Helpers
# ----------------------------
def eprint(*a: object) -> None:
    print(*a, file=sys.stderr)


def pause() -> None:
    input("\nPress Enter to continue...")


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def yes_no(prompt: str, default_yes: bool = True) -> bool:
    d = "Y/n" if default_yes else "y/N"
    s = input(f"{prompt} ({d}): ").strip().lower()
    if not s:
        return default_yes
    return s in ("y", "yes", "1", "true")


def bot_dir() -> Path:
    return Path(__file__).resolve().parent


def pk_path() -> Path:
    # same directory as bot.py
    return bot_dir() / "pk.txt"


def shelby_config_path() -> Path:
    # optional override: SHELBY_CONFIG_PATH=C:\Users\you\.shelby\config.yaml
    custom = os.getenv("SHELBY_CONFIG_PATH")
    if custom:
        return Path(custom).expanduser()
    return Path.home() / ".shelby" / "config.yaml"


def find_shelby_bin() -> str:
    # recommended in .env (Windows): SHELBY_BIN=shelby.cmd
    env_bin = os.getenv("SHELBY_BIN")
    if env_bin:
        return env_bin

    for cand in ("shelby", "shelby.cmd", "shelby.exe"):
        if shutil.which(cand):
            return cand
    return "shelby"


def run_cmd(args: list[str], capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    """
    Safe subprocess on Windows:
    - Force UTF-8 decode, errors=replace => avoid UnicodeDecodeError
    """
    try:
        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")

        return subprocess.run(
            args,
            check=check,
            text=True,
            capture_output=capture,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
    except FileNotFoundError as ex:
        raise RuntimeError(
            f"Command not found: {args[0]}\n"
            "Fix:\n"
            "  1) Install Shelby CLI: npm i -g @shelby-protocol/cli\n"
            "  2) Or set SHELBY_BIN in .env (Windows usually: shelby.cmd)\n"
        ) from ex
    except subprocess.CalledProcessError as ex:
        msg = (ex.stderr or "").strip() or (ex.stdout or "").strip() or str(ex)
        raise RuntimeError(msg) from ex


def parse_decimal(s: str) -> Optional[Decimal]:
    try:
        return Decimal(s.replace(",", ""))
    except Exception:
        return None


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


# ----------------------------
# Parse accounts: works for BOTH config.yaml and pk.txt
# ----------------------------
def parse_accounts_accounts_section(text: str) -> Dict[str, Dict[str, str]]:
    """
    Parse ONLY this structure (your desired):
    accounts:
      alias:
        address: "0x..."
        private_key: ed25519-priv-0x...

    Returns:
      { alias: {"address": "...", "private_key": "..."} }
    """
    lines = text.splitlines()

    # find "accounts:"
    start = -1
    for i, line in enumerate(lines):
        if re.match(r"^\s*accounts\s*:\s*$", line):
            start = i
            break
    if start == -1:
        return {}

    accounts: Dict[str, Dict[str, str]] = {}
    current_alias = ""  # always str, never None (fix pylance warnings)

    for line in lines[start + 1 :]:
        # stop when another top-level key begins (no indentation)
        if re.match(r"^[A-Za-z0-9_.-]+\s*:\s*$", line) and not line.startswith(" "):
            break

        # alias line: "  danns:"
        m_alias = re.match(r"^\s{2}([A-Za-z0-9_.-]+)\s*:\s*$", line)
        if m_alias:
            current_alias = m_alias.group(1)
            if current_alias not in accounts:
                accounts[current_alias] = {}
            continue

        if not current_alias:
            continue

        # address: can be quoted or not
        m_addr = re.match(r"^\s{4}address\s*:\s*(.+?)\s*$", line)
        if m_addr:
            accounts[current_alias]["address"] = _strip_quotes(m_addr.group(1))
            continue

        # private_key
        m_pk = re.match(r"^\s{4}private_key\s*:\s*(\S+)\s*$", line)
        if m_pk:
            accounts[current_alias]["private_key"] = _strip_quotes(m_pk.group(1))
            continue

    # cleanup: keep only accounts that have at least one field
    accounts = {a: d for a, d in accounts.items() if d.get("address") or d.get("private_key")}
    return accounts


def read_accounts_file(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8", errors="replace")
    return parse_accounts_accounts_section(raw)


def write_pk_yaml(accounts: Dict[str, Dict[str, str]]) -> Path:
    """
    Write pk.txt in YAML format exactly as you want.
    """
    lines: list[str] = []
    lines.append("# IMPORTANT: This file contains PRIVATE KEYS. KEEP IT SECRET. DO NOT COMMIT.\n")
    lines.append("accounts:\n")

    for alias in sorted(accounts.keys()):
        addr = (accounts[alias].get("address") or "").strip()
        pk = (accounts[alias].get("private_key") or "").strip()

        lines.append(f"  {alias}:\n")
        if addr:
            lines.append(f'    address: "{addr}"\n')
        if pk:
            lines.append(f"    private_key: {pk}\n")

    out = pk_path()
    out.write_text("".join(lines), encoding="utf-8")
    return out


def sync_config_to_pk(verbose: bool = True) -> Path:
    """
    Your required behavior:
    - If pk.txt not exist -> create it
    - Read config.yaml accounts
    - Read pk.txt accounts (if exists)
    - If there are accounts in config.yaml missing from pk.txt -> add them
    - If alias exists in pk but missing address/private_key -> fill it (from config)
    - If mismatch values exist -> DO NOT overwrite, just warn
    """
    cfg = shelby_config_path()
    if not cfg.exists():
        raise FileNotFoundError(f"Config not found: {cfg}")

    cfg_accounts = read_accounts_file(cfg)
    if not cfg_accounts:
        raise RuntimeError("No accounts found in config.yaml (accounts section not detected).")

    pk_accounts = read_accounts_file(pk_path())

    added = 0
    filled = 0
    mismatches = 0

    for alias, d in cfg_accounts.items():
        cfg_addr = (d.get("address") or "").strip()
        cfg_pk = (d.get("private_key") or "").strip()

        if alias not in pk_accounts:
            pk_accounts[alias] = {"address": cfg_addr, "private_key": cfg_pk}
            added += 1
            continue

        # fill missing fields only
        pk_addr = (pk_accounts[alias].get("address") or "").strip()
        pk_priv = (pk_accounts[alias].get("private_key") or "").strip()

        if not pk_addr and cfg_addr:
            pk_accounts[alias]["address"] = cfg_addr
            filled += 1

        if not pk_priv and cfg_pk:
            pk_accounts[alias]["private_key"] = cfg_pk
            filled += 1

        # mismatch detection (no overwrite)
        pk_addr2 = (pk_accounts[alias].get("address") or "").strip()
        pk_priv2 = (pk_accounts[alias].get("private_key") or "").strip()

        if cfg_addr and pk_addr2 and cfg_addr != pk_addr2:
            mismatches += 1
        if cfg_pk and pk_priv2 and cfg_pk != pk_priv2:
            mismatches += 1

    out = write_pk_yaml(pk_accounts)

    if verbose:
        print(f"\n✅ pk.txt synced: {out}")
        print(f"   - Added new accounts: {added}")
        print(f"   - Filled missing fields: {filled}")
        if mismatches:
            print(f"   - ⚠️ Mismatches detected: {mismatches} (not overwritten; check manually)")
        print(f"   - Source config: {cfg}")

    return out


# ----------------------------
# Shelby features (balance, faucet, upload, create)
# ----------------------------
def shelby_balance(shelby_bin: str) -> Balance:
    proc = run_cmd([shelby_bin, "account", "balance"], capture=True, check=True)
    text = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    b = Balance(raw_text=text)

    m = re.search(r"Address:\s*(0x[a-fA-F0-9]+)", text)
    if m:
        b.address = m.group(1)

    mapt = re.search(r"\|\s*APT\s*\|.*?\|\s*([0-9.,]+)\s*APT\s*\|", text, flags=re.S)
    if mapt:
        b.apt = parse_decimal(mapt.group(1))

    msu = re.search(r"\|\s*ShelbyUS.*?\|\s*([0-9.,]+)\s*ShelbyUSD\s*\|", text, flags=re.S)
    if msu:
        b.shelbyusd = parse_decimal(msu.group(1))

    return b


def print_balance(b: Balance) -> None:
    print("\n== Balance ==")
    if b.address:
        print(f"Address   : {b.address}")
    print(f"APT       : {b.apt if b.apt is not None else '(unknown)'}")
    print(f"ShelbyUSD : {b.shelbyusd if b.shelbyusd is not None else '(unknown)'}")
    print("\n--- Raw output ---\n")
    print(b.raw_text.strip())


def get_shelbyusd_faucet_url(shelby_bin: str) -> Optional[str]:
    try:
        proc = run_cmd([shelby_bin, "faucet", "--no-open"], capture=True, check=True)
        text = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        m = re.search(r"https?://\S+", text)
        return m.group(0) if m else None
    except Exception:
        return None


def claim_shelbyusd_faucet(shelby_bin: str) -> None:
    url = get_shelbyusd_faucet_url(shelby_bin)
    if not url:
        print("Could not get faucet URL. Try running: shelby faucet --no-open")
        return

    print("\nShelbyUSD Faucet URL (open in browser if needed):")
    print(url)

    try:
        r = requests.get(url, timeout=20)
        ct = r.headers.get("content-type", "")
        if "application/json" in ct:
            print("\nResponse JSON:")
            print(r.json())
        else:
            print(f"\nFetched URL (status {r.status_code}). If ShelbyUSD didn't arrive, open the URL in your browser.")
    except Exception as ex:
        print(f"\nCould not auto-request via HTTP ({ex}). Open the URL in your browser.")


def apt_to_octas(amount_apt: Decimal) -> int:
    return int((amount_apt * Decimal("100000000")).to_integral_value())


def claim_apt_faucet_http(address: str, amount_apt: Decimal) -> None:
    faucet_url = os.getenv("APTOS_FAUCET_URL", "https://faucet.shelbynet.shelby.xyz/fund")
    payload = {"address": address, "amount": apt_to_octas(amount_apt)}

    print("\nRequesting APT faucet (best-effort):")
    print(f"POST {faucet_url}")
    print(f"payload: {payload}")

    r = requests.post(faucet_url, json=payload, timeout=25)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    print(f"\nStatus: {r.status_code}")
    print("Response:", data)


def slugify_filename(name: str) -> str:
    p = Path(name)
    stem = re.sub(r"\s+", "-", p.stem.strip())
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem)
    stem = re.sub(r"-{2,}", "-", stem).strip("-") or "file"
    return f"{stem}{p.suffix.lower()}"


def ensure_trailing_slash(s: str) -> str:
    return s if s.endswith("/") else s + "/"


def choose_prefix_by_ext(ext: str) -> str:
    ext = ext.lower().lstrip(".")
    img = {"png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "svg"}
    vid = {"mp4", "mov", "mkv", "avi", "webm", "m4v"}
    if ext in img:
        return os.getenv("DEST_PREFIX_IMAGE", "images/")
    if ext in vid:
        return os.getenv("DEST_PREFIX_VIDEO", "videos/")
    return os.getenv("DEST_PREFIX_FILE", "files/")


def build_dst(local_path: Path) -> str:
    prefix = ensure_trailing_slash(choose_prefix_by_ext(local_path.suffix))
    fname = slugify_filename(local_path.name)

    if os.getenv("ADD_DATE_FOLDER", "false").lower() in ("1", "true", "yes", "y"):
        date_folder = datetime.now().strftime("%Y-%m-%d")
        prefix = ensure_trailing_slash(prefix + date_folder)

    return prefix + fname


def get_default_expiration() -> str:
    return os.getenv("DEFAULT_EXPIRATION", "in 30 days")


def shelby_upload(shelby_bin: str, src: Path, dst: str, expiration: str, assume_yes: bool = True) -> None:
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    args = [shelby_bin, "upload"]
    if assume_yes:
        args.append("--assume-yes")
    args += [str(src), dst, "--expiration", expiration]
    run_cmd(args, capture=False, check=True)


def ask_path(prompt: str) -> Path:
    s = input(prompt).strip().strip('"')
    return Path(s)


def ask_expiration() -> str:
    default = get_default_expiration()
    s = input(f"Expiration (default: {default}) : ").strip()
    return s or default


def shelby_account_create_interactive(shelby_bin: str, name: Optional[str]) -> None:
    args = [shelby_bin, "account", "create"]
    if name:
        args += ["--name", name]
    print("\nLaunching Shelby account create wizard...\n")
    run_cmd(args, capture=False, check=True)


# ----------------------------
# Menu actions
# ----------------------------
def action_balance() -> None:
    shelby_bin = find_shelby_bin()
    b = shelby_balance(shelby_bin)
    print_balance(b)


def action_claim_shelbyusd() -> None:
    shelby_bin = find_shelby_bin()
    claim_shelbyusd_faucet(shelby_bin)


def action_claim_apt() -> None:
    shelby_bin = find_shelby_bin()
    b = shelby_balance(shelby_bin)
    if not b.address:
        print("Could not detect address. Run balance first.")
        return
    amt_str = input("Request how much APT? (default 0.1) : ").strip() or "0.1"
    try:
        amt = Decimal(amt_str)
    except InvalidOperation:
        print("Invalid amount.")
        return
    claim_apt_faucet_http(b.address, amt)


def action_upload_auto() -> None:
    shelby_bin = find_shelby_bin()
    src = ask_path(r'Local file path (e.g. D:\DERP_.jpeg) : ')
    expiration = ask_expiration()
    assume_yes = yes_no("Auto-confirm cost? (--assume-yes)", True)

    dst = build_dst(src)
    print(f"\nWill upload:\n  src: {src}\n  dst: {dst}\n  expiration: {expiration}\n")
    if not yes_no("Proceed?", True):
        print("Canceled.")
        return

    shelby_upload(shelby_bin, src, dst, expiration, assume_yes=assume_yes)
    print("\n✅ Upload finished (if no errors shown above).")


def action_upload_custom() -> None:
    shelby_bin = find_shelby_bin()
    src = ask_path(r'Local file path (e.g. D:\DERP_.jpeg) : ')
    dst = input("Destination blob name (e.g. images/derp.jpeg) : ").strip()
    if not dst:
        print("Destination is required.")
        return
    expiration = ask_expiration()
    assume_yes = yes_no("Auto-confirm cost? (--assume-yes)", True)

    print(f"\nWill upload:\n  src: {src}\n  dst: {dst}\n  expiration: {expiration}\n")
    if not yes_no("Proceed?", True):
        print("Canceled.")
        return

    shelby_upload(shelby_bin, src, dst, expiration, assume_yes=assume_yes)
    print("\n✅ Upload finished (if no errors shown above).")


def action_create_wallet_auto_sync() -> None:
    print("\n⚠️ This will CREATE a NEW wallet and add it to your config.yaml.")
    if not yes_no("Continue?", False):
        print("Canceled.")
        return

    shelby_bin = find_shelby_bin()
    name = input("Account alias/name (optional, Enter to skip): ").strip() or None

    # create wallet
    shelby_account_create_interactive(shelby_bin, name)

    # then sync config -> pk
    print("\n✅ Wallet created. Syncing config.yaml -> pk.txt ...")
    out = sync_config_to_pk(verbose=True)
    print(f"\n✅ Done. pk.txt at:\n{out}")


def action_sync_only() -> None:
    out = sync_config_to_pk(verbose=True)
    print(f"\n✅ Done. pk.txt at:\n{out}")


# ----------------------------
# Menu
# ----------------------------
MENU = """\
Shelby Menu Bot
================
1) Check balance
2) Claim ShelbyUSD faucet (best-effort)
3) Claim APT faucet (best-effort)
4) Upload file (auto dst)
5) Upload file (custom dst)
6) Create wallet (then auto sync pk.txt)
7) Sync pk.txt from config.yaml (no create)
8) Exit
"""


def main() -> int:
    load_dotenv()
    clear()

    while True:
        print(MENU)
        choice = input("Select [1-8]: ").strip()

        try:
            if choice == "1":
                action_balance()
            elif choice == "2":
                action_claim_shelbyusd()
            elif choice == "3":
                action_claim_apt()
            elif choice == "4":
                action_upload_auto()
            elif choice == "5":
                action_upload_custom()
            elif choice == "6":
                action_create_wallet_auto_sync()
            elif choice == "7":
                action_sync_only()
            elif choice == "8":
                print("Bye.")
                return 0
            else:
                print("Invalid selection.")
        except Exception as ex:
            eprint("\n[ERROR]", str(ex))

        pause()
        clear()


if __name__ == "__main__":
    raise SystemExit(main())
