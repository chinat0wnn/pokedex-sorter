# 🗺️ Plano de Implementação — Novos Critérios de Ordenação

> **Projeto:** Pokédex Sort Visualizer  
> **Data:** 2026-04-14  
> **Status:** ✅ IMPLEMENTADO E TESTADO (2026-04-14)  

---

## 📋 Objetivo

Expandir a aplicação para permitir ordenação dos Pokémon por diferentes critérios além do número da Pokédex. Os novos critérios serão:

| Critério | Chave (`sort_key`) | Exemplo |
|---|---|---|
| 🔢 Número da Pokédex | `id` | #1 → #151 (atual) |
| 🔤 Alfabético (A-Z) | `name` | Abra → Zubat |
| 🔥 Tipo Primário | `type_primary` | Bug → Water |
| 📊 Base Stats (Total) | `base_stats_total` | Magikarp (200) → Mewtwo (680) |
| 🏠 Habitat | `habitat` | Cave → Waters-edge |

---

## 🔧 Mudanças por Arquivo

### 1. Backend — `backend/services/pokemon_service.py`

**O que muda:** Enriquecer os dados de cada Pokémon com campos novos.

**Dados atuais capturados:**
```python
{"id": 25, "name": "pikachu", "img": "..."}
```

**Dados após a mudança:**
```python
{
    "id": 25,
    "name": "pikachu",
    "img": "...",
    "type_primary": "electric",       # types[0].type.name
    "type_secondary": null,           # types[1].type.name ou null
    "base_stats_total": 320,          # sum(stats[].base_stat)
    "hp": 35,                         # stats individuais
    "attack": 55,
    "defense": 40,
    "special_attack": 50,
    "special_defense": 50,
    "speed": 90,
    "height": 4,
    "weight": 60,
    "habitat": "forest",              # via /pokemon-species/{id}
    "generation": "generation-i"      # via /pokemon-species/{id}
}
```

**Como:**
- Extrair `types`, `stats`, `height`, `weight` do endpoint `/pokemon/{id}` (já chamado)
- Adicionar segunda chamada ao endpoint `/pokemon-species/{id}` para `habitat` e `generation`

> ⚠️ **Impacto:** Dobra o número de requests à PokéAPI (151 → 302). Com throttle de 0.05s, o tempo de carregamento sobe de ~12s para ~24s.

---

### 2. Backend — `backend/algorithms/sorting.py`

**O que muda:** Todos os 5 algoritmos passam a receber um parâmetro `sort_key` em vez de comparar sempre por `id`.

**Antes:**
```python
def bubble_sort(arr: list[dict]) -> list[dict]:
    ...
    if a[j]["id"] > a[j + 1]["id"]:
```

**Depois:**
```python
def bubble_sort(arr: list[dict], sort_key: str = "id") -> list[dict]:
    ...
    if a[j][sort_key] > a[j + 1][sort_key]:
```

**Algoritmos afetados:**
- `bubble_sort`
- `selection_sort`
- `insertion_sort`
- `merge_sort`
- `quick_sort`

A função `run_algorithm()` também recebe `sort_key` e repassa ao algoritmo escolhido.

---

### 3. Backend — `backend/routes/sort.py`

**O que muda:** A rota de sorting aceita um novo campo `sort_by` no body do request.

**Antes:**
```python
body = request.get_json(silent=True) or {}
# só usava "array" e "algorithm"
```

**Depois:**
```python
body = request.get_json(silent=True) or {}
sort_by = body.get("sort_by", "id")

VALID_SORT_KEYS = {"id", "name", "type_primary", "base_stats_total", "habitat"}

if sort_by not in VALID_SORT_KEYS:
    return jsonify({"error": f"Invalid sort_by: {sort_by}"}), 400

result = run_algorithm(algorithm, arr, sort_key=sort_by)
```

---

### 4. Frontend — `frontend/src/services/api.js`

**O que muda:** A função `runSort` envia o campo `sort_by` para o backend.

**Antes:**
```javascript
export async function runSort(algorithm, array) {
  const res = await fetch(`${BASE}/sort/${algorithm}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ array }),
  });
```

**Depois:**
```javascript
export async function runSort(algorithm, array, sortBy = "id") {
  const res = await fetch(`${BASE}/sort/${algorithm}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ array, sort_by: sortBy }),
  });
```

---

### 5. Frontend — `frontend/src/App.jsx`

**O que muda:** Adicionar um dropdown "Ordenar por" na sidebar, abaixo do dropdown de Algoritmo.

**Novo state:**
```jsx
const SORT_CRITERIA = {
  id:               "🔢 Pokédex (#)",
  name:             "🔤 Alfabético (A-Z)",
  type_primary:     "🔥 Tipo Primário",
  base_stats_total: "📊 Base Stats (Total)",
  habitat:          "🏠 Habitat",
};

const [sortBy, setSortBy] = useState("id");
```

**No handleStart:**
```diff
- const result = await runSort(algorithm, shuffled);
+ const result = await runSort(algorithm, shuffled, sortBy);
```

**UI:** Um `<select>` estilizado com ícones e label "Ordenar por".

---

### 6. Frontend — `frontend/src/components/BarChart.jsx`

**O que muda:** A altura das barras passa a refletir o critério de ordenação escolhido.

| Critério | Cálculo da altura |
|---|---|
| `id` | `p.id / 151` (atual) |
| `base_stats_total` | `p.base_stats_total / maxStats` |
| `name` | Índice alfabético / total |
| `type_primary` | Índice alfabético do tipo / total de tipos |
| `habitat` | Índice alfabético do habitat / total de habitats |

**Como:** Receber `sortBy` como prop e calcular a altura dinamicamente.

---

### 7. Frontend — `frontend/src/components/CardGrid.jsx`

**O que muda:** Os cards mostram informações extras dependendo do critério de ordenação.

| Critério | Info extra no card |
|---|---|
| `id` | Número da Pokédex (atual) |
| `name` | Nome destacado |
| `type_primary` | Badge colorido com o tipo (Fire = vermelho, Water = azul, etc.) |
| `base_stats_total` | Valor total dos stats |
| `habitat` | Nome do habitat |

---

## 📊 Resumo de Impacto

| Camada | Arquivos | Tipo de mudança |
|---|---|---|
| Backend | `pokemon_service.py` | Enriquecer dados (types, stats, habitat) |
| Backend | `sorting.py` | Parâmetro `sort_key` nos 5 algoritmos |
| Backend | `routes/sort.py` | Aceitar `sort_by` no body |
| Frontend | `api.js` | Enviar `sort_by` para o backend |
| Frontend | `App.jsx` | Dropdown "Ordenar por" + state |
| Frontend | `BarChart.jsx` | Altura dinâmica por critério |
| Frontend | `CardGrid.jsx` | Info contextual nos cards |

**Total:** 7 arquivos modificados, 0 arquivos novos

---

## ✅ Plano de Verificação

### Testes Automatizados
1. Subir backend (`python app.py`) e frontend (`npm run dev`)
2. Carregar os 151 Pokémon
3. Para cada critério de ordenação:
   - Selecionar no dropdown
   - Executar cada algoritmo
   - Verificar que a ordenação está correta
4. Verificar nos logs do backend que o `sort_key` correto está sendo usado

### Verificação Visual
- **Pokédex (#):** Cards vão de #1 Bulbasaur a #151 Mew
- **Alfabético:** Cards vão de Abra a Zubat
- **Tipo Primário:** Todos os Bug juntos, depois Dragon, Electric, etc.
- **Base Stats:** Do mais fraco (Magikarp ~200) ao mais forte (Mewtwo ~680)
- **Habitat:** Agrupados por Cave, Forest, Grassland, etc.

---

## 📝 Ordem de Execução

```
1. pokemon_service.py  ← Primeiro: dados são a base de tudo
2. sorting.py          ← Segundo: algoritmos usam os novos dados
3. routes/sort.py      ← Terceiro: rota expõe o parâmetro
4. api.js              ← Quarto: frontend envia o parâmetro
5. App.jsx             ← Quinto: UI para o usuário escolher
6. BarChart.jsx         ← Sexto: visualização reflete o critério
7. CardGrid.jsx         ← Sétimo: cards mostram info extra
8. Testes no browser    ← Por último: validação completa
```
