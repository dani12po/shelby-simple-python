# 🛠️ Shelby Simple Python

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Node.js](https://img.shields.io/badge/Node.js-16%2B-green)
![CLI](https://img.shields.io/badge/Interface-CLI-lightgrey)
![License](https://img.shields.io/badge/License-Not%20Specified-red)

**Shelby Simple Python** is a Python-based CLI (Command Line Interface) tool designed to interact with the **Shelby Protocol**.

This project helps users manage wallets, claim faucets, check balances, and upload files to the Shelby Network directly from the terminal.

> ⚠️ **Security warning:** This tool can generate and store **private keys** (e.g., `pk.txt`). Treat them like passwords. **Do not share** them and **do not commit** them to GitHub.

---

## ✨ Features

- ✅ Check APT & ShelbyUSD balance
- 💧 Claim ShelbyUSD faucet (best-effort)
- 💧 Claim APT faucet (best-effort)
- 📤 Upload files to Shelby Network (auto & custom destination)
- 🔐 Create a new wallet (via Shelby CLI)
- 🔄 Sync private keys to `pk.txt` (from `config.yaml`)
- 🖥️ Interactive terminal-based menu

---

## 📦 Requirements

Before installation, make sure you have:

- **Python** `>= 3.8`
- **Node.js** `>= 16` (includes **npm**)
- **Git** (optional but recommended)

---

## 🚀 Installation (Step by Step)

### 1️⃣ Get the code

**Option A — Clone with Git**
```bash
git clone https://github.com/dani12po/shelby-simple-python.git
cd shelby-simple-python
```

**Option B — Download ZIP**
- On GitHub, click **Code** → **Download ZIP**
- Extract the ZIP
- Open the extracted folder in your terminal

---

### 2️⃣ Create and activate a virtual environment (recommended)

#### Windows (PowerShell) ✅
```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

If you get an error like *“running scripts is disabled”*, run this **once** in the same PowerShell window, then activate again:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.env\Scripts\Activate.ps1
```

#### Windows (CMD)
```bat
python -m venv venv
venv\Scripts\activate.bat
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Install Shelby CLI (required)

```bash
npm install -g @shelby-protocol/cli
```

Verify installation:
```bash
shelby --version
```

> **Note:** The latest `bot.py` can auto-detect `shelby` and can optionally auto-install it (if `npm` is available). If you prefer to disable auto-install, set:
```env
AUTO_INSTALL_SHELBY=false
```

---

## ▶️ Usage

Run the CLI tool:

```bash
python bot.py
```

You will see a menu like this:

```
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
```

---

## ✅ Recommended first-time workflow

1. **Create a wallet** (menu option `6`)
2. **Claim APT faucet** (menu option `3`)
3. **Claim ShelbyUSD faucet** (menu option `2`)
4. **Check balance** (menu option `1`)
5. **Upload a file** (menu option `4`)

---

## 📁 Project Structure

```
shelby-simple-python/
│
├── bot.py              # Main Python CLI script
├── bot.js              # Optional JavaScript integration
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
├── pk.txt              # Auto-generated private key file (DO NOT COMMIT)
└── README.md           # Documentation
```

---

## ⚙️ Configuration (Optional)

Create a `.env` file in the same directory as `bot.py`:

```env
# Optional: set a custom Shelby binary/command (Windows usually: shelby.cmd)
SHELBY_BIN=shelby

# Optional: disable auto-install of Shelby CLI
AUTO_INSTALL_SHELBY=true

# Optional: set Shelby config path if it's not in the default location
# SHELBY_CONFIG_PATH=C:\Users\you\.shelby\config.yaml

# Optional: faucet endpoint (if you use a custom faucet)
APTOS_FAUCET_URL=https://your-faucet-url

# Optional: upload defaults
DEST_PREFIX_IMAGE=images/
DEST_PREFIX_VIDEO=videos/
DEST_PREFIX_FILE=files/
DEFAULT_EXPIRATION=in 30 days
ADD_DATE_FOLDER=false
```

---

## 🔐 Security Notes

⚠️ **Important**

- Never commit `pk.txt` to the repository
- Never share your private keys
- Always use **testnet wallets** for testing

Add to `.gitignore`:

```gitignore
pk.txt
.env
venv/
__pycache__/
*.pyc
node_modules/
```

---

## 🤝 Contribution

Contributions are welcome!

- Open an **issue** for bug reports or feature requests
- Submit a **pull request** to improve the project

---

## 📜 License

This project currently has **no license specified**.
You may add one such as **MIT** or **Apache-2.0** if needed.

---

## ⭐ Support

If this project helps you, please consider giving it a ⭐ on GitHub.
