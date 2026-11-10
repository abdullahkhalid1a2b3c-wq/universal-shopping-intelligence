#!/usr/bin/env node
/**
 * Creates a zip archive of dist/ for Chrome Web Store distribution.
 * Uses Python's built-in zipfile module for reliable, cross-platform compression
 * without Windows PowerShell console buffer or external binary dependencies.
 */

import fs from 'node:fs'
import path from 'node:path'
import { execSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')
const distDir = path.join(rootDir, 'dist')
const outputDir = path.join(rootDir, 'dist-zip')
const zipPath = path.join(outputDir, 'fitsense-extension.zip')

if (!fs.existsSync(distDir)) {
  console.error('[FitSense] Error: dist/ directory does not exist. Run build first.')
  process.exit(1)
}

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true })
}

if (fs.existsSync(zipPath)) {
  fs.unlinkSync(zipPath)
}

console.log('[FitSense] Packaging dist/ into fitsense-extension.zip...')

try {
  const normDist = distDir.replace(/\\/g, '/')
  const normZip = zipPath.replace(/\\/g, '/')

  const pythonCmd = `python -c "import zipfile, os; z = zipfile.ZipFile('${normZip}', 'w', zipfile.ZIP_DEFLATED); [z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), '${normDist}')) for r, d, files in os.walk('${normDist}') for f in files]; z.close()"`

  execSync(pythonCmd, { stdio: 'inherit' })

  const stat = fs.statSync(zipPath)
  console.log(`[FitSense] ✓ Extension packaged successfully: ${zipPath} (${Math.round(stat.size / 1024)} KB)`)
} catch (err) {
  console.error('[FitSense] Failed to package extension:', err.message)
  process.exit(1)
}
