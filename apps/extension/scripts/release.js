#!/usr/bin/env node
/**
 * FitSense Chrome Extension Production Release Script
 * 1. Builds production extension with Vite
 * 2. Verifies manifest.json permissions strictly match supported-domains list
 * 3. Scans dist/ for accidental secrets
 * 4. Packages dist/ into dist-zip/fitsense-extension.zip
 */

import fs from 'node:fs'
import path from 'node:path'
import { execSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const extDir = path.resolve(__dirname, '..')
const rootDir = path.resolve(extDir, '..', '..')
const distDir = path.join(extDir, 'dist')
const manifestDistPath = path.join(distDir, 'manifest.json')
const domainsTsPath = path.join(extDir, 'src', 'constants', 'domains.ts')

console.log('====================================================')
console.log('🚀 FitSense Chrome Extension Release Pipeline')
console.log('====================================================')

// 1. Build Extension
console.log('\n[Step 1/4] Building production extension bundle...')
try {
  execSync('npm run build', { cwd: extDir, stdio: 'inherit' })
} catch (err) {
  console.error('[FitSense Release] ❌ Vite build failed.')
  process.exit(1)
}

// 2. Verify Manifest Permissions Match Supported Domains
console.log('\n[Step 2/4] Verifying manifest permissions against supported domains...')
if (!fs.existsSync(manifestDistPath)) {
  console.error('[FitSense Release] ❌ dist/manifest.json not found.')
  process.exit(1)
}

const manifest = JSON.parse(fs.readFileSync(manifestDistPath, 'utf-8'))
const domainsContent = fs.readFileSync(domainsTsPath, 'utf-8')

// Extract matchPatterns from domains.ts
const matchPatternRegex = /matchPattern:\s*['"]([^'"]+)['"]/g
const expectedPatterns = []
let match
while ((match = matchPatternRegex.exec(domainsContent)) !== null) {
  expectedPatterns.push(match[1])
}

const actualHostPermissions = manifest.host_permissions || []
const permissions = manifest.permissions || []

console.log(`- Expected Host Patterns (${expectedPatterns.length}):`, expectedPatterns)
console.log(`- Actual Host Permissions (${actualHostPermissions.length}):`, actualHostPermissions)
console.log(`- Base Permissions:`, permissions)

// Check base permissions - only storage allowed
if (permissions.length !== 1 || permissions[0] !== 'storage') {
  console.error(`[FitSense Release] ❌ Manifest permissions violation! Expected only ['storage'], found:`, permissions)
  process.exit(1)
}

// Check host permissions
const missing = expectedPatterns.filter((p) => !actualHostPermissions.includes(p))
const extra = actualHostPermissions.filter((p) => !expectedPatterns.includes(p))

if (missing.length > 0 || extra.length > 0) {
  if (missing.length > 0) console.error('[FitSense Release] ❌ Missing host permissions:', missing)
  if (extra.length > 0) console.error('[FitSense Release] ❌ Unauthorized extra host permissions:', extra)
  process.exit(1)
}
console.log('[FitSense Release] ✓ Manifest permissions strictly match supported domains.')

// 3. Scan for Secrets
console.log('\n[Step 3/4] Scanning built bundle for credential leaks...')
try {
  execSync('node scripts/scan-secrets.js', { cwd: extDir, stdio: 'inherit' })
} catch (err) {
  console.error('[FitSense Release] ❌ Secret scanning detected leaks.')
  process.exit(1)
}

// 4. Produce Zip Archive
console.log('\n[Step 4/4] Producing fitsense-extension.zip archive...')
try {
  execSync('node scripts/zip-extension.js', { cwd: extDir, stdio: 'inherit' })
} catch (err) {
  console.error('[FitSense Release] ❌ Zip archiving failed.')
  process.exit(1)
}

console.log('\n====================================================')
console.log('✅ Extension Release Ready for Chrome Web Store!')
console.log(`Archive: ${path.join(extDir, 'dist-zip', 'fitsense-extension.zip')}`)
console.log('====================================================')

