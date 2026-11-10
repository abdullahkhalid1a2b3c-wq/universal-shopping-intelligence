#!/usr/bin/env node
/**
 * Security audit script: scans built artifacts across apps/web and apps/extension
 * to prevent accidental bundling of service role keys, DB passwords, or AI credentials.
 */

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')

const targetDirs = [
  path.join(rootDir, 'apps', 'extension', 'dist'),
  path.join(rootDir, 'apps', 'web', '.output', 'public'),
]

const FORBIDDEN_PATTERNS = [
  { name: 'Supabase Service Role Key', regex: /eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/ },
  { name: 'PostgreSQL Database URL', regex: /postgres(ql)?:\/\/[a-zA-Z0-9_.-]+:[^@\s]+@/i },
  { name: 'Private AI API Key', regex: /(sk-[a-zA-Z0-9]{20,}|mistral_[a-zA-Z0-9]{20,})/i },
  { name: 'Supabase Secret Prefix', regex: /sb_secret_[a-zA-Z0-9_-]{20,}/i },
]

function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8')
  const violations = []

  for (const rule of FORBIDDEN_PATTERNS) {
    if (rule.name === 'Supabase Service Role Key') {
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
        } catch {}
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
  if (!fs.existsSync(dir)) return []
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

console.log('[FitSense Security] Running bundle secret scanning audit...')
let totalFilesScanned = 0
let totalViolations = 0

for (const dir of targetDirs) {
  if (!fs.existsSync(dir)) {
    console.log(`[FitSense Security] Target dir not yet built (skipped): ${path.relative(rootDir, dir)}`)
    continue
  }

  const files = walkDir(dir)
  totalFilesScanned += files.length
  for (const file of files) {
    const relative = path.relative(rootDir, file)
    const violations = scanFile(file)
    if (violations.length > 0) {
      console.error(`[FitSense Security] ❌ SECRET LEAK in ${relative}:`)
      for (const v of violations) {
        console.error(`   - ${v.rule} (${v.match})`)
        totalViolations++
      }
    }
  }
}

console.log(`[FitSense Security] Scanned ${totalFilesScanned} built files.`)
if (totalViolations > 0) {
  console.error(`[FitSense Security] ❌ AUDIT FAILED: ${totalViolations} secret leaks found!`)
  process.exit(1)
} else {
  console.log('[FitSense Security] ✓ AUDIT PASSED: 0 secrets or service_role tokens found.')
  process.exit(0)
}

