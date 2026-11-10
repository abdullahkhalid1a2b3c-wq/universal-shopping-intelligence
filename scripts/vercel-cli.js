import fs from 'node:fs'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')
const envVercelPath = path.join(rootDir, '.env.vercel')

let token = process.env.VERCEL_TOKEN

if (!token && fs.existsSync(envVercelPath)) {
  const content = fs.readFileSync(envVercelPath, 'utf8')
  for (const line of content.split('\n')) {
    const trimmed = line.trim()
    if (trimmed.startsWith('VERCEL_TOKEN=')) {
      token = trimmed.split('=')[1].replace(/^["']|["']$/g, '').trim()
      break
    }
  }
}

if (!token) {
  console.error('[vercel-cli] Error: VERCEL_TOKEN not found in environment or .env.vercel')
  process.exit(1)
}

const args = process.argv.slice(2)
const env = { ...process.env, VERCEL_TOKEN: token }

const res = spawnSync('npx', ['vercel', ...args, '--token', token], {
  cwd: rootDir,
  env,
  shell: true,
  stdio: 'inherit',
})

process.exit(res.status ?? 0)
