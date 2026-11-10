/**
 * FitSense floating widget mounted in an isolated Shadow DOM.
 *
 * Ensures:
 * - Complete style isolation: retailer CSS never leaks in; widget styles never affect the retailer page.
 * - Does not block or alter Add-to-Cart or checkout buttons.
 * - Highlights the recommended size button when available, failing silently if not found.
 */

export interface WidgetRecommendationData {
  recommendedSize: string
  confidenceScore: number
  confidenceLabel: 'high' | 'moderate' | 'low'
  explanation: string
  isDemo?: boolean
  isUnverified?: boolean
  details?: {
    chestDiff?: number
    waistDiff?: number
    hipDiff?: number
    fitPreference?: string
  }
}

export interface WidgetConfig {
  covered: boolean
  recommendation?: WidgetRecommendationData
  productUrl: string
  domain: string
  language?: string
  productId?: string
  hasPreviousRecommendation?: boolean
  feedbackUrl?: string
  onRequestCoverage?: () => Promise<boolean>
}

const WIDGET_HOST_ID = 'fitsense-widget-root'

export function removeWidget(): void {
  const existing = document.getElementById(WIDGET_HOST_ID)
  if (existing) {
    existing.remove()
  }
}

export function renderWidget(config: WidgetConfig): HTMLElement {
  removeWidget()

  const host = document.createElement('div')
  host.id = WIDGET_HOST_ID
  document.body.appendChild(host)

  const shadow = host.attachShadow({ mode: 'open' })

  const isRtl = config.language === 'ur'

  // Style sheet
  const style = document.createElement('style')
  style.textContent = `
    :host {
      all: initial;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      position: fixed;
      bottom: 24px;
      right: ${isRtl ? 'auto' : '24px'};
      left: ${isRtl ? '24px' : 'auto'};
      z-index: 2147483647;
      direction: ${isRtl ? 'rtl' : 'ltr'};
      color: #1e293b;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    .fitsense-card {
      width: 320px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
      overflow: hidden;
      transition: all 0.2s ease-in-out;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
    }

    .brand-title {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.5px;
      color: #4f46e5;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .close-btn {
      background: none;
      border: none;
      cursor: pointer;
      color: #94a3b8;
      font-size: 16px;
      line-height: 1;
      padding: 4px;
    }
    .close-btn:hover {
      color: #475569;
    }

    .card-body {
      padding: 16px;
    }

    /* Covered State */
    .rec-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 10px;
    }

    .rec-label {
      font-size: 13px;
      color: #64748b;
      font-weight: 500;
    }

    .rec-size {
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
    }

    .confidence-badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 600;
      text-transform: capitalize;
    }
    .confidence-high {
      background: #ecfdf5;
      color: #065f46;
      border: 1px solid #a7f3d0;
    }
    .confidence-moderate {
      background: #fffbeb;
      color: #92400e;
      border: 1px solid #fde68a;
    }
    .confidence-low {
      background: #f8fafc;
      color: #64748b;
      border: 1px solid #cbd5e1;
    }

    .explanation-text {
      font-size: 13px;
      line-height: 1.5;
      color: #334155;
      margin-bottom: 12px;
    }

    .warning-tag {
      display: block;
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 11px;
      margin-bottom: 10px;
      font-weight: 500;
    }
    .warning-demo {
      background: #eff6ff;
      color: #1e40af;
      border: 1px solid #bfdbfe;
    }
    .warning-unverified {
      background: #fffbeb;
      color: #b45309;
      border: 1px solid #fde68a;
    }

    .see-why-toggle {
      background: none;
      border: none;
      color: #4f46e5;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 2px 0;
    }
    .see-why-toggle:hover {
      text-decoration: underline;
    }

    .details-drawer {
      margin-top: 10px;
      padding: 10px;
      background: #f8fafc;
      border-radius: 8px;
      font-size: 12px;
      color: #475569;
      line-height: 1.4;
      display: none;
    }
    .details-drawer.open {
      display: block;
    }

    /* Uncovered State */
    .uncovered-box {
      text-align: center;
      padding: 8px 0;
    }
    .uncovered-title {
      font-size: 14px;
      font-weight: 600;
      color: #334155;
      margin-bottom: 6px;
    }
    .uncovered-desc {
      font-size: 12px;
      color: #64748b;
      margin-bottom: 14px;
      line-height: 1.4;
    }
    .coverage-btn {
      width: 100%;
      background: #4f46e5;
      color: #ffffff;
      border: none;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s ease;
    }
    .coverage-btn:hover {
      background: #4338ca;
    }
    .coverage-btn.done {
      background: #10b981;
      cursor: default;
    }

    .feedback-link {
      display: block;
      margin-top: 10px;
      padding-top: 8px;
      border-top: 1px dashed #e2e8f0;
      font-size: 11px;
      font-weight: 600;
      color: #4f46e5;
      text-decoration: none;
    }
    .feedback-link:hover {
      text-decoration: underline;
    }
  `

  const container = document.createElement('div')
  container.className = 'fitsense-card'

  // Header
  const header = document.createElement('div')
  header.className = 'card-header'
  header.innerHTML = `
    <span class="brand-title">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20.38 3.46L16 2a4 4 0 01-8 0L3.62 3.46a2 2 0 00-1.34 2.23l.58 3.47a1 1 0 00.99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 002-2V10h2.15a1 1 0 00.99-.84l.58-3.47a2 2 0 00-1.34-2.23z"/>
      </svg>
      FitSense
    </span>
    <button class="close-btn" title="Close">✕</button>
  `
  header.querySelector('.close-btn')?.addEventListener('click', () => {
    removeWidget()
  })

  // Body
  const body = document.createElement('div')
  body.className = 'card-body'

  if (config.covered && config.recommendation) {
    const rec = config.recommendation
    const confClass = `confidence-${rec.confidenceLabel || 'moderate'}`

    let warningsHtml = ''
    if (rec.isDemo) {
      warningsHtml += `<div class="warning-tag warning-demo">🧪 Demo Data — For evaluation only</div>`
    }
    if (rec.isUnverified) {
      warningsHtml += `<div class="warning-tag warning-unverified">⚠️ Unverified size chart</div>`
    }

    let feedbackPromptHtml = ''
    if (config.hasPreviousRecommendation || config.productId) {
      const fbUrl = config.feedbackUrl || (config.productId ? `http://localhost:3000/feedback/${config.productId}` : 'http://localhost:3000/saved')
      const fbText = isRtl
        ? 'کیا آپ نے یہ خریدا ہے؟ ہمیں بتائیں کہ کیسا آیا &larr;'
        : (config.language === 'ur-roman'
          ? 'Bought this? Tell us how it fits &rarr;'
          : 'Bought this? Tell us how it fits &rarr;')
      feedbackPromptHtml = `<a href="${fbUrl}" target="_blank" rel="noopener noreferrer" class="feedback-link">${fbText}</a>`
    }

    body.innerHTML = `
      <div class="rec-row">
        <div>
          <div class="rec-label">${isRtl ? 'تجویز کردہ سائز' : 'Recommended Size'}</div>
          <div class="rec-size">${rec.recommendedSize}</div>
        </div>
        <span class="confidence-badge ${confClass}">
          ${rec.confidenceLabel} confidence
        </span>
      </div>
      <div class="explanation-text">${rec.explanation}</div>
      ${warningsHtml}
      <button class="see-why-toggle">
        ${isRtl ? 'تفصیلات دیکھیں ▾' : 'See why ▾'}
      </button>
      <div class="details-drawer">
        <strong>Fit Analysis:</strong><br>
        Confidence Score: ${Math.round(rec.confidenceScore * 100)}%<br>
        ${rec.details?.fitPreference ? `Preference: ${rec.details.fitPreference}<br>` : ''}
        Garment measurements matched against your body profile.
      </div>
      ${feedbackPromptHtml}
    `

    const toggleBtn = body.querySelector('.see-why-toggle')
    const drawer = body.querySelector('.details-drawer')
    toggleBtn?.addEventListener('click', () => {
      drawer?.classList.toggle('open')
      const isOpen = drawer?.classList.contains('open')
      toggleBtn.textContent = isOpen
        ? (isRtl ? 'تفصیلات چھپائیں ▴' : 'Hide details ▴')
        : (isRtl ? 'تفصیلات دیکھیں ▾' : 'See why ▾')
    })
  } else {
    // Uncovered product state
    body.innerHTML = `
      <div class="uncovered-box">
        <div class="uncovered-title">${isRtl ? 'سائز چارٹ دستیاب نہیں ہے' : 'Size chart not available yet'}</div>
        <div class="uncovered-desc">
          ${isRtl ? 'ہم ابھی اس برانڈ کا احاطہ کر رہے ہیں۔ سپورٹ کی درخواست کے لیے کلک کریں۔' : 'We are adding size coverage for this brand. Click to request automatic chart matching.'}
        </div>
        <button class="coverage-btn">
          ${isRtl ? 'سائز کی درخواست کریں' : 'Request Brand Coverage'}
        </button>
      </div>
    `

    const covBtn = body.querySelector('.coverage-btn') as HTMLButtonElement | null
    covBtn?.addEventListener('click', async () => {
      covBtn.disabled = true
      covBtn.textContent = isRtl ? 'درخواست بھیجی جا رہی ہے...' : 'Submitting request...'
      try {
        if (config.onRequestCoverage) {
          await config.onRequestCoverage()
        }
        covBtn.classList.add('done')
        covBtn.textContent = isRtl ? '✓ درخواست جمع کر دی گئی' : '✓ Requested! We\'ll notify you.'
      } catch {
        covBtn.disabled = false
        covBtn.textContent = isRtl ? 'دوبارہ کوشش کریں' : 'Failed. Try again'
      }
    })
  }

  container.appendChild(header)
  container.appendChild(body)
  shadow.appendChild(style)
  shadow.appendChild(container)

  return host
}

/**
 * Highlights the recommended size button on the host page.
 * Uses adapter selector if available, or common button selectors.
 * Fails silently if no matching button is found.
 * Never alters or blocks Add-to-Cart.
 */
export function highlightSizeButton(
  recommendedSize: string,
  adapterSizeSelector?: string
): void {
  if (!recommendedSize) return

  try {
    const selector = adapterSizeSelector || '.size-swatch button, .variant-input input, .variant-input label, [data-option-name*="Size"] button, [data-option-type="size"]'
    const buttons = document.querySelectorAll(selector)

    for (const btn of Array.from(buttons)) {
      const text = btn.textContent?.trim().toLowerCase() || (btn as HTMLInputElement).value?.trim().toLowerCase()
      if (text === recommendedSize.toLowerCase()) {
        const target = btn as HTMLElement
        target.style.outline = '2px solid #6366f1'
        target.style.outlineOffset = '2px'
        target.style.boxShadow = '0 0 10px rgba(99, 102, 241, 0.4)'
        target.setAttribute('data-fitsense-recommended', 'true')
        break
      }
    }
  } catch {
    // Fail silently without disrupting page behavior
  }
}
