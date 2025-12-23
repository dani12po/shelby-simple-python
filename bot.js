#!/usr/bin/env node
/**
 * Shelby CLI Bot
 * - Wraps the official `shelby` CLI so you can automate common flows
 * - Requires: Node.js (>=18) and Shelby CLI installed/configured
 *
 * Docs: https://docs.shelby.xyz/tools/cli
 */
const fs = require("fs");
const os = require("os");
const path = require("path");
const process = require("process");

require("dotenv").config();

const { execa } = require("execa");
const chokidar = require("chokidar");
const yargs = require("yargs/yargs");
const { hideBin } = require("yargs/helpers");

const SHELBY_BIN = process.env.SHELBY_BIN || "shelby";
const CONFIG_PATH = process.env.SHELBY_CONFIG || path.join(os.homedir(), ".shelby", "config.yaml");

// Defaults you can set in .env
const DEFAULT_CONTEXT = process.env.DEFAULT_CONTEXT || "";
const DEFAULT_ACCOUNT = process.env.DEFAULT_ACCOUNT || "";
const DEFAULT_EXPIRATION = process.env.DEFAULT_EXPIRATION || "in 30 days";

function now() {
  return new Date().toISOString().replace("T", " ").replace("Z", "");
}

function log(msg) {
  process.stdout.write(`[${now()}] ${msg}\n`);
}

function die(msg, code = 1) {
  process.stderr.write(`\n[ERROR] ${msg}\n`);
  process.exit(code);
}

async function runShelby(args, opts = {}) {
  const {
    stdio = "inherit",
    dryRun = false,
    env = {},
  } = opts;

  // Allow user to pin default context/account via env or CLI flags
  const finalArgs = [];
  if (DEFAULT_CONTEXT && !args.includes("--context") && !args.includes("-c")) {
    // Most Shelby CLI commands support -c/--context in account balance;
    // for others, context/account is selected via `shelby context use` / `shelby account use`.
    // So we won't inject flags globally. We simply keep defaults in .env for our watch/sync commands.
  }
  if (DEFAULT_ACCOUNT && !args.includes("--account") && !args.includes("-a")) {
    // Same note as above.
  }

  if (dryRun) {
    log(`(dry-run) ${SHELBY_BIN} ${args.join(" ")}`);
    return { exitCode: 0 };
  }

  return execa(SHELBY_BIN, args, {
    stdio,
    env: { ...process.env, ...env },
  });
}

function assertConfigured() {
  if (!fs.existsSync(CONFIG_PATH)) {
    die(
      `Shelby config not found at:\n  ${CONFIG_PATH}\n\nRun this once first:\n  shelby init\n\n(That command creates ~/.shelby/config.yaml)`,
      2
    );
  }
}

async function doctor() {
  log("Checking Shelby CLI...");
  try {
    await runShelby(["--version"], { stdio: "pipe" });
    log("✅ Shelby CLI is installed.");
  } catch (e) {
    die(
      "Shelby CLI not found in PATH. Install it first:\n  npm i -g @shelby-protocol/cli",
      2
    );
  }

  log("Checking Shelby config...");
  if (fs.existsSync(CONFIG_PATH)) {
    log(`✅ Config found: ${CONFIG_PATH}`);
  } else {
    log(`⚠️  Config not found: ${CONFIG_PATH}`);
    log("   Run: shelby init");
  }

  log("Tip: Fund your account with APT + ShelbyUSD using: shelby faucet");
}

function ensureTrailingSlash(p) {
  return p.endsWith("/") ? p : (p + "/");
}

function isDir(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}

function toPosix(p) {
  // Shelby blob names use forward slashes
  return p.split(path.sep).join("/");
}

async function cmdUpload(argv) {
  assertConfigured();

  const src = argv.src;
  const dst = argv.dst;
  const expiration = argv.expiration || DEFAULT_EXPIRATION;

  if (!src || !dst) die("upload requires <src> and <dst>.", 2);

  const args = ["upload"];
  if (argv.recursive) args.push("--recursive");
  if (argv.yes) args.push("--assume-yes");
  if (argv.outputCommitments) args.push("--output-commitments", argv.outputCommitments);
  args.push(src, dst);
  args.push("--expiration", expiration);

  log(`Uploading: ${src} -> ${dst} (expiration: ${expiration})`);
  await runShelby(args, { dryRun: argv.dryRun });
}

async function cmdDownload(argv) {
  assertConfigured();

  const src = argv.src;
  const dst = argv.dst;
  if (!src || !dst) die("download requires <src> and <dst>.", 2);

  const args = ["download"];
  if (argv.recursive) args.push("--recursive");
  if (argv.force) args.push("--force");
  args.push(src, dst);

  log(`Downloading: ${src} -> ${dst}`);
  await runShelby(args, { dryRun: argv.dryRun });
}

async function cmdListBlobs(argv) {
  assertConfigured();
  const args = ["account", "blobs"];
  if (argv.account) args.push("--account", argv.account);
  log("Listing blobs…");
  await runShelby(args, { dryRun: argv.dryRun });
}

async function cmdBalance(argv) {
  assertConfigured();
  const args = ["account", "balance"];
  if (argv.account) args.push("--account", argv.account);
  if (argv.context) args.push("--context", argv.context);
  if (argv.address) args.push("--address", argv.address);
  log("Checking balance…");
  await runShelby(args, { dryRun: argv.dryRun });
}

async function cmdCommitment(argv) {
  const src = argv.src;
  const out = argv.out;
  if (!src || !out) die("commitment requires <src> and <out.json>.", 2);

  log(`Generating commitments: ${src} -> ${out}`);
  await runShelby(["commitment", src, out], { dryRun: argv.dryRun });
}

async function cmdContextUse(argv) {
  assertConfigured();
  if (!argv.name) die("context-use requires <name>.", 2);
  await runShelby(["context", "use", argv.name], { dryRun: argv.dryRun });
}

async function cmdAccountUse(argv) {
  assertConfigured();
  if (!argv.name) die("account-use requires <name>.", 2);
  await runShelby(["account", "use", argv.name], { dryRun: argv.dryRun });
}

async function cmdWatchUpload(argv) {
  assertConfigured();

  const dir = argv.dir;
  if (!dir) die("watch-upload requires --dir <folder>.", 2);

  const dstPrefixRaw = argv.dstPrefix;
  if (!dstPrefixRaw) die("watch-upload requires --dst-prefix <blob-prefix/>.", 2);

  const dstPrefix = ensureTrailingSlash(dstPrefixRaw);
  const expiration = argv.expiration || DEFAULT_EXPIRATION;

  if (!isDir(dir)) die(`--dir is not a directory: ${dir}`, 2);

  const ignoreInitial = argv.ignoreInitial ?? true;
  const yes = argv.yes ?? true;

  log("Starting watcher…");
  log(` Local dir : ${path.resolve(dir)}`);
  log(` Blob prefix: ${dstPrefix}`);
  log(` Expiration: ${expiration}`);
  log(` ignoreInitial: ${ignoreInitial}`);
  log(` assume-yes: ${yes}`);
  log("Press Ctrl+C to stop.");

  const pending = new Map(); // filepath -> timeoutId
  const debounceMs = Number(argv.debounceMs || 750);

  async function uploadFile(filepath) {
    const rel = path.relative(dir, filepath);
    if (rel.startsWith("..")) return;

    const dst = toPosix(path.posix.join(dstPrefix, toPosix(rel)));
    // Prevent directories
    try {
      if (fs.statSync(filepath).isDirectory()) return;
    } catch {
      return;
    }

    const args = ["upload"];
    if (yes) args.push("--assume-yes");
    args.push(filepath, dst, "--expiration", expiration);

    log(`↥ upload ${toPosix(rel)} -> ${dst}`);
    try {
      await runShelby(args, { dryRun: argv.dryRun });
      log(`✅ uploaded ${toPosix(rel)}`);
    } catch (e) {
      log(`❌ failed ${toPosix(rel)} (${e.exitCode ?? "unknown"})`);
    }
  }

  function scheduleUpload(filepath) {
    if (pending.has(filepath)) clearTimeout(pending.get(filepath));
    const tid = setTimeout(() => {
      pending.delete(filepath);
      uploadFile(filepath);
    }, debounceMs);
    pending.set(filepath, tid);
  }

  const watcher = chokidar.watch(dir, {
    ignoreInitial,
    persistent: true,
    awaitWriteFinish: {
      stabilityThreshold: 800,
      pollInterval: 100,
    },
  });

  watcher.on("add", scheduleUpload);
  watcher.on("change", scheduleUpload);
  watcher.on("error", (err) => log(`Watcher error: ${err.message || err}`));
}

yargs(hideBin(process.argv))
  .scriptName("shelby-bot")
  .usage("$0 <cmd> [args]")
  .command("doctor", "Check shelby CLI + config presence", () => {}, (argv) => doctor())
  .command(
    "upload <src> <dst>",
    "Upload a file or directory (use -r for directories).",
    (y) =>
      y
        .positional("src", { describe: "Local file/dir path", type: "string" })
        .positional("dst", { describe: "Shelby blob name (or prefix/ for -r)", type: "string" })
        .option("expiration", { alias: "e", describe: "Expiration time (e.g. \"2025-12-31\" or \"in 2 days\")", type: "string" })
        .option("recursive", { alias: "r", describe: "Upload a directory recursively", type: "boolean", default: false })
        .option("yes", { describe: "Skip interactive cost confirmation", type: "boolean", default: true })
        .option("outputCommitments", { describe: "Write commitments JSON to this file", type: "string" })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdUpload(argv)
  )
  .command(
    "download <src> <dst>",
    "Download a file or directory (use -r for prefixes).",
    (y) =>
      y
        .positional("src", { describe: "Shelby blob name (or prefix/ for -r)", type: "string" })
        .positional("dst", { describe: "Local output file path (or dir/ for -r)", type: "string" })
        .option("recursive", { alias: "r", describe: "Download a prefix (directory) recursively", type: "boolean", default: false })
        .option("force", { alias: "f", describe: "Overwrite existing destination", type: "boolean", default: false })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdDownload(argv)
  )
  .command(
    "list-blobs",
    "List stored blobs for an account",
    (y) =>
      y
        .option("account", { alias: "a", describe: "Account name override", type: "string" })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdListBlobs(argv)
  )
  .command(
    "balance",
    "Show APT + ShelbyUSD balance",
    (y) =>
      y
        .option("account", { alias: "a", describe: "Account name override", type: "string" })
        .option("context", { alias: "c", describe: "Context name override", type: "string" })
        .option("address", { describe: "Raw Aptos address (0x…)", type: "string" })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdBalance(argv)
  )
  .command(
    "commitment <src> <out>",
    "Generate commitments for a local file (offline, no upload).",
    (y) =>
      y
        .positional("src", { describe: "Local file path", type: "string" })
        .positional("out", { describe: "Output JSON file path", type: "string" })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdCommitment(argv)
  )
  .command(
    "context-use <name>",
    "Switch default Shelby context",
    (y) =>
      y
        .positional("name", { describe: "Context name", type: "string" })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdContextUse(argv)
  )
  .command(
    "account-use <name>",
    "Switch default Shelby account",
    (y) =>
      y
        .positional("name", { describe: "Account name", type: "string" })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdAccountUse(argv)
  )
  .command(
    "watch-upload",
    "Watch a local folder and upload changed files automatically.",
    (y) =>
      y
        .option("dir", { describe: "Folder to watch", type: "string", demandOption: true })
        .option("dst-prefix", { describe: "Blob prefix ending with '/' (e.g. backups/site/)", type: "string", demandOption: true })
        .option("expiration", { alias: "e", describe: "Expiration (default from .env)", type: "string" })
        .option("debounce-ms", { describe: "Debounce interval for rapid file writes", type: "number", default: 750 })
        .option("ignore-initial", { describe: "Do not upload existing files at start", type: "boolean", default: true })
        .option("yes", { describe: "Use --assume-yes for uploads", type: "boolean", default: true })
        .option("dryRun", { describe: "Print commands without executing", type: "boolean", default: false }),
    (argv) => cmdWatchUpload(argv)
  )
  .demandCommand(1, "Pick a command. Try: doctor")
  .help()
  .wrap(Math.min(120, process.stdout.columns || 120))
  .parseAsync()
  .catch((err) => die(err?.message || String(err), 1));
