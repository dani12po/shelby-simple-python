project:
  name: Shelby Simple Python
  description: >
    Shelby Simple Python is a Python-based CLI (Command Line Interface) tool
    designed to interact with the Shelby Protocol.
    It allows users to manage wallets, claim faucets, check balances,
    and upload files to the Shelby Network directly from the terminal.

badges:
  - Python: ">=3.8"
  - Node.js: ">=16"
  - Interface: CLI
  - License: Not Specified

features:
  - Check APT & ShelbyUSD balance
  - Claim ShelbyUSD faucet
  - Claim APT faucet
  - Upload files to Shelby Network (auto & custom destination)
  - Automatically create a new wallet
  - Sync private keys to pk.txt
  - Interactive terminal-based menu

requirements:
  python:
    version: ">= 3.8"
  nodejs:
    version: ">= 16"
  npm: required
  git: required
  shelby_cli:
    description: Shelby Protocol CLI
    install_command: npm install -g @shelby-protocol/cli

installation:
  step_by_step:
    - step: 1
      title: Clone Repository
      commands:
        - git clone https://github.com/dani12po/shelby-simple-python.git
        - cd shelby-simple-python

    - step: 2
      title: Create Virtual Environment (Optional)
      commands:
        linux_macos:
          - python3 -m venv venv
          - source venv/bin/activate
        windows:
          - python -m venv venv
          - venv\Scripts\activate

    - step: 3
      title: Install Python Dependencies
      commands:
        - pip install -r requirements.txt

    - step: 4
      title: Install Shelby CLI (Required)
      commands:
        - npm install -g @shelby-protocol/cli
        - shelby --version

usage:
  run:
    command: python bot.py
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
  root: shelby-simple-python
  files:
    - bot.py: Main Python CLI script
    - bot.js: Optional JavaScript integration
    - requirements.txt: Python dependency list
    - package.json: Node.js dependency list
    - pk.txt: Auto-generated private key file
    - README.md: Project documentation

configuration:
  optional_env:
    file: .env
    variables:
      SHELBY_BIN: "/path/to/shelby"
      APTOS_FAUCET_URL: "https://your-faucet-url"
      DEST_PREFIX_IMAGE: "images/"
      DEST_PREFIX_VIDEO: "videos/"

security:
  warnings:
    - Never commit pk.txt to the repository
    - Never share your private keys
    - Always use testnet wallets for testing
  gitignore_recommended:
    - pk.txt
    - .env

contribution:
  guidelines: >
    Contributions are welcome.
    Feel free to open an issue for bug reports or feature requests,
    or submit a pull request to improve the project.

license:
  status: Not specified
  recommendation:
    - MIT
    - Apache-2.0

support:
  message: >
    If this project helps you, please consider giving it a star ⭐ on GitHub.
