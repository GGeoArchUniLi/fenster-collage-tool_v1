import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import random
import uuid
import json
try:
    from duckduckgo_search import DDGS
except ImportError:
    pass

st.set_page_config(page_title="Patchwork Facade Generator Pro", layout="wide")

# --- SPRACH-WÖRTERBUCH (Alle 9 Sprachen inkl. Spanisch) ---
LANG_DICT = {
    "🇩🇪 DE": {
        "title": "🧱 Patchwork-Fassaden-Generator v4.1", "search_header": "1. Globale Suche", "country": "Land", "zip": "PLZ / Ort", "radius": "Umkreis (km)", "reuse": "🔄 Gebraucht", "new": "🆕 Neu", "search_btn": "🔍 Suchen", "custom_header": "2. Eigenbestand", "width": "Breite (mm)", "height": "Höhe (mm)", "add_btn": "➕ Hinzufügen", "wall_header": "Wandöffnung (bis 30m)", "shuffle_btn": "🎲 Neu clustern (KI)", "auto_rotate": "🔄 Auto-Rotation erlauben", "lock_pinned": "🔒 Gepinnte Fenster beim Würfeln behalten", "symmetry": "📐 Symmetrisches Cluster", "chaos": "Varianz / Chaos (%)", "opt_gaps_btn": "✂️ Zuschnitte umschalten (H/V)", "price_total": "Gesamtpreis Fenster", "win_area": "Gesamtfläche Fenster", "wall_area": "Fläche Wandöffnung", "fill_rate": "Füllgrad", "matrix_header": "📋 Fenster-Steuerung & Docking", "export_btn": "📥 CSV Einkaufsliste", "gaps_header": "🟥 Benötigte Zuschnitte (Exakt, keine Überlappung)", "no_gaps": "Die Wand ist perfekt gefüllt! Keine Zuschnitte benötigt.", "fill": "Zuschnitt Panel", "col_layer": "👁️ Sichtbar", "col_pin": "📌 Pin", "col_rotate": "🔄 90°", "col_force": "⭐ Prio", "col_type": "Typ", "col_status": "Status", "col_dim": "Maße (BxH)", "col_area": "Fläche (m²)", "col_source": "Herkunft", "col_price": "Preis", "col_link": "🛒 Shop"
    },
    "🇪🇸 ES": {
        "title": "🧱 Generador de Fachadas v4.1", "search_header": "1. Búsqueda Global", "country": "País", "zip": "C.P.", "radius": "Radio (km)", "reuse": "🔄 Usado", "new": "🆕 Nuevo", "search_btn": "🔍 Buscar", "custom_header": "2. Inventario Propio", "width": "Ancho (mm)", "height": "Alto (mm)", "add_btn": "➕ Añadir", "wall_header": "Apertura (hasta 30m)", "shuffle_btn": "🎲 Reagrupar (IA)", "auto_rotate": "🔄 Auto-rotación", "lock_pinned": "🔒 Mantener posiciones fijadas", "symmetry": "📐 Clúster Simétrico", "chaos": "Caos (%)", "opt_gaps_btn": "✂️ Alternar cortes (H/V)", "price_total": "Precio Total", "win_area": "Área de Ventanas", "wall_area": "Área de Apertura", "fill_rate": "Tasa de relleno", "matrix_header": "📋 Matriz de Control", "export_btn": "📥 Exportar CSV", "gaps_header": "🟥 Paneles de Relleno (Sin superposición)", "no_gaps": "¡Muro perfecto!", "fill": "Panel de corte", "col_layer": "👁️ Visible", "col_pin": "📌 Fijar", "col_rotate": "🔄 90°", "col_force": "⭐ Prio", "col_type": "Tipo", "col_status": "Estado", "col_dim": "Dimensiones", "col_area": "Área (m²)", "col_source": "Origen", "col_price": "Precio", "col_link": "🛒 Tienda"
    },
    "🇬🇧 EN": {
        "title": "🧱 Facade Generator v4.1", "search_header": "1. Search", "country": "Country", "zip": "ZIP", "radius": "Radius", "reuse": "🔄 Used", "new": "🆕 New", "search_btn": "🔍 Search", "custom_header": "2. Custom Inventory", "width": "Width", "height": "Height", "add_btn": "➕ Add", "wall_header": "Wall Opening", "shuffle_btn": "🎲 Shuffle (AI)", "auto_rotate": "🔄 Auto-Rotation", "lock_pinned": "🔒 Lock pinned", "symmetry": "📐 Symmetry", "chaos": "Chaos", "opt_gaps_btn": "✂️ Toggle Fillers", "price_total": "Total Price", "win_area": "Window Area", "wall_area": "Wall Area", "fill_rate": "Fill Rate", "matrix_header": "📋 Window Control", "export_btn": "📥 Export CSV", "gaps_header": "🟥 Required Fillers", "no_gaps": "Perfectly filled!", "fill": "Filler", "col_layer": "👁️ Vis", "col_pin": "📌 Pin", "col_rotate": "🔄 90°", "col_force": "⭐ Prio", "col_type": "Type", "col_status": "Status", "col_dim": "Dims", "col_area": "Area", "col_source": "Source", "col_price": "Price", "col_link": "🛒 Shop"
    },
    "🇫🇷 FR": {"title": "🧱 Générateur de Façade", "search_header": "Recherche", "country": "Pays", "zip": "CP", "radius": "Rayon", "reuse": "Usagé", "new": "Neuf", "search_btn": "Chercher", "custom_header": "Inventaire", "width": "Largeur", "height": "Hauteur", "add_btn": "Ajouter", "wall_header": "Ouverture", "shuffle_btn": "🎲 Mélanger", "auto_rotate": "🔄 Rotation", "lock_pinned": "🔒 Verrouiller", "symmetry": "📐 Symétrie", "chaos": "Chaos", "opt_gaps_btn": "✂️ Alterner", "price_total": "Prix Total", "win_area": "Surface Fen.", "wall_area": "Surface Mur", "fill_rate": "Remplissage", "matrix_header": "📋 Matrice", "export_btn": "📥 CSV", "gaps_header": "🟥 Panneaux", "no_gaps": "Parfait!", "fill": "Panneau", "col_layer": "👁️", "col_pin": "📌", "col_rotate": "🔄", "col_force": "⭐", "col_type": "Type", "col_status": "Statut", "col_dim": "Dim", "col_area": "Surface", "col_source": "Source", "col_price": "Prix", "col_link": "Lien"},
    "🇮🇹 IT": {"title": "🧱 Generatore Facciate", "search_header": "Ricerca", "country": "Paese", "zip": "CAP", "radius": "Raggio", "reuse": "Usato", "new": "Nuovo", "search_btn": "Cerca", "custom_header": "Inventario", "width": "Largh.", "height": "Altezza", "add_btn": "Aggiungi", "wall_header": "Muro", "shuffle_btn": "🎲 Rimescola", "auto_rotate": "🔄 Rotazione", "lock_pinned": "🔒 Blocca", "symmetry": "📐 Simmetria", "chaos": "Caos", "opt_gaps_btn": "✂️ Tagli", "price_total": "Prezzo", "win_area": "Area Fin.", "wall_area": "Area Muro", "fill_rate": "Riemp.", "matrix_header": "📋 Matrice", "export_btn": "📥 CSV", "gaps_header": "🟥 Pannelli", "no_gaps": "Perfetto!", "fill": "Pannello", "col_layer": "👁️", "col_pin": "📌", "col_rotate": "🔄", "col_force": "⭐", "col_type": "Tipo", "col_status": "Stato", "col_dim": "Dim", "col_area": "Area", "col_source": "Fonte", "col_price": "Prezzo", "col_link": "Link"},
    "🇨🇭 RM": {"title": "🧱 Generatur Façadas", "search_header": "Tschertga", "country": "Pajais", "zip": "PLZ", "radius": "Radius", "reuse": "Duvrà", "new": "Nov", "search_btn": "Tschertgar", "custom_header": "Inventari", "width": "Ladezza", "height": "Autezza", "add_btn": "Agiuntar", "wall_header": "Paraid", "shuffle_btn": "🎲 Maschadar", "auto_rotate": "🔄 Rotaziun", "lock_pinned": "🔒 Fixar", "symmetry": "📐 Simetria", "chaos": "Caos", "opt_gaps_btn": "✂️ Panels", "price_total": "Pretsch", "win_area": "Surfatscha", "wall_area": "Paraid", "fill_rate": "Emplenida", "matrix_header": "📋 Matrix", "export_btn": "📥 CSV", "gaps_header": "🟥 Panels", "no_gaps": "Perfegt!", "fill": "Panel", "col_layer": "👁️", "col_pin": "📌", "col_rotate": "🔄", "col_force": "⭐", "col_type": "Tip", "col_status": "Status", "col_dim": "Dim", "col_area": "Area", "col_source": "Funtauna", "col_price": "Pretsch", "col_link": "Link"},
    "🇧🇬 BG": {"title": "🧱 Генератор на фасади", "search_header": "Търсене", "country": "Държава", "zip": "ПК", "radius": "Радиус", "reuse": "Стари", "new": "Нови", "search_btn": "Търси", "custom_header": "Инвентар", "width": "Ширина", "height": "Височина", "add_btn": "Добави", "wall_header": "Стена", "shuffle_btn": "🎲 Разбъркай", "auto_rotate": "🔄 Ротация", "lock_pinned": "🔒 Заключи", "symmetry": "📐 Симетрия", "chaos": "Хаос", "opt_gaps_btn": "✂️ Панели", "price_total": "Цена", "win_area": "Площ Проз.", "wall_area": "Площ Стена", "fill_rate": "Запълване", "matrix_header": "📋 Матрица", "export_btn": "📥 CSV", "gaps_header": "🟥 Панели", "no_gaps": "Идеално!", "fill": "Панел", "col_layer": "👁️", "col_pin": "📌", "col_rotate": "🔄", "col_force": "⭐", "col_type": "Тип", "col_status": "Статус", "col_dim": "Разм", "col_area": "Площ", "col_source": "Източник", "col_price": "Цена", "col_link": "Линк"},
    "🇮🇱 HE": {"title": "🧱 מחולל חזיתות", "search_header": "חיפוש", "country": "מדינה", "zip": "מיקוד", "radius": "רדיוס", "reuse": "ישן", "new": "חדש", "search_btn": "חפש", "custom_header": "מלאי", "width": "רוחב", "height": "גובה", "add_btn": "הוסף", "wall_header": "קיר", "shuffle_btn": "🎲 ערבב", "auto_rotate": "🔄 סיבוב", "lock_pinned": "🔒 נעל", "symmetry": "📐 סימטריה", "chaos": "כאוס", "opt_gaps_btn": "✂️ פאנלים", "price_total": "מחיר", "win_area": "שטח חלונות", "wall_area": "שטח קיר", "fill_rate": "מילוי", "matrix_header": "📋 טבלה", "export_btn": "📥 CSV", "gaps_header": "🟥 פאנלים", "no_gaps": "מושלם!", "fill": "פאנל", "col_layer": "👁️", "col_pin": "📌", "col_rotate": "🔄", "col_force": "⭐", "col_type": "סוג", "col_status": "סטטוס", "col_dim": "מידות", "col_area": "שטח", "col_source": "מקור", "col_price": "מחיר", "col_link": "לינק"},
    "🇯🇵 JA": {"title": "🧱 ファサードジェネレーター", "search_header": "検索", "country": "国", "zip": "郵便番号", "radius": "半径", "reuse": "中古", "new": "新品", "search_btn": "検索", "custom_header": "在庫", "width": "幅", "height": "高さ", "add_btn": "追加", "wall_header": "壁", "shuffle_btn": "🎲 シャッフル", "auto_rotate": "🔄 自動回転", "lock_pinned": "🔒 固定", "symmetry": "📐 対称", "chaos": "カオス", "opt_gaps_btn": "✂️ パネル", "price_total": "価格", "win_area": "窓面積", "wall_area": "壁面積", "fill_rate": "充填率", "matrix_header": "📋 マトリックス", "export_btn": "📥 CSV", "gaps_header": "🟥 パネル", "no_gaps": "完璧！", "fill": "パネル", "col_layer": "👁️", "col_pin": "📌", "col_rotate": "🔄", "col_force": "⭐", "col_type": "タイプ", "col_status": "ステータス", "col_dim": "寸法", "col_area": "面積", "col_source": "ソース", "col_price": "価格", "col_link": "リンク"}
}

langs = list(LANG_DICT.keys())
lang_choice = st.radio("Language / Sprache / Idioma:", langs, horizontal=True)
T = LANG_DICT[lang_choice]
st.title(T["title"])

# --- SESSION STATES ---
if 'inventory' not in st.session_state: st.session_state['inventory'] = []
if 'custom_windows' not in st.session_state: st.session_state['custom_windows'] = []
if 'is_loaded' not in st.session_state: st.session_state['is_loaded'] = False
if 'item_states' not in st.session_state: st.session_state['item_states'] = {} 
if 'pos_counter' not in st.session_state: st.session_state['pos_counter'] = 1 
if 'layout_seed' not in st.session_state: st.session_state['layout_seed'] = 42 
if 'gap_toggle' not in st.session_state: st.session_state['gap_toggle'] = False
if 'last_ts' not in st.session_state: st.session_state['last_ts'] = 0

# Bidirektionale Slider Sync
if 'w_val' not in st.session_state: st.session_state.w_val = 4000
if 'h_val' not in st.session_state: st.session_state.h_val = 3000

def sync_w_sli(): st.session_state.w_val = st.session_state.w_sli
def sync_w_num(): st.session_state.w_val = st.session_state.w_num
def sync_h_sli(): st.session_state.h_val = st.session_state.h_sli
def sync_h_num(): st.session_state.h_val = st.session_state.h_num

def shuffle_layout(): st.session_state['layout_seed'] = random.randint(1, 10000)
def optimize_gaps(): st.session_state['gap_toggle'] = not st.session_state['gap_toggle']

# =====================================================================
# --- OFFIZIELLE STREAMLIT KOMPONENTE FÜR DRAG & DROP (DER BUGFIX) ---
# =====================================================================
html_component_code = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@1.3.0/dist/streamlit.js"></script>
  <style>
    body { margin: 0; padding: 0; background-color: #f0f2f6; font-family: sans-serif; overflow: hidden; }
    .container { display: flex; align-items: flex-end; justify-content: center; gap: 15px; padding-top: 10px; }
    .scale-figure { opacity: 0.8; }
    #wall { border: 4px solid #31333F; position: relative; background: repeating-linear-gradient(45deg, #fce4e4, #fce4e4 10px, #ffffff 10px, #ffffff 20px); overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-radius: 2px; }
    .window { position: absolute; border: 2px solid #555; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #222; cursor: grab; user-select: none; z-index: 10; box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: box-shadow 0.1s; }
    .window.pinned { cursor: not-allowed; opacity: 0.95; border: 3px solid #31333F; box-shadow: none; }
    .window:active:not(.pinned) { cursor: grabbing; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); z-index: 1000 !important; }
    .win-icons { position: absolute; top: 2px; right: 2px; display: flex; gap: 3px; z-index: 20; }
    .win-btn { background: rgba(255,255,255,0.9); border: 1px solid #777; border-radius: 3px; font-size: 10px; cursor: pointer; padding: 2px 4px; pointer-events: auto; }
    .win-btn:hover { background: white; transform: scale(1.1); }
    .gap { position: absolute; background-color: rgba(255,75,75,0.4); border: 1px dashed #FF4B4B; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white; box-sizing: border-box; z-index: 5; font-weight: 600; pointer-events: none; text-shadow: 0px 1px 2px rgba(0,0,0,0.8); }
  </style>
</head>
<body>
  <div class="container">
    <div id="figure" class="scale-figure" title="Scale Figure (1,78m)"></div>
    <div id="wall"></div>
  </div>
  <script>
    let isReady = false;
    let scale = 1;
    let canvas_h = 1;
    let draggedEl = null; 
    let startX, startY, initialLeft, initialTop;
    
    function sendToPython(action, id, x, y) {
        Streamlit.setComponentValue({action: action, id: id, x: x, y: y, ts: Date.now()});
    }

    function renderData(args) {
        scale = args.scale;
        canvas_h = args.wall_h * scale;
        const wallW = args.wall_w * scale;
        
        const wall = document.getElementById("wall");
        wall.style.width = wallW + "px";
        wall.style.height = canvas_h + "px";
        wall.innerHTML = ""; 

        const fig = document.getElementById("figure");
        fig.style.width = Math.max(25, 400 * scale) + "px";
        fig.style.height = (1780 * scale) + "px";
        const svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 280'><circle cx='50' cy='25' r='15' fill='%23333'/><path d='M 30 50 Q 50 40 70 50 L 85 130 L 70 130 L 65 70 L 60 130 L 65 260 L 45 260 L 50 140 L 45 140 L 40 260 L 20 260 L 25 130 L 20 70 L 15 130 Z' fill='%23333'/></svg>";
        fig.style.background = `url("${svg}") no-repeat bottom center/contain`;

        args.gaps.forEach(g => {
            const el = document.createElement('div');
            el.className = 'gap';
            el.style.width = (g.w * scale) + 'px'; el.style.height = (g.h * scale) + 'px';
            el.style.left = (g.x * scale) + 'px'; el.style.top = (canvas_h - (g.y * scale) - (g.h * scale)) + 'px';
            if((g.w * g.h / 1000000) >= 0.4) el.innerText = (g.w * g.h / 1000000).toFixed(2) + " m²";
            wall.appendChild(el);
        });

        args.windows.forEach(w => {
            const el = document.createElement('div');
            el.className = 'window';
            if(w.is_pinned) el.classList.add('pinned');
            el.id = w.id;
            
            let pinIcon = w.is_pinned ? "❌" : "📌";
            el.innerHTML = `
                <div class="win-icons">
                    <div class="win-btn rot-btn" title="Rotieren">🔄</div>
                    <div class="win-btn pin-btn" title="Pinnen">${pinIcon}</div>
                </div>
                <div style="margin-top:12px; pointer-events:none; text-align:center; line-height: 1.2;">
                    ${w.is_pinned ? "📌 " : ""}${w.label}<br><span style="font-size: 9px; font-weight: 500;">${w.w}x${w.h}</span>
                </div>
            `;
            
            el.style.backgroundColor = w.color;
            el.style.width = (w.w * scale) + 'px'; el.style.height = (w.h * scale) + 'px';
            el.style.left = (w.x * scale) + 'px'; el.style.top = (canvas_h - (w.y * scale) - (w.h * scale)) + 'px';
            
            el.querySelector('.rot-btn').addEventListener('click', (e) => {
                e.stopPropagation(); sendToPython("rotate", w.id, 0, 0);
            });
            el.querySelector('.pin-btn').addEventListener('click', (e) => {
                e.stopPropagation(); 
                const mm_x = Math.round(parseInt(el.style.left) / scale);
                const mm_y = Math.round((canvas_h - parseInt(el.style.top) - parseInt(el.style.height)) / scale);
                sendToPython("pin", w.id, mm_x, mm_y);
            });
            
            el.addEventListener('mousedown', dragStart);
            wall.appendChild(el);
        });
        Streamlit.setFrameHeight();
    }

    function onRender(event) {
        if (event.data.type !== "streamlit:render") return;
        renderData(event.data.args);
        if (!isReady) {
            Streamlit.setFrameHeight();
            isReady = true;
        }
    }

    window.addEventListener("message", onRender);
    Streamlit.setComponentReady();

    function dragStart(e) {
        if (e.target.classList.contains('win-btn')) return;
        let targetWindow = e.target.closest('.window');
        if (!targetWindow || targetWindow.classList.contains('pinned')) return;
        draggedEl = targetWindow; startX = e.clientX; startY = e.clientY;
        initialLeft = parseInt(draggedEl.style.left, 10); initialTop = parseInt(draggedEl.style.top, 10);
        document.addEventListener('mousemove', drag); document.addEventListener('mouseup', dragEnd);
    }
    function drag(e) {
        if (!draggedEl) return; e.preventDefault();
        draggedEl.style.left = (initialLeft + (e.clientX - startX)) + 'px';
        draggedEl.style.top = (initialTop + (e.clientY - startY)) + 'px';
    }
    function dragEnd(e) {
        document.removeEventListener('mousemove', drag); document.removeEventListener('mouseup', dragEnd);
        if(draggedEl) {
            const px_x = parseInt(draggedEl.style.left, 10);
            const px_y = parseInt(draggedEl.style.top, 10);
            const px_h = parseInt(draggedEl.style.height, 10);
            const mm_x = Math.round(px_x / scale);
            const mm_y = Math.round((canvas_h - px_y - px_h) / scale);
            sendToPython("move", draggedEl.id, mm_x, mm_y);
            draggedEl = null;
        }
    }
  </script>
</body>
</html>
"""

# HIER IST DER FIX: Streamlit Custom Component Ordner generieren
if not os.path.exists("canvas_component"):
    os.makedirs("canvas_component")
with open("canvas_component/index.html", "w", encoding="utf-8") as f:
    f.write(html_component_code)
    
interactive_canvas = components.declare_component("interactive_canvas", path="canvas_component")
# =====================================================================


# --- FUNKTION: Daten suchen ---
def harvest_materials(land, plz, radius, use_reuse, use_new):
    materials = []
    queries = []
    if use_reuse: queries.append((f"site:ebay.de OR site:kleinanzeigen.de Fenster gebraucht {plz} {land}", "Re-Use", '#4682b4'))
    if use_new: queries.append((f"Fenster neu kaufen {plz} {land}", "Neu", '#add8e6'))
        
    for query, condition, color in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=15))
                for res in results:
                    match = re.search(r'(\d{3,4})\s*[xX*]\s*(\d{3,4})', res['title'] + " " + res['body'])
                    if match:
                        w, h = int(match.group(1)), int(match.group(2))
                        if 300 <= w <= 30000 and 300 <= h <= 30000:
                            price_match = re.search(r'(\d{1,5})[.,]?\d*\s*[€|EUR]', res['title'] + " " + res['body'])
                            price = float(price_match.group(1)) if price_match else float(int((w * h) / 20000) + random.randint(10, 50))
                            
                            item_id = uuid.uuid4().hex
                            pos_label = f"P{st.session_state['pos_counter']}"
                            st.session_state['pos_counter'] += 1
                            materials.append({
                                'id': item_id, 'pos_label': pos_label, 'w': w, 'h': h, 'type': 'Fenster', 'color': color, 
                                'price': price, 'source': res['title'][:30] + '...', 'condition': condition, 'link': res['href']
                            })
                            st.session_state['item_states'][item_id] = {'visible': True, 'pinned': False, 'force': False, 'rotated': False, 'man_x': None, 'man_y': None}
        except Exception: pass 
            
    if len(materials) < 3: 
        fallback = [(1200, 1400, "Re-Use", 85.0), (2000, 2100, "Neu", 350.0), (800, 600, "Re-Use", 40.0), (2500, 2500, "Re-Use", 150.0)]
        for w, h, cond, pr in fallback * 4:
            if not use_new and cond == "Neu": continue
            if not use_reuse and cond == "Re-Use": continue
            col = '#add8e6' if cond == "Neu" else '#4682b4'
            item_id = uuid.uuid4().hex
            pos_label = f"P{st.session_state['pos_counter']}"
            st.session_state['pos_counter'] += 1
            materials.append({'id': item_id, 'pos_label': pos_label, 'w': w, 'h': h, 'type': 'Fenster', 'color': col, 'price': pr, 'source': 'Notfall-Reserve', 'condition': cond, 'link': ''})
            st.session_state['item_states'][item_id] = {'visible': True, 'pinned': False, 'force': False, 'rotated': False, 'man_x': None, 'man_y': None}
    return materials

# --- ALGORITHMEN (KI Core) ---
def check_overlap(x, y, w, h, placed):
    for p in placed:
        if not (x + w <= p['x'] or x >= p['x'] + p['w'] or y + h <= p['y'] or y >= p['y'] + p['h']): return True
    return False

def pack_smart_cluster(wall_w, wall_h, items, allow_auto_rotate, symmetry, randomness, seed, lock_pinned):
    random.seed(seed)
    placed_items = []
    
    pinned_items = [i for i in items if st.session_state['item_states'][i['id']].get('pinned')]
    dynamic_items = [i for i in items if not st.session_state['item_states'][i['id']].get('pinned')]
    fixed_x, fixed_y = [], []
    
    for item in pinned_items:
        state = st.session_state['item_states'][item['id']]
        eff_w, eff_h = (item['h'], item['w']) if state.get('rotated') else (item['w'], item['h'])
        dyn_item = {**item, 'w': eff_w, 'h': eff_h, '_user_rotated': state.get('rotated'), 'is_pinned': True}
        
        target_x = max(0, min(state.get('man_x') or 0, wall_w - eff_w))
        target_y = max(0, min(state.get('man_y') or 0, wall_h - eff_h))
        
        if not check_overlap(target_x, target_y, eff_w, eff_h, placed_items):
            final_x, final_y = target_x, target_y
        else:
            best_x, best_y = target_x, target_y
            min_dist = float('inf')
            step = 50
            for r in range(0, wall_h - eff_h + 1, step):
                for c in range(0, wall_w - eff_w + 1, step):
                    if not check_overlap(c, r, eff_w, eff_h, placed_items):
                        dist = (c - target_x)**2 + (r - target_y)**2
                        if dist < min_dist:
                            min_dist = dist
                            best_x, best_y = c, r
            final_x, final_y = best_x, best_y
            
        placed_items.append({**dyn_item, 'x': final_x, 'y': final_y})
        fixed_x.append(final_x + eff_w / 2)
        fixed_y.append(final_y + eff_h / 2)
        
        if lock_pinned:
            st.session_state['item_states'][item['id']]['man_x'] = final_x
            st.session_state['item_states'][item['id']]['man_y'] = final_y
            
    cx = sum(fixed_x)/len(fixed_x) if fixed_x else wall_w / 2
    cy = sum(fixed_y)/len(fixed_y) if fixed_y else wall_h / 2
            
    forced_items = [i for i in dynamic_items if st.session_state['item_states'][i['id']]['force']]
    normal_items = [i for i in dynamic_items if not st.session_state['item_states'][i['id']]['force']]
    
    for it in normal_items:
        noise = random.uniform(1.0 - (randomness/100), 1.0 + (randomness/100))
        it['_weight'] = (it['w'] * it['h']) * noise
        if symmetry: it['_weight'] = (it['w'] * 1000 + it['h']) * noise
            
    normal_items = sorted(normal_items, key=lambda i: i['_weight'], reverse=True)
    pack_list = forced_items + normal_items
    step = 200 if wall_w > 15000 or wall_h > 15000 else 100
    
    for item in pack_list: 
        state = st.session_state['item_states'][item['id']]
        eff_w, eff_h = (item['h'], item['w']) if state.get('rotated') else (item['w'], item['h'])
        dyn_item = {**item, 'w': eff_w, 'h': eff_h, '_user_rotated': state.get('rotated'), 'is_pinned': False}
        
        best_pos = None
        min_score = float('inf')
        
        for y in range(0, wall_h - min(dyn_item['w'], dyn_item['h']) + 1, step):
            for x in range(0, wall_w - min(dyn_item['w'], dyn_item['h']) + 1, step):
                fits_orig = not check_overlap(x, y, dyn_item['w'], dyn_item['h'], placed_items) if x + dyn_item['w'] <= wall_w and y + dyn_item['h'] <= wall_h else False
                fits_rot = not check_overlap(x, y, dyn_item['h'], dyn_item['w'], placed_items) if allow_auto_rotate and not dyn_item['_user_rotated'] and x + dyn_item['h'] <= wall_w and y + dyn_item['w'] <= wall_h else False
                        
                if fits_orig or fits_rot:
                    cx_orig, cy_orig = x + dyn_item['w']/2, y + dyn_item['h']/2
                    dist_orig = (cx_orig - cx)**2 + (cy_orig - cy)**2 if fits_orig else float('inf')
                    
                    cx_rot, cy_rot = x + dyn_item['h']/2, y + dyn_item['w']/2
                    dist_rot = (cx_rot - cx)**2 + (cy_rot - cy)**2 if fits_rot else float('inf')
                    
                    if symmetry:
                        if fits_orig: dist_orig += min(abs(cx_orig - cx), abs(cy_orig - cy)) * 5000
                        if fits_rot: dist_rot += min(abs(cx_rot - cx), abs(cy_rot - cy)) * 5000
                    if randomness > 0:
                        dist_orig *= random.uniform(1.0, 1.0 + (randomness/50))
                        dist_rot *= random.uniform(1.0, 1.0 + (randomness/50))
                    
                    if dist_orig < min_score and dist_orig <= dist_rot:
                        min_score = dist_orig
                        best_pos = {**dyn_item, 'x': x, 'y': y}
                    elif dist_rot < min_score:
                        min_score = dist_rot
                        best_pos = {**dyn_item, 'x': x, 'y': y, 'w': dyn_item['h'], 'h': dyn_item['w']} 
        if best_pos:
            placed_items.append(best_pos)
            
    if placed_items and not fixed_x:
        min_x, max_x = min(p['x'] for p in placed_items), max(p['x'] + p['w'] for p in placed_items)
        min_y, max_y = min(p['y'] for p in placed_items), max(p['y'] + p['h'] for p in placed_items)
        shift_x, shift_y = int((wall_w - (max_x - min_x)) / 2) - min_x, int((wall_h - (max_y - min_y)) / 2) - min_y
        for p in placed_items: 
            p['x'] += shift_x
            p['y'] += shift_y
            
    return placed_items

# ALGORITHMUS: Exakter Zuschnitt (Ohne Überlappung)
def calculate_gaps_exact(wall_w, wall_h, placed, toggle_dir):
    x_coords = {0, wall_w}
    y_coords = {0, wall_h}
    for p in placed:
        x_coords.add(p['x']); x_coords.add(p['x'] + p['w'])
        y_coords.add(p['y']); y_coords.add(p['y'] + p['h'])

    xs = sorted(list(x_coords)); ys = sorted(list(y_coords))
    grid = np.zeros((len(ys)-1, len(xs)-1), dtype=bool)

    for p in placed:
        xi1, xi2 = xs.index(p['x']), xs.index(p['x'] + p['w'])
        yi1, yi2 = ys.index(p['y']), ys.index(p['y'] + p['h'])
        grid[yi1:yi2, xi1:xi2] = True

    gaps = []
    for r in range(len(ys)-1):
        for c in range(len(xs)-1):
            if not grid[r, c]:
                if toggle_dir:
                    ch = 0
                    while r + ch < len(ys)-1 and not grid[r + ch, c]: ch += 1
                    cw, valid = 0, True
                    while c + cw < len(xs)-1 and valid:
                        for ir in range(r, r + ch):
                            if grid[ir, c + cw]: valid = False; break
                        if valid: cw += 1
                    grid[r:r+ch, c:c+cw] = True
                    gaps.append({'id': uuid.uuid4().hex, 'x': xs[c], 'y': ys[r], 'w': xs[c+cw]-xs[c], 'h': ys[r+ch]-ys[r], 'type': T["fill"], 'color': '#ff4d4d', 'price': 0.0, 'source': 'Holz/Metall', 'condition': 'Neu', 'link': ''})
                else:
                    cw = 0
                    while c + cw < len(xs)-1 and not grid[r, c + cw]: cw += 1
                    ch, valid = 0, True
                    while r + ch < len(ys)-1 and valid:
                        for ic in range(c, c + cw):
                            if grid[r + ch, ic]: valid = False; break
                        if valid: ch += 1
                    grid[r:r+ch, c:c+cw] = True
                    gaps.append({'id': uuid.uuid4().hex, 'x': xs[c], 'y': ys[r], 'w': xs[c+cw]-xs[c], 'h': ys[r+ch]-ys[r], 'type': T["fill"], 'color': '#ff4d4d', 'price': 0.0, 'source': 'Holz/Metall', 'condition': 'Neu', 'link': ''})
    return gaps

# --- UI: SIDEBAR ---
with st.sidebar:
    st.header(T["search_header"])
    land = st.selectbox(T["country"], ["Deutschland", "Österreich", "Schweiz", "España"])
    plz = st.text_input(T["zip"], "10115")
    radius = st.slider(T["radius"], 0, 100, 50, 10)
    
    use_reuse = st.checkbox(T["reuse"], value=True)
    use_new = st.checkbox(T["new"], value=False)
    
    if st.button(T["search_btn"], type="primary"):
        with st.spinner("..."):
            st.session_state['inventory'] = harvest_materials(land, plz, radius, use_reuse, use_new)
            st.session_state['is_loaded'] = True
        st.rerun()

    st.divider()
    st.header(T["custom_header"])
    colA, colB = st.columns(2)
    with colA: cw_w = st.number_input(T["width"], 300, 30000, 1000, step=100, key="cw_w_in")
    with colB: cw_h = st.number_input(T["height"], 300, 30000, 1200, step=100, key="cw_h_in")
    if st.button(T["add_btn"]):
        item_id = uuid.uuid4().hex
        pos_label = f"P{st.session_state['pos_counter']}"
        st.session_state['pos_counter'] += 1
        st.session_state['custom_windows'].append({
            'id': item_id, 'pos_label': pos_label, 'w': int(st.session_state.cw_w_in), 'h': int(st.session_state.cw_h_in), 'type': 'Fenster', 'color': '#90EE90', 'price': 0.0, 'source': 'Eigenbestand', 'condition': 'Eigen', 'link': ''
        })
        st.session_state['item_states'][item_id] = {'visible': True, 'pinned': False, 'force': True, 'rotated': False, 'man_x': None, 'man_y': None}
        st.rerun()
        
# --- UI: HAUPTBEREICH ---
if st.session_state['is_loaded'] or len(st.session_state['custom_windows']) > 0:
    total_inventory = st.session_state['custom_windows'] + st.session_state['inventory']
    usable_inventory = [item for item in total_inventory if st.session_state['item_states'].get(item['id'], {}).get('visible') == True]
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader(T["wall_header"])
        
        c_sli1, c_num1 = st.columns([2, 1])
        c_sli1.slider("B", 1000, 30000, value=st.session_state.w_val, step=100, key="w_sli", on_change=sync_w_sli, label_visibility="collapsed")
        c_num1.number_input("B", 1000, 30000, value=st.session_state.w_val, step=100, key="w_num", on_change=sync_w_num, label_visibility="collapsed")
        
        c_sli2, c_num2 = st.columns([2, 1])
        c_sli2.slider("H", 1000, 30000, value=st.session_state.h_val, step=100, key="h_sli", on_change=sync_h_sli, label_visibility="collapsed")
        c_num2.number_input("H", 1000, 30000, value=st.session_state.h_val, step=100, key="h_num", on_change=sync_h_num, label_visibility="collapsed")
        
        wall_width = st.session_state.w_val
        wall_height = st.session_state.h_val
        
        st.divider()
        st.markdown("**Design-Parameter**")
        auto_rotate = st.checkbox(T["auto_rotate"], value=True)
        lock_pinned = st.checkbox(T["lock_pinned"], value=True)
        symmetry = st.checkbox(T["symmetry"], value=False)
        chaos_val = st.slider(T["chaos"], 0, 100, 10, 5)
        
        st.button(T["shuffle_btn"], on_click=shuffle_layout, type="primary", use_container_width=True)
        st.divider()
        st.button(T["opt_gaps_btn"], on_click=optimize_gaps, use_container_width=True)

    with col2:
        placed = pack_smart_cluster(wall_width, wall_height, usable_inventory, allow_auto_rotate=auto_rotate, symmetry=symmetry, randomness=chaos_val, seed=st.session_state['layout_seed'], lock_pinned=lock_pinned)
        gaps = calculate_gaps_exact(wall_width, wall_height, placed, toggle_dir=st.session_state['gap_toggle'])
        
        # --- GROSSES DASHBOARD ---
        total_price = sum(p['price'] for p in placed)
        wall_area_m2 = (wall_width * wall_height) / 1000000
        win_area_m2 = sum((p['w'] * p['h'])/1000000 for p in placed)
        win_pct = (win_area_m2 / wall_area_m2 * 100) if wall_area_m2 > 0 else 0
        
        st.markdown("### 📊 Live-Kalkulation")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric(T["wall_area"], f"{wall_area_m2:.2f} m²")
        m_col2.metric(T["win_area"], f"{win_area_m2:.2f} m²")
        m_col3.metric(T["fill_rate"], f"{win_pct:.1f} %")
        m_col4.metric(T["price_total"], f"{total_price:.2f} €")
        
        # --- ECHTE BIDIREKTIONALE DRAG & DROP KOMPONENTE ---
        scale = 800 / max(wall_width, 1)
        
        js_placed = []
        for p in placed:
            js_placed.append({
                "id": p['id'], "label": p['pos_label'], "color": p['color'],
                "x": p['x'], "y": p['y'], "w": p['w'], "h": p['h'],
                "is_pinned": p.get('is_pinned', False)
            })

        js_gaps = []
        for g in gaps:
            js_gaps.append({"w": g['w'], "h": g['h'], "x": g['x'], "y": g['y']})

        # Aufruf der magischen Custom Component
        component_result = interactive_canvas(
            windows=js_placed, gaps=js_gaps, 
            wall_w=wall_width, wall_h=wall_height, scale=scale, 
            key="canvas"
        )
        
        # WENN JAVASCRIPT EIN SIGNAL SENDET (Drag, Pin, Rotate)
        if component_result and component_result.get("ts", 0) > st.session_state.last_ts:
            st.session_state.last_ts = component_result["ts"]
            act = component_result["action"]
            item_id = component_result["id"]
            state = st.session_state['item_states'].get(item_id)
            
            if state:
                if act == "rotate":
                    state['rotated'] = not state.get('rotated', False)
                elif act == "pin":
                    state['pinned'] = not state.get('pinned', False)
                    if state['pinned']:
                        state['man_x'] = component_result["x"]
                        state['man_y'] = component_result["y"]
                    else:
                        state['man_x'] = None; state['man_y'] = None
                elif act == "move":
                    state['man_x'] = component_result["x"]
                    state['man_y'] = component_result["y"]
                    state['pinned'] = True
            st.rerun()

    # ==========================================
    # --- TABELLE 1: FENSTER MATRIX ---
    # ==========================================
    st.divider()
    st.subheader(T["matrix_header"])
    df_win_data = []
    
    placed_dict = {p['id']: p for p in placed}
    total_inventory = sorted(total_inventory, key=lambda x: int(x['pos_label'][1:]))
    
    for item in total_inventory:
        state = st.session_state['item_states'].get(item['id'])
        status = ""
        if not state['visible']:
            status = "🙈"
            disp_w, disp_h = (item['h'], item['w']) if state['rotated'] else (item['w'], item['h'])
        elif item['id'] in placed_dict:
            disp_w, disp_h = placed_dict[item['id']]['w'], placed_dict[item['id']]['h']
            if disp_w == item['h'] and disp_h == item['w'] and item['w'] != item['h'] and not state['rotated']: status = "✅ 🔄" 
            else: status = "✅"
            if state.get('pinned'): status = "📌"
        else:
            status = "❌"
            disp_w, disp_h = (item['h'], item['w']) if state['rotated'] else (item['w'], item['h'])
            
        area_m2 = (disp_w * disp_h) / 1000000
        df_win_data.append({
            "id": item['id'], "_color": item['color'], T["col_layer"]: state['visible'], T["col_pin"]: state.get('pinned', False), 
            "📍 Man X": state.get('man_x'), "📍 Man Y": state.get('man_y'), T["col_rotate"]: state.get('rotated', False), 
            T["col_force"]: state['force'], "Pos": item['pos_label'], T["col_status"]: status, T["col_dim"]: f"{disp_w} x {disp_h}",
            T["col_area"]: f"{area_m2:.2f}", T["col_type"]: item['type'], T["col_price"]: f"{item['price']:.2f} €", T["col_link"]: item['link']
        })
        
    df_win = pd.DataFrame(df_win_data)
    df_win.set_index('id', inplace=True) 
    def highlight_windows(row):
        stat = str(row[T['col_status']]); color_hex = str(row['_color'])
        if '✅' in stat: return [f'background-color: {color_hex}66'] * len(row) 
        if '📌' in stat: return ['background-color: rgba(255, 193, 7, 0.4)'] * len(row) 
        if '🙈' in stat: return ['background-color: rgba(128, 128, 128, 0.2); color: gray'] * len(row)
        return [''] * len(row)
        
    edited_df = st.data_editor(
        df_win.style.apply(highlight_windows, axis=1), 
        column_config={
            "_color": None, T["col_layer"]: st.column_config.CheckboxColumn(T["col_layer"]),
            T["col_pin"]: st.column_config.CheckboxColumn(T["col_pin"]),
            "📍 Man X": st.column_config.NumberColumn("📍 Man X"),
            "📍 Man Y": st.column_config.NumberColumn("📍 Man Y"), T["col_rotate"]: st.column_config.CheckboxColumn(T["col_rotate"]),
            T["col_force"]: st.column_config.CheckboxColumn(T["col_force"]),
            T["col_link"]: st.column_config.LinkColumn(T["col_link"], display_text="Link 🔗")
        },
        disabled=[T["col_type"], "Pos", T["col_status"], T["col_dim"], T["col_area"], T["col_price"], T["col_link"]], 
        use_container_width=True, key="windows_editor"
    )
    
    changes_made = False
    for item_id, row in edited_df.iterrows():
        if item_id in st.session_state['item_states']:
            state = st.session_state['item_states'][item_id]
            new_vis = bool(row[T['col_layer']]); new_rot = bool(row[T['col_rotate']]); new_fce = bool(row[T['col_force']]); new_pin = bool(row[T['col_pin']])
            new_mx = None if pd.isna(row['📍 Man X']) else int(row['📍 Man X']); new_my = None if pd.isna(row['📍 Man Y']) else int(row['📍 Man Y'])
            
            if new_pin != state.get('pinned', False):
                state['pinned'] = new_pin
                if new_pin: 
                    curr_x = placed_dict[item_id]['x'] if item_id in placed_dict else 0
                    curr_y = placed_dict[item_id]['y'] if item_id in placed_dict else 0
                    state['man_x'] = curr_x; state['man_y'] = curr_y
                else: 
                    state['man_x'] = None; state['man_y'] = None
                changes_made = True
            elif new_mx != state.get('man_x') or new_my != state.get('man_y'):
                state['man_x'] = new_mx; state['man_y'] = new_my
                state['pinned'] = True if (new_mx is not None or new_my is not None) else False
                changes_made = True
            elif new_vis != state['visible'] or new_rot != state.get('rotated', False) or new_fce != state['force']:
                state['visible'] = new_vis; state['rotated'] = new_rot; state['force'] = new_fce
                changes_made = True
    if changes_made: st.rerun()

    # ==========================================
    # --- EXPORT & ZUSCHNITT MATRIX ---
    # ==========================================
    st.divider()
    export_data = df_win[(df_win[T['col_status']].str.contains('✅')) | (df_win[T['col_status']].str.contains('📌'))].copy()
    df_gaps_data = []
    for g in gaps:
        area_m2 = (g['w'] * g['h']) / 1000000
        df_gaps_data.append({T["col_type"]: T["fill"], "Pos": "Gap", T["col_status"]: "⚠️", T["col_dim"]: f"{g['w']} x {g['h']}", T["col_area"]: f"{area_m2:.2f}", T["col_source"]: g['source'], T["col_price"]: "-"})
    df_gaps = pd.DataFrame(df_gaps_data)
    final_export_df = pd.concat([export_data, df_gaps], ignore_index=True)
    final_export_df = final_export_df.drop(columns=['_color', T['col_layer'], T['col_pin'], T['col_rotate'], '📍 Man X', '📍 Man Y', T['col_force']], errors='ignore')
    csv = final_export_df.to_csv(index=False).encode('utf-8')
    st.download_button(label=T["export_btn"], data=csv, file_name='stueckliste.csv', mime='text/csv', type="primary")
    
    st.subheader(T["gaps_header"])
    if not df_gaps.empty: st.dataframe(df_gaps[[T["col_type"], T["col_dim"], T["col_area"], T["col_source"]]], hide_index=True, use_container_width=True)
    else: st.success(T["no_gaps"])
else:
    st.info("👈 " + T["search_header"])
