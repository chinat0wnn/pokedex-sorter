# Pokédex Sort Visualizer

Visualizador de algoritmos de ordenação temático usando os 151 Pokémon originais.  
**Backend**: Flask (Python) · **Frontend**: React

---

## Estrutura do Projeto

```
pokedex-sorter/
├── backend/
│   ├── app.py                  ← Entry point Flask
│   ├── requirements.txt
│   ├── algorithms/
│   │   └── sorting.py          ← 5 algoritmos + geração de steps
│   ├── routes/
│   │   ├── pokemon.py          ← GET/POST /api/pokemon/
│   │   └── sort.py             ← POST /api/sort/<algorithm>
│   └── services/
│       └── pokemon_service.py  ← Cache + fetch da PokéAPI
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.jsx
        ├── index.js
        ├── components/
        │   ├── BarChart.jsx
        │   ├── CardGrid.jsx
        │   ├── StatsPanel.jsx
        │   └── CompareModal.jsx
        ├── hooks/
        │   ├── useSort.js
        │   └── usePokemon.js
        ├── services/
        │   └── api.js
        └── utils/
            └── shuffle.js
```

---

## Como Rodar

### 1. Backend (Flask)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

O servidor sobe em **http://localhost:5000**

---

### 2. Frontend (React)

```bash
cd frontend
npm install
npm start
```

O app abre em **http://localhost:3000**

> O `"proxy": "http://localhost:5000"` no `package.json` redireciona `/api/*` automaticamente para o Flask.

---

## Endpoints da API

### Pokémon

| Método | Rota                    | Descrição                              |
|--------|-------------------------|----------------------------------------|
| POST   | `/api/pokemon/load`     | Dispara carregamento background        |
| GET    | `/api/pokemon/progress` | Retorna progresso do carregamento      |
| GET    | `/api/pokemon/`         | Retorna todos os 151 Pokémon           |

### Ordenação

| Método | Rota                    | Descrição                              |
|--------|-------------------------|----------------------------------------|
| GET    | `/api/sort/algorithms`  | Lista algoritmos + complexidades       |
| POST   | `/api/sort/bubble`      | Gera steps do Bubble Sort              |
| POST   | `/api/sort/selection`   | Gera steps do Selection Sort          |
| POST   | `/api/sort/insertion`   | Gera steps do Insertion Sort          |
| POST   | `/api/sort/merge`       | Gera steps do Merge Sort              |
| POST   | `/api/sort/quick`       | Gera steps do Quick Sort              |
| POST   | `/api/sort/compare`     | Compara todos os algoritmos           |

### Exemplo de Request para `/api/sort/bubble`

```json
POST /api/sort/bubble
Content-Type: application/json

{
  "array": [
    { "id": 25, "name": "pikachu", "img": "https://..." },
    { "id": 1,  "name": "bulbasaur", "img": "https://..." }
  ]
}
```

### Exemplo de Response

```json
{
  "algorithm": "bubble",
  "complexity": {
    "name": "Bubble Sort",
    "best": "O(n)",
    "average": "O(n²)",
    "worst": "O(n²)",
    "space": "O(1)"
  },
  "total_steps": 11325,
  "steps": [
    { "type": "compare",  "indices": [0, 1] },
    { "type": "swap",     "indices": [0, 1] },
    { "type": "sorted",   "index": 150 }
  ],
  "stats": {
    "compares": 11175,
    "swaps": 3742,
    "writes": 0,
    "total": 14917,
    "n": 151
  }
}
```

---

## Tipos de Steps (animação)

| Tipo        | Campos                        | Descrição                     |
|-------------|-------------------------------|-------------------------------|
| `compare`   | `indices: [i, j]`             | Elementos sendo comparados    |
| `swap`      | `indices: [i, j]`             | Elementos sendo trocados      |
| `overwrite` | `index: i, value: {...}`      | Sobrescrita (Merge Sort)      |
| `pivot`     | `index: i`                    | Pivot do Quick Sort           |
| `sorted`    | `index: i`                    | Elemento na posição final     |

---

## Funcionalidades

- ✅ 5 algoritmos de ordenação com geração de steps
- ✅ Animação controlável (play/pause/reset)
- ✅ Slider de velocidade (5ms–300ms)
- ✅ Dois modos de visualização (barras/cards)
- ✅ Contadores em tempo real (comparações, trocas, escritas)
- ✅ Complexidade teórica por algoritmo
- ✅ Feedback sonoro via Web Audio API
- ✅ Comparação de todos os algoritmos lado a lado
- ✅ Cache dos dados da PokéAPI no backend
