# 🛠️ Shelby Simple Python

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Node.js](https://img.shields.io/badge/Node.js-16%2B-green)
![CLI](https://img.shields.io/badge/Interface-CLI-lightgrey)
![License](https://img.shields.io/badge/License-Not%20Specified-red)

**Shelby Simple Python** is a Python-based CLI (Command Line Interface) tool
designed to interact with the **Shelby Protocol**.

This project helps users manage wallets, claim faucets, check balances,
and upload files to the Shelby Network directly from the terminal.

---

## ✨ Features

* ✅ Check APT & ShelbyUSD balance
* 💧 Claim ShelbyUSD faucet
* 💧 Claim APT faucet
* 📤 Upload files to Shelby Network (auto & custom destination)
* 🔐 Automatically create a new wallet
* 🔄 Sync private keys to `pk.txt`
* 🖥️ Interactive terminal-based menu

---

## 📦 Requirements

Before installation, make sure you have:

* **Python** `>= 3.8`
* **Node.js** `>= 16`
* **npm`
* **Git**

---

## 🚀 Installation (Step by Step)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/dani12po/shelby-simple-python.git
cd shelby-simple-python
```

---

### 2️⃣ Create Virtual Environment (Optional but Recommended)

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Install Shelby CLI (Required)

```bash
npm install -g @shelby-protocol/cli
```

Verify installation:

```bash
shelby --version
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
===============
1) Check balance
2) Claim ShelbyUSD faucet
3) Claim APT faucet
4) Upload file (auto destination)
5) Upload file (custom destination)
6) Create wallet & auto sync pk.txt
7) Sync pk.txt from config.yaml
8) Exit
```

---

## 📁 Project Structure

```
shelby-simple-python/
│
├── bot.py              # Main Python CLI script
├── bot.js              # Optional JavaScript integration
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
├── pk.txt              # Auto-generated private key file
└── README.md           # Documentation
```

---

## ⚙️ Configuration (Optional)

Create a `.env` file:

```env
SHELBY_BIN=/path/to/shelby
APTOS_FAUCET_URL=https://your-faucet-url
DEST_PREFIX_IMAGE=images/
DEST_PREFIX_VIDEO=videos/
```

---

## 🔐 Security Notes

⚠️ **Important**

* Never commit `pk.txt` to the repository
* Never share your private keys
* Always use **testnet wallets** for testing

Add to `.gitignore`:

```gitignore
pk.txt
.env
```

---

## 🤝 Contribution

Contributions are welcome!

* Open an **issue** for bug reports or feature requests
* Submit a **pull request** to improve the project

---

## 📜 License

This project currently has **no license specified**.
You may add one such as **MIT** or **Apache-2.0** if needed.

---

## ⭐ Support

If project helps you, please consider giving it a ⭐ on GitHub.
