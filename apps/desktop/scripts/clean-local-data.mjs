#!/usr/bin/env node
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const isWindows = process.platform === 'win32'
const isMac = process.platform === 'darwin'
const __dirname = path.dirname(fileURLToPath(import.meta.url))
const desktopRoot = path.resolve(__dirname, '..')

const cleanBuild = process.argv.includes('--all') || process.argv.includes('--build')

function getHermesHome() {
  if (process.env.HERMES_HOME) {
    return path.resolve(process.env.HERMES_HOME)
  }
  if (isWindows) {
    const localAppData = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local')
    return path.join(localAppData, 'hermes')
  }
  return path.join(os.homedir(), '.hermes')
}

function getUserDataDirs() {
  const dirs = []
  if (isMac) {
    const appSupport = path.join(os.homedir(), 'Library', 'Application Support')
    dirs.push(path.join(appSupport, 'Hermes'), path.join(appSupport, 'Gideon'))
  } else if (isWindows) {
    const appData = process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming')
    dirs.push(path.join(appData, 'Hermes'), path.join(appData, 'Gideon'))
  } else {
    const config = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config')
    dirs.push(path.join(config, 'Hermes'), path.join(config, 'Gideon'))
  }
  return dirs
}

function safeRemove(targetPath) {
  if (!fs.existsSync(targetPath)) return
  try {
    fs.rmSync(targetPath, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 })
  } catch {
    // If rmdir fails on macOS due to .DS_Store or open lock, clean children
    try {
      if (fs.statSync(targetPath).isDirectory()) {
        const items = fs.readdirSync(targetPath)
        for (const item of items) {
          fs.rmSync(path.join(targetPath, item), { recursive: true, force: true, maxRetries: 3, retryDelay: 100 })
        }
      }
    } catch {
      // ignore
    }
  }
}

console.log('🧹 Cleaning desktop local data...')

// 1. Clean Electron UserData dirs
for (const dir of getUserDataDirs()) {
  if (fs.existsSync(dir)) {
    console.log(`  - Removing Electron user data: ${dir}`)
    safeRemove(dir)
  }
}

// 2. Clean Hermes Home (preserving .env so API keys are not lost)
const hermesHome = getHermesHome()
if (fs.existsSync(hermesHome)) {
  const envPath = path.join(hermesHome, '.env')
  let envBackup = null
  if (fs.existsSync(envPath)) {
    try {
      envBackup = fs.readFileSync(envPath, 'utf8')
      console.log('  - Backed up .env (API keys preserved)')
    } catch {
      // ignore
    }
  }

  console.log(`  - Removing Hermes home data: ${hermesHome}`)
  safeRemove(hermesHome)
  fs.mkdirSync(hermesHome, { recursive: true })
  if (envBackup) {
    fs.writeFileSync(envPath, envBackup, { encoding: 'utf8', mode: 0o600 })
    console.log('  - Restored .env to fresh Hermes home')
  }
}

// 3. Clean build caches if --all or --build passed
if (cleanBuild) {
  const buildDirs = [
    path.join(desktopRoot, 'dist'),
    path.join(desktopRoot, 'release'),
    path.join(desktopRoot, 'node_modules', '.vite')
  ]
  for (const dir of buildDirs) {
    if (fs.existsSync(dir)) {
      console.log(`  - Removing build cache: ${path.relative(desktopRoot, dir)}`)
      safeRemove(dir)
    }
  }
}

console.log('✨ Done! Local data cleared. Ready for a fresh start.')
