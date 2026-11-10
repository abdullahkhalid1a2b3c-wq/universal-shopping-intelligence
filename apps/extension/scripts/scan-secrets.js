#!/usr/bin/env node
/**
 * Secret scanner for FitSense Chrome Extension build output.
 * Scans dist/ directory to ensure no secret keys, service role credentials,
 * database passwords, or private API keys were bundled into the extension.
 */

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const distDir = path.resolve(__dirname, '..', 'dist')

if (!fs.existsSync(distDir)) {
  console.error('[FitSense Security] Error: dist/ directory does not exist. Run build first.')
  process.exit(1)
}

const FORBIDDEN_PATTERNS = [
  { name: 'Supabase Secret Key', regex: /sb_secret_[a-zA-Z0-9_-]{20,}/i },
  { name: 'Service Role Token', regex: /eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/ }, // Will check for service_role inside JWT
  { name: 'PostgreSQL Database URL', regex: /postgres(ql)?:\/\/[a-zA-Z0-9_.-]+:[^@\s]+@/i },
  { name: 'Private AI API Key', regex: /(sk-[a-zA-Z0-9]{20,}|mistral_[a-zA-Z0-9]{20,})/i },
]

function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8')
  const violations = []

  for (const rule of FORBIDDEN_PATTERNS) {
    if (rule.name === 'Service Role Token') {
      // Decode JWT tokens found to verify none have service_role claim
      const matches = content.match(new RegExp(rule.regex, 'g')) || []
      for (const token of matches) {
        try {
          const parts = token.split('.')
          if (parts.length >= 2) {
            const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString('utf-8'))
            if (payload.role === 'service_role') {
              violations.push({ rule: 'Supabase service_role JWT in bundle', match: `${token.slice(0, 10)}...` })
            }
          }
        } catch {
          // Not a base64 JWT payload, skip
        }
      }
    } else {
      const match = content.match(rule.regex)
      if (match) {
        violations.push({ rule: rule.name, match: `${match[0].slice(0, 10)}...[REDACTED]` })
      }
    }
  }

  return violations
}

function walkDir(dir) {
  let allFiles = []
  const list = fs.readdirSync(dir)
  for (const item of list) {
    const fullPath = path.join(dir, item)
    const stat = fs.statSync(fullPath)
    if (stat.isDirectory()) {
      allFiles = allFiles.concat(walkDir(fullPath))
    } else if (/\.(js|html|css|json)$/i.test(item)) {
      allFiles.push(fullPath)
    }
  }
  return allFiles
}

const files = walkDir(distDir)
let totalViolations = 0

console.log(`[FitSense Security] Scanning ${files.length} built files in dist/ for credential leaks...`)

for (const file of files) {
  const relative = path.relative(distDir, file)
  const violations = scanFile(file)
  if (violations.length > 0) {
    console.error(`[FitSense Security] ❌ SECRET LEAK DETECTED in ${relative}:`)
    for (const v of violations) {
      console.error(`   - ${v.rule} (${v.match})`)
      totalViolations++
    }
  }
}

if (totalViolations > 0) {
  console.error(`[FitSense Security] BUILD FAILED: ${totalViolations} secret credential patterns detected in dist.`)
  process.exit(1)
} else {
  console.log(`[FitSense Security] ✓ Scan passed: 0 secret credentials found. Bundle is safe for Chrome Web Store.`)
  process.exit(0)
}
