import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { Window } from 'happy-dom'
import { renderWidget, removeWidget, highlightSizeButton } from '../src/content/widget.ts'

describe('Floating Shadow DOM Widget', () => {
  it('renders recommendation widget with confidence badge, explanation and warnings', () => {
    const window = new Window()
    globalThis.document = window.document as unknown as Document
    globalThis.HTMLElement = window.HTMLElement as unknown as typeof HTMLElement

    const host = renderWidget({
      covered: true,
      recommendation: {
        recommendedSize: 'M',
        confidenceScore: 0.85,
        confidenceLabel: 'high',
        explanation: 'Fits well in the chest with relaxed waist allowance.',
        isDemo: true,
        isUnverified: true,
      },
      productUrl: 'https://outfitters.com.pk/products/tee',
      domain: 'outfitters.com.pk',
      language: 'en',
    })

    assert.ok(host)
    assert.equal(host.id, 'fitsense-widget-root')

    const shadow = host.shadowRoot
    assert.ok(shadow)

    const recSize = shadow.querySelector('.rec-size')
    assert.equal(recSize?.textContent, 'M')

    const badge = shadow.querySelector('.confidence-badge')
    assert.ok(badge?.classList.contains('confidence-high'))
    assert.ok(badge?.textContent?.includes('high confidence'))

    const explanation = shadow.querySelector('.explanation-text')
    assert.equal(explanation?.textContent, 'Fits well in the chest with relaxed waist allowance.')

    const demoTag = shadow.querySelector('.warning-demo')
    assert.ok(demoTag)

    const unverifiedTag = shadow.querySelector('.warning-unverified')
    assert.ok(unverifiedTag)
  })

  it('renders uncovered product state with request coverage button', async () => {
    const window = new Window()
    globalThis.document = window.document as unknown as Document
    globalThis.HTMLElement = window.HTMLElement as unknown as typeof HTMLElement

    let requested = false
    const host = renderWidget({
      covered: false,
      productUrl: 'https://sapphireonline.pk/products/uncovered',
      domain: 'sapphireonline.pk',
      language: 'en',
      onRequestCoverage: async () => {
        requested = true
        return true
      },
    })

    const shadow = host.shadowRoot
    assert.ok(shadow)

    const title = shadow.querySelector('.uncovered-title')
    assert.equal(title?.textContent, 'Size chart not available yet')

    const btn = shadow.querySelector('.coverage-btn') as HTMLButtonElement
    assert.ok(btn)
    assert.equal(btn.textContent?.trim(), 'Request Brand Coverage')

    btn.click()
    // Give async event handler a tick
    await new Promise((r) => setTimeout(r, 10))
    assert.equal(requested, true)
  })

  it('highlights recommended size button without throwing', () => {
    const window = new Window()
    globalThis.document = window.document as unknown as Document

    window.document.body.innerHTML = `
      <div class="size-swatch">
        <button>S</button>
        <button>M</button>
        <button>L</button>
      </div>
    `

    highlightSizeButton('M', '.size-swatch button')

    const buttons = window.document.querySelectorAll('.size-swatch button')
    const mBtn = buttons[1] as HTMLElement
    assert.equal(mBtn.getAttribute('data-fitsense-recommended'), 'true')
  })

  it('renders feedback prompt link when previously recommended', () => {
    const window = new Window()
    globalThis.document = window.document as unknown as Document
    globalThis.HTMLElement = window.HTMLElement as unknown as typeof HTMLElement

    const host = renderWidget({
      covered: true,
      productId: 'prod-uuid-123',
      hasPreviousRecommendation: true,
      recommendation: {
        recommendedSize: 'L',
        confidenceScore: 0.9,
        confidenceLabel: 'high',
        explanation: 'Matches your measurements well.',
      },
      productUrl: 'https://outfitters.com.pk/products/tee',
      domain: 'outfitters.com.pk',
      language: 'en',
    })

    const shadow = host.shadowRoot
    assert.ok(shadow)
    const fbLink = shadow.querySelector('.feedback-link') as HTMLAnchorElement
    assert.ok(fbLink)
    assert.ok(fbLink.textContent?.includes('Bought this? Tell us how it fits'))
    assert.ok(fbLink.getAttribute('href')?.includes('/feedback/prod-uuid-123'))
  })
})
