#!/usr/bin/env node

/**
 * Show Me The Money — installer
 *
 * Copies every skill in ./skills into the user's Claude Code skills
 * directory (~/.claude/skills/). Re-running performs an in-place update;
 * existing skill folders with the same name are replaced.
 *
 * Usage:
 *   node install.js              # install / update all skills
 *   node install.js uninstall    # remove all money-* skills
 *   npx @orrisai/show-me-the-money
 *   npx @orrisai/show-me-the-money uninstall
 */

const fs = require("fs");
const path = require("path");
const os = require("os");

const SOURCE_DIR = path.join(__dirname, "skills");
const TARGET_DIR = path.join(os.homedir(), ".claude", "skills");

function log(msg) {
  process.stdout.write(`${msg}\n`);
}

function listSkills() {
  if (!fs.existsSync(SOURCE_DIR)) {
    throw new Error(`No skills directory found at ${SOURCE_DIR}`);
  }
  return fs
    .readdirSync(SOURCE_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function install() {
  const skills = listSkills();
  fs.mkdirSync(TARGET_DIR, { recursive: true });

  log(`💰 Installing ${skills.length} skills to ${TARGET_DIR}`);
  for (const skill of skills) {
    const dest = path.join(TARGET_DIR, skill);
    fs.rmSync(dest, { recursive: true, force: true });
    copyDir(path.join(SOURCE_DIR, skill), dest);
    log(`   ✅ ${skill}`);
  }
  log("");
  log("Done. Open Claude Code (or Codex / Gemini CLI) and type /money to start.");
}

function uninstall() {
  const skills = listSkills();
  log(`🗑  Removing ${skills.length} skills from ${TARGET_DIR}`);
  let removed = 0;
  for (const skill of skills) {
    const dest = path.join(TARGET_DIR, skill);
    if (fs.existsSync(dest)) {
      fs.rmSync(dest, { recursive: true, force: true });
      log(`   ✅ removed ${skill}`);
      removed += 1;
    }
  }
  log("");
  log(`Done. Removed ${removed} skill(s).`);
}

function main() {
  const cmd = process.argv[2];
  try {
    if (cmd === "uninstall" || cmd === "remove") {
      uninstall();
    } else {
      install();
    }
  } catch (err) {
    process.stderr.write(`Error: ${err.message}\n`);
    process.exit(1);
  }
}

main();
