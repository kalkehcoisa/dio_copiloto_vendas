<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const API = 'http://localhost:8000'

const presets = ref({})
const selectedPreset = ref(null)
const message = ref('')
const context = reactive({ product: '', persona: 'indeciso', budget: '', objection: '', mode: 'padrao' })
const result = ref(null)
const loading = ref(false)
const error = ref('')
const tokensUsed = ref(null)

const personas = [
  { value: 'cauteloso', label: 'Cauteloso' },
  { value: 'entusiasta', label: 'Entusiasta' },
  { value: 'pai_comprando_para_filho', label: 'Pai comprando para filho' },
  { value: 'gamer_pro', label: 'Gamer Pro' },
  { value: 'primeiro_pc', label: 'Primeiro PC' },
  { value: 'orcamento_apertado', label: 'Orçamento apertado' },
  { value: 'indeciso', label: 'Indeciso' },
  { value: 'comparador', label: 'Comparador' },
]

const modes = [
  { value: 'padrao', label: 'Padrão (análise completa)' },
  { value: 'objecao', label: 'Quebrar Objeção' },
  { value: 'pitch_rapido', label: 'Pitch Rápido' },
  { value: 'followup', label: 'Follow-up' },
  { value: 'fechamento', label: 'Fechamento' },
]

const opportunityColor = computed(() => {
  const d = result.value?.diagnostico_oportunidade || ''
  if (d.startsWith('ALTA')) return '#22c55e'
  if (d.startsWith('MÉDIA')) return '#f59e0b'
  if (d.startsWith('BAIXA')) return '#ef4444'
  return '#6b7280'
})

onMounted(async () => {
  const res = await fetch(`${API}/presets`)
  presets.value = await res.json()
})

function applyPreset(key) {
  const p = presets.value[key]
  if (!p) return
  selectedPreset.value = key
  const c = p.default_context
  context.product = c.product || ''
  context.persona = c.persona || 'indeciso'
  context.budget = c.budget || ''
  context.objection = c.objection || ''
  context.mode = c.mode || 'padrao'
  message.value = ''
  result.value = null
  error.value = ''
}

async function send() {
  if (!message.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  tokensUsed.value = null

  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message.value,
        context: {
          product: context.product,
          persona: context.persona,
          budget: context.budget ? Number(context.budget) : undefined,
          objection: context.objection || undefined,
          mode: context.mode,
        }
      })
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.detail || 'Erro desconhecido')
    result.value = json.data
    tokensUsed.value = json.tokens_used
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app">
    <header>
      <div class="header-inner">
        <div class="logo">
          <span class="logo-icon">🎮</span>
          <span class="logo-text">VEGA <small>Copiloto de Vendas</small></span>
        </div>
        <span v-if="tokensUsed" class="token-badge">{{ tokensUsed }} tokens</span>
      </div>
    </header>

    <main>
      <section class="presets-section">
        <h2>Prompts Prontos</h2>
        <div class="presets-grid">
          <button
            v-for="(p, key) in presets"
            :key="key"
            class="preset-btn"
            :class="{ active: selectedPreset === key }"
            @click="applyPreset(key)"
          >
            <span class="preset-label">{{ p.label }}</span>
            <span class="preset-desc">{{ p.description }}</span>
          </button>
        </div>
      </section>

      <div class="workspace">
        <section class="form-section">
          <h2>Contexto do Atendimento</h2>

          <label>Produto em foco
            <input v-model="context.product" placeholder="ex: Notebook Gamer RTX 4060" />
          </label>

          <label>Perfil do cliente
            <select v-model="context.persona">
              <option v-for="p in personas" :key="p.value" :value="p.value">{{ p.label }}</option>
            </select>
          </label>

          <label>Orçamento estimado (R$)
            <input v-model="context.budget" type="number" placeholder="ex: 4500" />
          </label>

          <label>Modo de análise
            <select v-model="context.mode">
              <option v-for="m in modes" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </label>

          <label>Objeção levantada (opcional)
            <input v-model="context.objection" placeholder="ex: Tá caro, vi mais barato online" />
          </label>

          <label>Fala / situação do cliente
            <textarea v-model="message" rows="4" placeholder="Descreva o que o cliente disse ou está procurando..." />
          </label>

          <button class="send-btn" :disabled="loading || !message.trim()" @click="send">
            <span v-if="loading">Analisando...</span>
            <span v-else>Analisar com IA →</span>
          </button>

          <div v-if="error" class="error-box">⚠️ {{ error }}</div>
        </section>

        <section class="result-section" v-if="result">
          <div v-if="result.erro" class="error-box">{{ result.erro }}</div>

          <template v-else>
            <div class="result-card alert" v-if="result.alerta_vendedor">
              <h3>⚡ Alerta para o Vendedor</h3>
              <p>{{ result.alerta_vendedor }}</p>
            </div>

            <div class="result-card">
              <h3>🔍 Leitura do Interesse</h3>
              <p>{{ result.leitura_interesse }}</p>
            </div>

            <div class="result-card">
              <h3>📊 Diagnóstico de Oportunidade</h3>
              <p :style="{ color: opportunityColor, fontWeight: 700 }">{{ result.diagnostico_oportunidade }}</p>
            </div>

            <div class="result-card" v-if="result.script_abertura">
              <h3>🗣️ Script de Abertura</h3>
              <blockquote>{{ result.script_abertura }}</blockquote>
            </div>

            <div class="result-card" v-if="result.quebra_objecao">
              <h3>🛡️ Quebra de Objeção</h3>
              <blockquote>{{ result.quebra_objecao }}</blockquote>
            </div>

            <div class="result-card" v-if="result.perguntas_qualificacao?.length">
              <h3>❓ Perguntas de Qualificação</h3>
              <ol>
                <li v-for="(q, i) in result.perguntas_qualificacao" :key="i">{{ q }}</li>
              </ol>
            </div>

            <div class="result-card offer" v-if="result.oferta_principal?.produto">
              <h3>🎯 Oferta Principal</h3>
              <p class="offer-product">{{ result.oferta_principal.produto }}</p>
              <p>{{ result.oferta_principal.argumento }}</p>
              <p class="highlight">✅ {{ result.oferta_principal.ponto_chave }}</p>
            </div>

            <div class="result-card cross" v-if="result.cross_sell?.produto">
              <h3>➕ Cross-sell</h3>
              <p class="offer-product">{{ result.cross_sell.produto }}</p>
              <p>{{ result.cross_sell.gancho }}</p>
            </div>

            <div class="result-card anchor" v-if="result.ancoragem?.opcao_premium">
              <h3>⚓ Ancoragem</h3>
              <div class="anchor-grid">
                <div class="anchor-option premium">
                  <span class="anchor-tag">Premium</span>
                  <strong>{{ result.ancoragem.opcao_premium.produto }}</strong>
                  <span class="price">{{ result.ancoragem.opcao_premium.preco_estimado }}</span>
                  <p>{{ result.ancoragem.opcao_premium.diferencial }}</p>
                </div>
                <div class="anchor-option recommended">
                  <span class="anchor-tag">⭐ Recomendado</span>
                  <strong>{{ result.ancoragem.opcao_recomendada.produto }}</strong>
                  <span class="price">{{ result.ancoragem.opcao_recomendada.preco_estimado }}</span>
                  <p>{{ result.ancoragem.opcao_recomendada.diferencial }}</p>
                </div>
              </div>
            </div>

            <div class="result-card" v-if="result.gatilhos_ativos?.length">
              <h3>🔔 Gatilhos Detectados</h3>
              <div class="tags">
                <span v-for="g in result.gatilhos_ativos" :key="g" class="tag">{{ g }}</span>
              </div>
            </div>
          </template>
        </section>
      </div>
    </main>
  </div>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', system-ui, sans-serif;
  background: #0f1117;
  color: #e2e8f0;
  min-height: 100vh;
}

.app { display: flex; flex-direction: column; min-height: 100vh; }

header {
  background: #1a1d27;
  border-bottom: 1px solid #2d3148;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
}

.header-inner { display: flex; align-items: center; justify-content: space-between; width: 100%; max-width: 1400px; margin: 0 auto; }

.logo { display: flex; align-items: center; gap: 10px; }
.logo-icon { font-size: 22px; }
.logo-text { font-size: 18px; font-weight: 700; color: #a78bfa; }
.logo-text small { font-size: 12px; color: #64748b; font-weight: 400; margin-left: 6px; }

.token-badge { font-size: 11px; color: #64748b; background: #1e2235; padding: 3px 8px; border-radius: 12px; }

main { flex: 1; max-width: 1400px; margin: 0 auto; width: 100%; padding: 24px; }

h2 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 12px; }

.presets-section { margin-bottom: 24px; }

.presets-grid { display: flex; flex-wrap: wrap; gap: 8px; }

.preset-btn {
  background: #1a1d27;
  border: 1px solid #2d3148;
  border-radius: 8px;
  padding: 8px 14px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  transition: all 0.15s;
  max-width: 220px;
}
.preset-btn:hover { border-color: #7c3aed; background: #1e1b2e; }
.preset-btn.active { border-color: #7c3aed; background: #1e1b2e; }

.preset-label { font-size: 13px; font-weight: 600; color: #e2e8f0; }
.preset-desc { font-size: 11px; color: #64748b; text-align: left; }

.workspace { display: grid; grid-template-columns: 380px 1fr; gap: 24px; align-items: start; }

@media (max-width: 900px) {
  .workspace { grid-template-columns: 1fr; }
}

.form-section {
  background: #1a1d27;
  border: 1px solid #2d3148;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: sticky;
  top: 24px;
}

label { display: flex; flex-direction: column; gap: 5px; font-size: 12px; color: #94a3b8; font-weight: 500; }

input, select, textarea {
  background: #0f1117;
  border: 1px solid #2d3148;
  border-radius: 6px;
  padding: 8px 10px;
  color: #e2e8f0;
  font-size: 13px;
  transition: border-color 0.15s;
  font-family: inherit;
}
input:focus, select:focus, textarea:focus { outline: none; border-color: #7c3aed; }
select option { background: #1a1d27; }
textarea { resize: vertical; }

.send-btn {
  background: #7c3aed;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.send-btn:hover:not(:disabled) { background: #6d28d9; }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.error-box {
  background: #1f1315;
  border: 1px solid #7f1d1d;
  color: #fca5a5;
  border-radius: 8px;
  padding: 12px;
  font-size: 13px;
}

.result-section { display: flex; flex-direction: column; gap: 12px; }

.result-card {
  background: #1a1d27;
  border: 1px solid #2d3148;
  border-radius: 10px;
  padding: 16px;
}

.result-card h3 { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #64748b; margin-bottom: 8px; }
.result-card p { font-size: 14px; line-height: 1.6; }
.result-card ol { padding-left: 18px; font-size: 14px; line-height: 2; }

blockquote {
  border-left: 3px solid #7c3aed;
  padding-left: 14px;
  font-size: 14px;
  line-height: 1.7;
  color: #c4b5fd;
  font-style: italic;
}

.result-card.alert { border-color: #d97706; background: #1c1710; }
.result-card.alert h3 { color: #fbbf24; }
.result-card.alert p { color: #fde68a; }

.result-card.offer { border-color: #059669; background: #0d1f17; }
.result-card.offer h3 { color: #34d399; }
.offer-product { font-size: 16px; font-weight: 700; color: #e2e8f0; margin-bottom: 6px; }
.highlight { color: #6ee7b7; font-size: 13px; margin-top: 8px; }

.result-card.cross { border-color: #0284c7; background: #0c1929; }
.result-card.cross h3 { color: #38bdf8; }

.result-card.anchor { border-color: #7c3aed; }

.anchor-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 4px; }
@media (max-width: 600px) { .anchor-grid { grid-template-columns: 1fr; } }

.anchor-option { background: #0f1117; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 4px; border: 1px solid #2d3148; }
.anchor-option.recommended { border-color: #7c3aed; }
.anchor-option strong { font-size: 13px; color: #e2e8f0; }
.anchor-option p { font-size: 12px; color: #94a3b8; margin-top: 4px; }
.anchor-tag { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #7c3aed; letter-spacing: 0.08em; }
.anchor-option.premium .anchor-tag { color: #64748b; }
.price { font-size: 15px; font-weight: 700; color: #a78bfa; }

.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.tag {
  background: #1e2235;
  border: 1px solid #2d3148;
  color: #a78bfa;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
