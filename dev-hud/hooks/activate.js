// dev-hud — SessionStart activator.
//
// Claude Code plugins can't declare a `statusLine` directly in plugin.json —
// the field lives in the user's settings.json. This hook checks whether
// settings.json already has a `statusLine` pointing at our script. If not,
// it emits a system-reminder nudging Claude to offer setup.
//
// Mirrors the pattern caveman uses (cf. caveman/hooks/caveman-activate.js).

const fs = require('fs');
const path = require('path');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(require('os').homedir(), '.claude');
const settingsPath = path.join(claudeDir, 'settings.json');
const scriptPath = path.join(__dirname, 'statusline.sh');
const command = `bash "${scriptPath}"`;

let needsSetup = false;
try {
  if (fs.existsSync(settingsPath)) {
    const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    const current = settings.statusLine && settings.statusLine.command;
    // If statusLine is already pointing at any dev-hud install (cached plugin
    // path, local dev path, prior `statusline-context` name) leave it alone.
    const ours = current && (current.includes('dev-hud') || current.includes('statusline-context'));
    if (!current) needsSetup = true;
    else if (!ours) {
      // Already set to something else — respect the user's choice.
    }
  } else {
    needsSetup = true;
  }
} catch (_) {
  // Settings unreadable. Don't block session start.
}

if (needsSetup) {
  const snippet = '"statusLine": { "type": "command", "command": ' + JSON.stringify(command) + ' }';
  const msg =
    'DEV-HUD SETUP NEEDED: The dev-hud plugin renders an always-visible ' +
    'HUD with the current Linear ticket, PR number, worktree, and branch state. ' +
    'It is not wired yet. To enable, add this entry to ' + settingsPath + ': ' +
    snippet + ' ' +
    'Proactively offer to set this up for the user on first interaction. ' +
    'Optional: also create ' + path.join(claudeDir, 'linear-token') +
    ' (chmod 600) containing a Linear personal API token to enable Linear titles.';
  process.stdout.write(msg);
}
