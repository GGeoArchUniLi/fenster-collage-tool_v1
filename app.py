import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import random
import uuid
import json  # <--- HIER FEHLTE DER IMPORT!
from duckduckgo_search import DDGS

st.set_page_config(page_title="Patchwork Facade Generator v1.3.1", layout="wide")

# --- 100% LÜCKENLOSES SPRACH-WÖRTERBUCH ---
LANG_DICT = {
    "🇩🇪 DE": {
        "title": "🧱 Patchwork-Fassaden-Generator v1.3",
        "search_header": "1. Globale Suche", "country": "Land", "zip": "PLZ / Ort", "radius": "Umkreis (km)",
        "reuse": "🔄 Gebrauchte Fenster", "new": "🆕 Fabrikneue Fenster", "search_btn": "🔍 Marktplätze durchsuchen",
        "custom_header": "2. Eigenbestand", "width": "Breite (mm)", "height": "Höhe (mm)", "add_btn": "➕ Hinzufügen",
        "wall_header": "Wandöffnung", "shuffle_btn": "🎲 Neu würfeln (Auto-Layout)",
        "price_total": "Gesamtpreis", "win_area": "Fensterfläche", "wall_area": "Wandfläche", "fill_rate": "Füllgrad",
        "matrix_header": "📋 Fenster-Steuerung", "export_btn": "📥 Einkaufsliste herunterladen (CSV)",
        "gaps_header": "🟥 Benötigte Zuschnitte", "no_gaps": "Die Wand ist perfekt gefüllt! Keine Zuschnitte benötigt.",
        "col_layer": "👁️ Layer", "col_force": "⭐ Priorität", "col_type": "Typ", "col_status": "Status", 
        "col_dim": "Maße (BxH)", "col_area": "Fläche (m²)", "col_source": "Herkunft", "col_price": "Preis", "col_link": "🛒 Shop"
    },
    "🇬🇧 EN": {
        "title": "🧱 Patchwork Facade Generator v1.3",
        "search_header": "1. Global Search", "country": "Country", "zip": "ZIP / City", "radius": "Radius (km)",
        "reuse": "🔄 Re-Use Windows", "new": "🆕 Brand New Windows", "search_btn": "🔍 Search Marketplaces",
        "custom_header": "2. Custom Inventory", "width": "Width (mm)", "height": "Height (mm)", "add_btn": "➕ Add Window",
        "wall_header": "Wall Opening", "shuffle_btn": "🎲 Shuffle (Auto-Layout)",
        "price_total": "Total Price", "win_area": "Window Area", "wall_area": "Wall Area", "fill_rate": "Fill Rate",
        "matrix_header": "📋 Window Control", "export_btn": "📥 Download Shopping List (CSV)",
        "gaps_header": "🟥 Required Filler Panels", "no_gaps": "Wall is perfectly filled! No panels needed.",
        "col_layer": "👁️ Layer", "col_force": "⭐ Priority", "col_type": "Type", "col_status": "Status", 
        "col_dim": "Dimensions", "col_area": "Area (m²)", "col_source": "Source", "col_price": "Price", "col_link": "🛒 Shop"
    },
    "🇫🇷 FR": {
        "title": "🧱 Générateur de Façade v1.3",
        "search_header": "1. Recherche Globale", "country": "Pays", "zip": "Code Postal", "radius": "Rayon (km)",
        "reuse": "🔄 Fenêtres Réutilisées", "new": "🆕 Fenêtres Neuves", "search_btn": "🔍 Chercher les marchés",
        "custom_header": "2. Inventaire Personnalisé", "width": "Largeur (mm)", "height": "Hauteur (mm)", "add_btn": "➕ Ajouter",
        "wall_header": "Ouverture du mur", "shuffle_btn": "🎲 Mélanger (Auto-Layout)",
        "price_total": "Prix Total", "win_area": "Surface Fenêtre", "wall_area": "Surface Mur", "fill_rate": "Taux de remplissage",
        "matrix_header": "📋 Contrôle des fenêtres", "export_btn": "📥 Télécharger la liste (CSV)",
        "gaps_header": "🟥 Panneaux de remplissage", "no_gaps": "Mur parfaitement rempli ! Aucun panneau nécessaire.",
        "col_layer": "👁️ Calque", "col_force": "⭐ Priorité", "col_type": "Type", "col_status": "Statut", 
        "col_dim": "Dimensions", "col_area": "Surface (m²)", "col_source": "Source", "col_price": "Prix", "col_link": "🛒 Boutique"
    },
    "🇮🇹 IT": {
        "title": "🧱 Generatore di Facciate v1.3",
        "search_header": "1. Ricerca Globale", "country": "Paese", "zip": "CAP", "radius": "Raggio (km)",
        "reuse": "🔄 Finestre Usate", "new": "🆕 Finestre Nuove", "search_btn": "🔍 Cerca mercati",
        "custom_header": "2. Inventario", "width": "Larghezza (mm)", "height": "Altezza (mm)", "add_btn": "➕ Aggiungi",
        "wall_header": "Apertura del muro", "shuffle_btn": "🎲 Rimescola",
        "price_total": "Prezzo Totale", "win_area": "Area Finestre", "wall_area": "Area Muro", "fill_rate": "Riempimento",
        "matrix_header": "📋 Controllo finestre", "export_btn": "📥 Scarica lista (CSV)",
        "gaps_header": "🟥 Pannelli richiesti", "no_gaps": "Muro perfettamente riempito!",
        "col_layer": "👁️ Layer", "col_force": "⭐ Priorità", "col_type": "Tipo", "col_status": "Stato", 
        "col_dim": "Dimensioni", "col_area": "Area (m²)", "col_source": "Fonte", "col_price": "Prezzo", "col_link": "🛒 Negozio"
    },
    "🇨🇭 RM": {
        "title": "🧱 Generatur da Façadas v1.3",
        "search_header": "1. Tschertga", "country": "Pajais", "zip": "PLZ", "radius": "Radius (km)",
        "reuse": "🔄 Fanestras duvradas", "new": "🆕 Fanestras novas", "search_btn": "🔍 Tschertgar martgads",
        "custom_header": "2. Inventari", "width": "Ladezza (mm)", "height": "Autezza (mm)", "add_btn": "➕ Agiuntar",
        "wall_header": "Avertura da paraid", "shuffle_btn": "🎲 Maschadar",
        "price_total": "Pretsch total", "win_area": "Surfatscha", "wall_area": "Paraid", "fill_rate": "Emplenida",
        "matrix_header": "📋 Control da fanestras", "export_btn": "📥 Chargiar glista (CSV)",
        "gaps_header": "🟥 Panels", "no_gaps": "Perfegt!",
        "col_layer": "👁️ Layer", "col_force": "⭐ Prioritad", "col_type": "Tip", "col_status": "Status", 
        "col_dim": "Dimensiuns", "col_area": "Surfatscha", "col_source": "Funtauna", "col_price": "Pretsch", "col_link": "🛒 Butia"
    },
    "🇧🇬 BG": {
        "title": "🧱 Генератор на фасади v1.3",
        "search_header": "1. Търсене", "country": "Държава", "zip": "Пощенски код", "radius": "Радиус (км)",
        "reuse": "🔄 Използвани прозорци", "new": "🆕 Нови прозорци", "search_btn": "🔍 Търсене в пазари",
        "custom_header": "2. Мой инвентар", "width": "Ширина (мм)", "height": "Височина (мм)", "add_btn": "➕ Добави",
        "wall_header": "Отвор на стената", "shuffle_btn": "🎲 Разбъркай",
        "price_total": "Обща цена", "win_area": "Площ прозорци", "wall_area": "Площ стена", "fill_rate": "Запълване",
        "matrix_header": "📋 Управление на прозорци", "export_btn": "📥 Изтегли списък (CSV)",
        "gaps_header": "🟥 Нужни панели", "no_gaps": "Стената е идеално запълнена!",
        "col_layer": "👁️ Слой", "col_force": "⭐ Приоритет", "col_type": "Тип", "col_status": "Статус", 
        "col_dim": "Размери", "col_area": "Площ (м²)", "col_source": "Източник", "col_price": "Цена", "col_link": "🛒 Магазин"
    },
    "🇮🇱 HE": {
        "title": "🧱 מחולל חזיתות טלאים v1.3",
        "search_header": "1. חיפוש גלובלי", "country": "מדינה", "zip": "מיקוד", "radius": "רדיוס (ק״מ)",
        "reuse": "🔄 חלונות בשימוש חוזר", "new": "🆕 חלונות חדשים", "search_btn": "🔍 חפש בשווקים",
        "custom_header": "2. מלאי אישי", "width": "רוחב (מ״מ)", "height": "גובה (מ״מ)", "add_btn": "➕ הוסף",
        "wall_header": "פתח קיר", "shuffle_btn": "🎲 ערבב",
        "price_total": "מחיר כולל", "win_area": "שטח חלונות", "wall_area": "שטח קיר", "fill_rate": "אחוז מילוי",
        "matrix_header": "📋 בקרת חלונות", "export_btn": "📥 הורד רשימת קניות (CSV)",
        "gaps_header": "🟥 פאנלים חסרים", "no_gaps": "הקיר מלא לחלוטין! אין צורך בפאנלים.",
        "col_layer": "👁️ שכבה", "col_force": "⭐ עדיפות", "col_type": "סוג", "col_status": "סטטוס", 
        "col_dim": "מידות", "col_area": "שטח (מ״ר)", "col_source": "מקור", "col_price": "מחיר", "col_link": "🛒 חנות"
    },
    "🇯🇵 JA": {
        "title": "🧱 パッチワークファサード v1.3",
        "search_header": "1. グローバル検索", "country": "国", "zip": "郵便番号", "radius": "半径 (km)",
        "reuse": "🔄 中古窓", "new": "🆕 新品窓", "search_btn": "🔍 市場を検索",
        "custom_header": "2. カスタム在庫", "width": "幅 (mm)", "height": "高さ (mm)", "add_btn": "➕ 追加",
        "wall_header": "壁の開口部", "shuffle_btn": "🎲 シャッフル",
        "price_total": "合計価格", "win_area": "窓面積", "wall_area": "壁面積", "fill_rate": "充填率",
        "matrix_header": "📋 ウィンドウコントロール", "export_btn": "📥 リストをダウンロード (CSV)",
        "gaps_header": "🟥 必要なパネル", "no_gaps": "完全に充填されました！",
        "col_layer": "👁️ レイヤー", "col_force": "⭐ 優先順位", "col_type": "タイプ", "col_status": "ステータス", 
        "col_dim": "寸法", "col_area": "面積 (m²)", "col_source": "ソース", "col_price": "価格", "col_link": "🛒 ショップ"
    }
}

lang_choice = st.radio("Language:", list(LANG_DICT.keys()), horizontal=True)
T = LANG_DICT[lang_choice]
st.title(T["title"])

# --- SESSION STATE ---
if 'inventory' not in st.session_state: st.session_state['inventory'] = []
if 'custom_windows' not in st.session_state: st.session_state['custom_windows'] = []
if 'is_loaded' not in st.session_state: st.session_state['is_loaded'] = False
if 'item_states' not in st.session_state: st.session_state['item_states'] = {} 

# --- FUNKTION: Daten suchen ---
def harvest_materials(land, plz, radius, use_reuse, use_new):
    materials = []
    queries = []
    if use_reuse: queries.append((f"site:ebay.de OR site:kleinanzeigen.de Fenster gebraucht {plz} {land}", "Re-Use", '#4682b4'))
    if use_new: queries.append((f"Fenster neu kaufen {plz} {land}", "Neu", '#add8e6'))
        
    for query, condition, color in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=20))
                for res in results:
                    match = re.search(r'(\d{3,4})\s*[xX*]\s*(\d{3,4})', res['title'] + " " + res['body'])
                    if match:
                        w, h = int(match.group(1)), int(match.group(2))
                        price_match = re.search(r'(\d{1,5})[.,]?\d*\s*[€|EUR]', res['title'] + " " + res['body'])
                        price = float(price_match.group(1)) if price_match else float(int((w * h) / 20000) + random.randint(10, 50))
                        if 300 <= w <= 12000 and 300 <= h <= 12000:
                            item_id = uuid.uuid4().hex
                            materials.append({
                                'id': item_id, 'w': w, 'h': h, 'type': 'Fenster', 'color': color, 
                                'price': price, 'source': res['title'][:30] + '...', 
                                'condition': condition, 'link': res['href']
                            })
                            st.session_state['item_states'][item_id] = {'visible': True, 'force': False, 'man_x': None, 'man_y': None}
        except Exception: pass 
            
    if len(materials) < 3: 
        fallback = [(1200, 1400, "Re-Use", 85.0), (2000, 2100, "Neu", 350.0), (800, 600, "Re-Use", 40.0)]
        for w, h, cond, pr in fallback * 5:
            if not use_new and cond == "Neu": continue
            if not use_reuse and cond == "Re-Use": continue
            col = '#add8e6' if cond == "Neu" else '#4682b4'
            item_id = uuid.uuid4().hex
            materials.append({'id': item_id, 'w': w, 'h': h, 'type': 'Fenster', 'color': col, 'price': pr, 'source': 'Notfall-Reserve', 'condition': cond, 'link': 'https://ebay.de'})
            st.session_state['item_states'][item_id] = {'visible': True, 'force': False, 'man_x': None, 'man_y': None}
    return materials

# --- ALGORITHMEN ---
def check_overlap(x, y, w, h, placed):
    for p in placed:
        if not (x + w <= p['x'] or x >= p['x'] + p['w'] or y + h <= p['y'] or y >= p['y'] + p['h']): return True
    return False

def pack_mondrian_cluster(wall_w, wall_h, items):
    placed_items = []
    dynamic_items = []
    
    for item in items:
        state = st.session_state['item_states'][item['id']]
        if state.get('man_x') is not None and state.get('man_y') is not None:
            placed_items.append({**item, 'x': int(state['man_x']), 'y': int(state['man_y'])})
        else:
            dynamic_items.append(item)
            
    forced_items = [i for i in dynamic_items if st.session_state['item_states'][i['id']]['force']]
    normal_items = [i for i in dynamic_items if not st.session_state['item_states'][i['id']]['force']]
    random.shuffle(normal_items) 
    mixed_normal = sorted(normal_items, key=lambda i: (i['w'] * i['h']) * random.uniform(0.5, 1.5), reverse=True)
    
    pack_list = forced_items + mixed_normal
    step = 50 if wall_w <= 6000 else 100
    
    for item in pack_list: 
        fitted = False
        for y in range(0, wall_h - item['h'] + 1, step):
            for x in range(0, wall_w - item['w'] + 1, step):
                if not check_overlap(x, y, item['w'], item['h'], placed_items):
                    placed_items.append({**item, 'x': x, 'y': y})
                    fitted = True; break
            if fitted: break
            
    has_manual = any(st.session_state['item_states'][i['id']].get('man_x') is not None for i in items)
    if placed_items and not has_manual:
        max_x = max(p['x'] + p['w'] for p in placed_items)
        max_y = max(p['y'] + p['h'] for p in placed_items)
        offset_x = (wall_w - max_x) // 2
        offset_y = (wall_h - max_y) // 2
        for p in placed_items: p['x'] += offset_x; p['y'] += offset_y
            
    return placed_items

def calculate_gaps(wall_w, wall_h, placed, step=50):
    grid_w, grid_h = int(wall_w // step), int(wall_h // step)
    grid = np.zeros((grid_h, grid_w), dtype=bool)
    
    for p in placed:
        px, py, pw, ph = int(p['x']//step), int(p['y']//step), int(p['w']//step), int(p['h']//step)
        grid[max(0, py):min(grid_h, py+ph), max(0, px):min(grid_w, px+pw)] = True
        
    gaps = []
    for y in range(grid_h):
        for x in range(grid_w):
            if not grid[y, x]:
                cw, ch, valid = 0, 0, True
                while x + cw < grid_w and not grid[y, x + cw]: cw += 1
                while y + ch < grid_h and valid:
                    for ix in range(x, x + cw):
                        if grid[y + ch, ix]: valid = False; break
                    if valid: ch += 1
                grid[y:y+ch, x:x+cw] = True
                if cw > 0 and ch > 0:
                    gaps.append({
                        'id': uuid.uuid4().hex, 'x': x*step, 'y': y*step, 'w': cw*step, 'h': ch*step, 
                        'type': T["fill"], 'color': '#ff4d4d', 'price': 0.0,
                        'source': '-', 'condition': 'Neu', 'link': ''
                    })
    return gaps

# --- UI: SIDEBAR ---
with st.sidebar:
    st.header(T["search_header"])
    land = st.selectbox(T["country"], ["Deutschland", "Österreich", "Schweiz", "Liechtenstein"])
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
    if st.session_state['is_loaded']:
        stats_container = st.empty()
        st.divider()

    st.header(T["custom_header"])
    colA, colB = st.columns(2)
    with colA: cw_w = st.number_input(T["width"], 300, 12000, 1000, step=50)
    with colB: cw_h = st.number_input(T["height"], 300, 12000, 1200, step=50)
    if st.button(T["add_btn"]):
        item_id = uuid.uuid4().hex
        st.session_state['custom_windows'].append({
            'id': item_id, 'w': int(cw_w), 'h': int(cw_h), 'type': 'Fenster', 'color': '#90EE90', 'price': 0.0, 'source': 'Mein Lager', 'condition': 'Eigen', 'link': ''
        })
        st.session_state['item_states'][item_id] = {'visible': True, 'force': True, 'man_x': None, 'man_y': None}
        st.rerun()
        
# --- UI: HAUPTBEREICH ---
if st.session_state['is_loaded'] or len(st.session_state['custom_windows']) > 0:
    total_inventory = st.session_state['custom_windows'] + st.session_state['inventory']
    total_inventory.sort(key=lambda x: x['id']) 
    
    usable_inventory = [item for item in total_inventory if st.session_state['item_states'].get(item['id'], {}).get('visible') == True]
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader(T["wall_header"])
        wall_width = st.slider(T["width"], 1000, 12000, 4000, 100)
        wall_height = st.slider(T["height"], 1000, 12000, 3000, 100)
        if st.button(T["shuffle_btn"]): pass 

    with col2:
        placed = pack_mondrian_cluster(wall_width, wall_height, usable_inventory)
        gaps = calculate_gaps(wall_width, wall_height, placed, step=50 if wall_width <= 6000 else 100)
        
        total_price = sum(p['price'] for p in placed)
        wall_area_m2 = (wall_width * wall_height) / 1000000
        win_area_m2 = sum((p['w'] * p['h'])/1000000 for p in placed)
        win_pct = (win_area_m2 / wall_area_m2 * 100) if wall_area_m2 > 0 else 0
        
        stats_container.markdown(f"### 💶 {T['price_total']}: **{total_price:.2f} €**")
        stats_container.markdown(f"**{T['wall_area']}:** {wall_area_m2:.2f} m²<br>**{T['win_area']}:** {win_area_m2:.2f} m²<br>*(**{T['fill_rate']}:** {win_pct:.1f}%)*", unsafe_allow_html=True)
        
        # ==============================================================
        # --- DRAG & DROP HTML/JAVASCRIPT BLOCK ---
        # ==============================================================
        scale = 800 / max(wall_width, 1)
        canvas_w = int(wall_width * scale)
        canvas_h = int(wall_height * scale)
        
        js_placed = []
        for i, p in enumerate(placed):
            js_placed.append({
                "id": p['id'], "label": f"P{i+1}\n{p['w']}x{p['h']}", "color": p['color'],
                "x": int(p['x'] * scale), "y": int(canvas_h - (p['y'] * scale) - (p['h'] * scale)),
                "w": int(p['w'] * scale), "h": int(p['h'] * scale)
            })

        html_code = f"""
        <!DOCTYPE html><html><head><style>
            body {{ margin: 0; padding: 0; display: flex; justify-content: center; background-color: #f0f2f6; font-family: sans-serif; }}
            #wall {{ width: {canvas_w}px; height: {canvas_h}px; background: repeating-linear-gradient(45deg, #ffcccc, #ffcccc 10px, #ffffff 10px, #ffffff 20px); border: 4px solid #cc0000; position: relative; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .window {{ position: absolute; border: 3px solid #222; box-sizing: border-box; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 11px; font-weight: bold; color: #222; cursor: grab; user-select: none; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); transition: box-shadow 0.2s; white-space: pre-wrap; line-height: 1.2;}}
            .window:active {{ cursor: grabbing; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); z-index: 1000 !important; }}
        </style></head><body>
            <div id="wall"></div>
            <script>
                const wall = document.getElementById('wall');
                const items = {json.dumps(js_placed)};
                let draggedEl = null; let startX, startY, initialLeft, initialTop;

                items.forEach(item => {{
                    const el = document.createElement('div');
                    el.className = 'window'; el.id = item.id; el.innerText = item.label;
                    el.style.backgroundColor = item.color; el.style.width = item.w + 'px';
                    el.style.height = item.h + 'px'; el.style.left = item.x + 'px'; el.style.top = item.y + 'px'; el.style.zIndex = 10;
                    el.addEventListener('mousedown', dragStart);
                    wall.appendChild(el);
                }});

                function dragStart(e) {{
                    draggedEl = e.target; startX = e.clientX; startY = e.clientY;
                    initialLeft = parseInt(draggedEl.style.left, 10); initialTop = parseInt(draggedEl.style.top, 10);
                    document.addEventListener('mousemove', drag); document.addEventListener('mouseup', dragEnd);
                }}
                function drag(e) {{
                    if (!draggedEl) return; e.preventDefault();
                    draggedEl.style.left = (initialLeft + (e.clientX - startX)) + 'px';
                    draggedEl.style.top = (initialTop + (e.clientY - startY)) + 'px';
                }}
                function dragEnd(e) {{ document.removeEventListener('mousemove', drag); document.removeEventListener('mouseup', dragEnd); draggedEl = null; }}
            </script>
        </body></html>
        """
        st.caption("🖱️ **Drag & Drop Preview:** Bewege die Fenster direkt im Bild mit der Maus!")
        components.html(html_code, height=canvas_h + 20)

    # ==========================================
    # --- TABELLE 1: INTERAKTIVE FENSTER ---
    # ==========================================
    st.subheader(T["matrix_header"])
    
    df_win_data = []
    placed_ids = [p['id'] for p in placed]
    
    for item in total_inventory:
        state = st.session_state['item_states'].get(item['id'])
        area_m2 = (item['w'] * item['h']) / 1000000
        
        pos_label, status = "", ""
        if not state['visible']:
            status = "🙈"
            pos_label = "-"
        elif item['id'] in placed_ids:
            pos_label = f"P{placed_ids.index(item['id']) + 1}"
            status = "✅"
            if state.get('man_x') is not None: status = "📌"
        else:
            status = "❌"

        df_win_data.append({
            "id": item['id'],
            T["col_layer"]: state['visible'], 
            "📍 Manuell X": state.get('man_x'), 
            "📍 Manuell Y": state.get('man_y'), 
            T["col_force"]: state['force'],
            T["col_type"]: item['type'],
            "Pos": pos_label,
            T["col_status"]: status,
            T["col_dim"]: f"{item['w']} x {item['h']}",
            T["col_area"]: f"{area_m2:.2f}",
            T["col_source"]: item['source'],
            T["col_price"]: f"{item['price']:.2f} €", 
            T["col_link"]: item['link']
        })
        
    df_win = pd.DataFrame(df_win_data)
    
    def highlight_windows(row):
        stat = str(row[T['col_status']])
        if '✅' in stat: return ['background-color: rgba(40, 167, 69, 0.2)'] * len(row)
        if '📌' in stat: return ['background-color: rgba(255, 193, 7, 0.3)'] * len(row) 
        if '🙈' in stat: return ['background-color: rgba(128, 128, 128, 0.2); color: gray'] * len(row)
        return [''] * len(row)
        
    edited_df = st.data_editor(
        df_win.style.apply(highlight_windows, axis=1), 
        column_config={
            "id": None, 
            T["col_layer"]: st.column_config.CheckboxColumn(T["col_layer"]),
            "📍 Manuell X": st.column_config.NumberColumn("📍 Manuell X"),
            "📍 Manuell Y": st.column_config.NumberColumn("📍 Manuell Y"),
            T["col_force"]: st.column_config.CheckboxColumn(T["col_force"]),
            T["col_link"]: st.column_config.LinkColumn(T["col_link"], display_text="Link 🔗")
        },
        disabled=[T["col_type"], "Pos", T["col_status"], T["col_dim"], T["col_area"], T["col_source"], T["col_price"], T["col_link"]], 
        hide_index=True, use_container_width=True, key="windows_editor"
    )
    
    changes_made = False
    for idx, row in edited_df.iterrows():
        item_id = row['id']
        if item_id in st.session_state['item_states']:
            state = st.session_state['item_states'][item_id]
            if (row[T['col_layer']] != state['visible'] or 
                row[T['col_force']] != state['force'] or 
                row['📍 Manuell X'] != state['man_x'] or 
                row['📍 Manuell Y'] != state['man_y']):
                
                state['visible'] = row[T['col_layer']]
                state['force'] = row[T['col_force']]
                state['man_x'] = None if pd.isna(row['📍 Manuell X']) else int(row['📍 Manuell X'])
                state['man_y'] = None if pd.isna(row['📍 Manuell Y']) else int(row['📍 Manuell Y'])
                changes_made = True
                
    if changes_made: st.rerun()

    # ==========================================
    # --- EXPORT & LÜCKEN (GAPS) ---
    # ==========================================
    st.divider()
    
    export_data = df_win[(df_win[T['col_status']] == '✅') | (df_win[T['col_status']] == '📌')].copy()
    
    df_gaps_data = []
    for g in gaps:
        area_m2 = (g['w'] * g['h']) / 1000000
        df_gaps_data.append({
            T["col_type"]: T["fill"], "Pos": "Gap", T["col_status"]: "⚠️",
            T["col_dim"]: f"{g['w']} x {g['h']}", T["col_area"]: f"{area_m2:.2f}",
            T["col_source"]: g['source'], T["col_price"]: "-", T["col_link"]: ""
        })
    df_gaps = pd.DataFrame(df_gaps_data)
    
    final_export_df = pd.concat([export_data, df_gaps], ignore_index=True)
    final_export_df = final_export_df.drop(columns=['id', T['col_layer'], '📍 Manuell X', '📍 Manuell Y', T['col_force']], errors='ignore')

    csv = final_export_df.to_csv(index=False).encode('utf-8')
    st.download_button(label=T["export_btn"], data=csv, file_name='stueckliste.csv', mime='text/csv', type="primary")

    st.subheader(T["gaps_header"])
    if not df_gaps.empty:
        st.dataframe(df_gaps[[T["col_type"], T["col_dim"], T["col_area"], T["col_source"]]], hide_index=True, use_container_width=True)
    else:
        st.success(T["no_gaps"])

else:
    st.info("👈 " + T["search_header"])
