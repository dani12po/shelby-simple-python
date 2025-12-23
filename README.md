name: Shelby Simple Python

description: >
  Shelby Simple Python is a simple Python-based CLI (Command Line Interface)
  tool used to interact with the Shelby Protocol.
  This script helps users check balances, claim faucets,
  upload files to the Shelby Network, and create & synchronize wallets
  directly from the terminal.

features:
  - Check APT & ShelbyUSD balance
  - Claim ShelbyUSD faucet
  - Claim APT faucet
  - Upload files to Shelby Network (auto & custom destination)
  - Create a new wallet automatically
  - Sync private keys to pk.txt
  - Interactive terminal-based CLI menu

requirements:
  python:
    version: ">= 3.8"
  nodejs:
    version: ">= 16"
  npm: required
  shelby_cli:
    install_command: "npm install -g @shelby-protocol/cli"

installation:
  steps:
    - step: Clone the repository
      command: |
        git clone https://github.com/dani12po/shelby-simple-python.git
        cd shelby-simple-python

    - step: Create virtual environment (optional)
      command: |
        python -m venv venv
        source venv/bin/activate   # Linux / macOS
        venv\Scripts\activate      # Windows

    - step: Install Python dependencies
      command: |
        pip install -r requirements.txt

    - step: Install Shelby CLI
      command: |
        npm install -g @shelby-protocol/cli

usage:
  run_command: "python bot.py"
  menu:
    - Check balance
    - Claim ShelbyUSD faucet
    - Claim APT faucet
    - Upload file (auto destination)
    - Upload file (custom destination)
    - Create wallet & auto sync pk.txt
    - Sync pk.txt from config.yaml
    - Exit

project_structure:
  - bot.py: Main Python script
  - bot.js: JavaScript integration (optional)
  - requirements.txt: Python dependencies
  - package.json: Node.js dependencies
  - pk.txt: Private key file (auto generated)

configuration:
  env_example:
    SHELBY_BIN: "/path/to/shelby"
    APTOS_FAUCET_URL: "https://your-faucet-url"
    DEST_PREFIX_IMAGE: "images/"
    DEST_PREFIX_VIDEO: "videos/"

security_notes:
  - Never commit pk.txt to the repository
  - Never share your private keys
  - Use testnet wallets for experimentation

contribution:
  guide: >
    Feel free to open an issue or submit a pull request
    if you want to add features or fix bugs.

license:
  status: Not specified
  suggestion: MIT or Apache-2.0
