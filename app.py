import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import random
import uuid
import json
from duckduckgo_search import DDGS

st.set_page_config(page_title="Patchwork Facade Generator v2.7", layout="wide")

# --- SPRACH-WÖRTERBUCH (Komplett inkl. Spanisch) ---
LANG_DICT = {
    "🇩🇪 DE": {
        "title": "🧱 Patchwork-Fassaden-Generator v2.7",
        "search_header": "1. Globale Suche", "country": "Land", "zip": "PLZ / Ort", "radius": "Umkreis (km)",
        "reuse": "🔄 Gebrauchte Fenster", "new": "🆕 Fabrikneue Fenster", "search_btn": "🔍 Marktplätze durchsuchen",
        "custom_header": "2. Eigenbestand", "width": "Breite (mm)", "height": "Höhe (mm)", "add_btn": "➕ Hinzufügen",
        "wall_header": "Wandöffnung (bis 30m)", "shuffle_btn": "🎲 Neu clustern (KI)", 
        "auto_rotate": "🔄 Auto-Rotation erlauben", "lock_pinned": "🔒 Gepinnte Positionen beim Clustern beibehalten",
        "symmetry": "📐 Symmetrisches Cluster", "chaos": "Varianz / Chaos (%)", "opt_gaps_btn": "✂️ Zuschnitte umschalten (H/V)",
        "price_total": "Gesamtpreis Fenster", "win_area": "Gesamtfläche Fenster", "wall_area": "Fläche Wandöffnung", "fill_rate": "Füllgrad",
        "matrix_header": "📋 Fenster-Steuerung & Docking", "export_btn": "📥 Einkaufsliste herunterladen (CSV)",
        "gaps_header": "🟥 Benötigte Zuschnitte (Exakt, ohne Überlappung)", "no_gaps": "Die Wand ist perfekt gefüllt! Keine Zuschnitte benötigt.",
        "fill": "Zuschnitt Panel",
        "col_layer": "👁️ Sichtbar", "col_pin": "📌 Pin", "col_rotate": "🔄 90°", "col_force": "⭐ Prio", "col_type": "Typ", "col_status": "Status", 
        "col_dim": "Maße (BxH)", "col_area": "Fläche (m²)", "col_source": "Herkunft", "col_price": "Preis", "col_link": "🛒 Shop"
    },
    "🇪🇸 ES": {
        "title": "🧱 Generador de Fachadas v2.7",
        "search_header": "1. Búsqueda Global", "country": "País", "zip": "C.P. / Ciudad", "radius": "Radio (km)",
        "reuse": "🔄 Ventanas Usadas", "new": "🆕 Ventanas Nuevas", "search_btn": "🔍 Buscar en mercados",
        "custom_header": "2. Inventario Propio", "width": "Ancho (mm)", "height": "Alto (mm)", "add_btn": "➕ Añadir",
        "wall_header": "Apertura (hasta 30m)", "shuffle_btn": "🎲 Reagrupar (IA)", 
        "auto_rotate": "🔄 Permitir auto-rotación", "lock_pinned": "🔒 Mantener posiciones fijadas",
        "symmetry": "📐 Clúster Simétrico", "chaos": "Varianza / Caos (%)", "opt_gaps_btn": "✂️ Alternar cortes (H/V)",
        "price_total": "Precio Total", "win_area": "Área de Ventanas", "wall_area": "Área de Apertura", "fill_rate": "Tasa de relleno",
        "matrix_header": "📋 Matriz de Control", "export_btn": "📥 Descargar lista (CSV)",
        "gaps_header": "🟥 Paneles de Relleno Requeridos", "no_gaps": "¡El muro está perfectamente lleno!",
        "fill": "Panel de corte",
        "col_layer": "👁️ Visible", "col_pin": "📌 Fijar", "col_rotate": "🔄 90°", "col_force": "⭐ Prio", "col_type": "Tipo", "col_status": "Estado", 
        "col_dim": "Dimensiones", "col_area": "Área (m²)", "col_source": "Origen", "col_price": "Precio", "col_link": "🛒 Tienda"
    }
}
# Fallback für die anderen Sprachen, hier der Übersichtlichkeit halber abgekürzt, wir laden das DE/ES dict.
lang_choice = st.radio("Sprache / Idioma:", ["🇩🇪 DE", "🇪🇸 ES"], horizontal=True)
T = LANG_DICT[lang_choice]
st.title(T["title"])

# --- SESSION STATES INITIALISIERUNG ---
if 'inventory' not in st.session_state: st.session_state['inventory'] = []
if 'custom_windows' not in st.session_state: st.session_state['custom_windows'] = []
if 'is_loaded' not in st.session_state: st.session_state['is_loaded'] = False
if 'item_states' not in st.session_state: st.session_state['item_states'] = {} 
if 'pos_counter' not in st.session_state: st.session_state['pos_counter'] = 1 
if 'layout_seed' not in st.session_state: st.session_state['layout_seed'] = 42 
if 'gap_toggle' not in st.session_state: st.session_state['gap_toggle'] = False

# --- SLIDER SYNCHRONISATION ---
if 'w_sli' not in st.session_state: st.session_state.w_sli = 4000
if 'w_num' not in st.session_state: st.session_state.w_num = 4000
if 'h_sli' not in st.session_state: st.session_state.h_sli = 3000
if 'h_num' not in st.session_state: st.session_state.h_num = 3000

def sync_w_from_sli(): st.session_state.w_num = st.session_state.w_sli
def sync_w_from_num(): st.session_state.w_sli = st.session_state.w_num
def sync_h_from_sli(): st.session_state.h_num = st.session_state.h_sli
def sync_h_from_num(): st.session_state.h_sli = st.session_state.h_num

def shuffle_layout(): st.session_state['layout_seed'] = random.randint(1, 10000)
def optimize_gaps(): st.session_state['gap_toggle'] = not st.session_state['gap_toggle']

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

# --- ALGORITHMEN ---
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
    
    # 1. Gepinnte Elemente setzen (mit Bounds & KI Overlap Check)
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
    
    # 2. Dynamische Elemente platzieren
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

# ALGORITHMUS: Exakter Sweep-Line Zuschnitt (Ohne Lücken, ohne Überlappung)
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
    if st.session_state['is_loaded']:
        # KOMPAKTE STATS IN DER SIDEBAR (Preis ist da!)
        st.header("📊 Info")
        stats_container = st.empty()
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
            'id': item_id, 'pos_label': pos_label, 'w': int(st.session_state.cw_w_in), 'h': int(st.session_state.cw_h_in), 'type': 'Fenster', 'color': '#90EE90', 'price': 0.0, 'source': 'Lager', 'condition': 'Eigen', 'link': ''
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
        c_sli1.slider("B", 1000, 30000, key="w_sli", on_change=sync_w_from_sli, label_visibility="collapsed")
        c_num1.number_input("B", 1000, 30000, key="w_num", on_change=sync_w_from_num, label_visibility="collapsed")
        
        c_sli2, c_num2 = st.columns([2, 1])
        c_sli2.slider("H", 1000, 30000, key="h_sli", on_change=sync_h_from_sli, label_visibility="collapsed")
        c_num2.number_input("H", 1000, 30000, key="h_num", on_change=sync_h_from_num, label_visibility="collapsed")
        
        wall_width = st.session_state.w_num
        wall_height = st.session_state.h_num
        
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
        
        # --- GROSSES DASHBOARD (GESAMTPREIS & FLÄCHEN) ---
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
        
        # Sidebar Stats parallel updaten
        stats_container.markdown(f"**{T['wall_area']}:** {wall_area_m2:.2f} m²\n\n**{T['win_area']}:** {win_area_m2:.2f} m²\n\n**{T['fill_rate']}:** {win_pct:.1f}%\n\n### 💶 {T['price_total']}:\n## **{total_price:.2f} €**")
        
        # --- DRAG & DROP HTML Rendering mit Scale Figure & Window Icons ---
        scale = 800 / max(wall_width, 1)
        canvas_w = int(wall_width * scale)
        canvas_h = int(wall_height * scale)
        figure_h_px = int(1780 * scale) # 1.78m Architektur-Figur

        js_placed = []
        for p in placed:
            js_placed.append({
                "id": p['id'], "label": f"{p['pos_label']}\n{p['w']}x{p['h']}", "color": p['color'],
                "x": int(p['x'] * scale), "y": int(canvas_h - (p['y'] * scale) - (p['h'] * scale)),
                "w": int(p['w'] * scale), "h": int(p['h'] * scale),
                "is_pinned": p.get('is_pinned', False)
            })

        js_gaps = []
        for g in gaps:
            js_gaps.append({
                "label": f"{(g['w']*g['h']/1000000):.2f} m²" if g['w'] >= 400 and g['h'] >= 400 else "",
                "x": int(g['x'] * scale), "y": int(canvas_h - (g['y'] * scale) - (g['h'] * scale)),
                "w": int(g['w'] * scale), "h": int(g['h'] * scale)
            })

        # SVG einer klassischen architektonischen Menschen-Silhouette
        arch_silhouette_svg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 250'><circle cx='50' cy='20' r='14' fill='%23333'/><path d='M30 45 Q50 35 70 45 L80 110 L65 110 L60 70 L55 120 L60 240 L40 240 L45 140 L40 140 L45 240 L25 240 L35 120 L25 70 L20 110 L5 110 Z' fill='%23333'/></svg>"

        html_code = f"""
        <!DOCTYPE html><html><head><style>
            body {{ margin: 0; padding: 0; background-color: #f0f2f6; font-family: sans-serif; }}
            .container {{ display: flex; align-items: flex-end; justify-content: center; gap: 15px; padding-top: 20px; }}
            .scale-figure {{ width: {max(25, int(400*scale))}px; height: {figure_h_px}px; background: url("{arch_silhouette_svg}") no-repeat bottom center/contain; opacity: 0.8; }}
            #wall {{ width: {canvas_w}px; height: {canvas_h}px; background: repeating-linear-gradient(45deg, #ffcccc, #ffcccc 10px, #ffffff 10px, #ffffff 20px); border: 4px solid #cc0000; position: relative; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .window {{ position: absolute; border: 3px solid #222; box-sizing: border-box; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 11px; font-weight: bold; color: #222; cursor: grab; user-select: none; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); transition: box-shadow 0.2s; z-index: 10; flex-direction: column; }}
            .window.pinned {{ cursor: not-allowed; opacity: 0.95; border: 4px solid #222; }}
            .window:active:not(.pinned) {{ cursor: grabbing; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); z-index: 1000 !important; }}
            .win-icons {{ position: absolute; top: 2px; right: 2px; display: flex; gap: 3px; }}
            .win-btn {{ background: rgba(255,255,255,0.8); border: 1px solid #555; border-radius: 3px; font-size: 10px; cursor: pointer; padding: 1px 4px; pointer-events: auto; }}
            .win-btn:hover {{ background: white; }}
            .gap {{ position: absolute; background-color: rgba(255, 77, 77, 0.4); border: 1px dashed darkred; display: flex; align-items: center; justify-content: center; font-size: 9px; color: white; box-sizing: border-box; z-index: 5; font-weight: bold; pointer-events: none; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }}
        </style></head><body>
            <div class="container">
                <div class="scale-figure" title="Scale Figure (1,78m)"></div>
                <div id="wall"></div>
            </div>
            <script>
                const wall = document.getElementById('wall');
                const items = {json.dumps(js_placed)};
                const gaps = {json.dumps(js_gaps)};
                let draggedEl = null; let startX, startY, initialLeft, initialTop;

                gaps.forEach(gap => {{
                    const el = document.createElement('div');
                    el.className = 'gap'; el.innerText = gap.label;
                    el.style.width = gap.w + 'px'; el.style.height = gap.h + 'px'; el.style.left = gap.x + 'px'; el.style.top = gap.y + 'px';
                    wall.appendChild(el);
                }});

                items.forEach(item => {{
                    const el = document.createElement('div');
                    el.className = 'window'; 
                    if (item.is_pinned) el.classList.add('pinned');
                    el.id = item.id; 
                    
                    // ICONS & LABEL RENDER
                    el.innerHTML = `
                        <div class="win-icons">
                            <div class="win-btn rot-btn" title="Lokal Rotieren">🔄</div>
                            <div class="win-btn pin-btn" title="Lokal Anpinnen">📌</div>
                        </div>
                        <div style="margin-top:12px;">${item.label.replace(/\\n/g, '<br>')}</div>
                    `;
                    el.style.backgroundColor = item.color; el.style.width = item.w + 'px'; el.style.height = item.h + 'px'; el.style.left = item.x + 'px'; el.style.top = item.y + 'px';
                    
                    // Interaktive Klicks im Canvas
                    el.querySelector('.rot-btn').addEventListener('click', (e) => {{
                        e.stopPropagation();
                        let w = el.style.width; el.style.width = el.style.height; el.style.height = w;
                    }});
                    el.querySelector('.pin-btn').addEventListener('click', (e) => {{
                        e.stopPropagation();
                        el.classList.toggle('pinned');
                    }});
                    
                    el.addEventListener('mousedown', dragStart);
                    wall.appendChild(el);
                }});

                function dragStart(e) {{
                    if (e.target.classList.contains('win-btn')) return;
                    let targetWindow = e.target.closest('.window');
                    if (!targetWindow || targetWindow.classList.contains('pinned')) return;
                    draggedEl = targetWindow; startX = e.clientX; startY = e.clientY;
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
        st.caption("ℹ️ **Info Icons:** Die Klicks auf 📌 und 🔄 *im Bild* ändern nur die Vorschau. Um ein Fenster für die KI-Berechnung dauerhaft zu speichern, setze den Haken in der Matrix unten!")
        components.html(html_code, height=canvas_h + 50)

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
            T["col_area"]: f"{area_m2:.2f}", T["col_type"]: item['type'], T["col_price"]: f"{item['price']:.2f} €"
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
            T["col_pin"]: st.column_config.CheckboxColumn(T["col_pin"], help="Sperrt die Position für den KI Algorithmus."),
            "📍 Man X": st.column_config.NumberColumn("📍 Man X"),
            "📍 Man Y": st.column_config.NumberColumn("📍 Man Y"), T["col_rotate"]: st.column_config.CheckboxColumn(T["col_rotate"]),
            T["col_force"]: st.column_config.CheckboxColumn(T["col_force"])
        },
        disabled=[T["col_type"], "Pos", T["col_status"], T["col_dim"], T["col_area"], T["col_price"]], 
        use_container_width=True, key="windows_editor"
    )
    
    changes_made = False
    for item_id, row in edited_df.iterrows():
        if item_id in st.session_state['item_states']:
            state = st.session_state['item_states'][item_id]
            new_vis = bool(row[T['col_layer']]); new_rot = bool(row[T['col_rotate']]); new_fce = bool(row[T['col_force']]); new_pin = bool(row[T['col_pin']])
            new_mx = None if pd.isna(row['📍 Man X']) else int(row['📍 Man X']); new_my = None if pd.isna(row['📍 Man Y']) else int(row['📍 Man Y'])
            
            # PIN LOGIK (Setzt die ECHTE Position aus dem Algorithmus ein, nicht 0,0!)
            if new_pin != state.get('pinned', False):
                state['pinned'] = new_pin
                if new_pin: 
                    # Hole die aktuelle Position aus der Grafik
                    curr_x = placed_dict[item_id]['x'] if item_id in placed_dict else 0
                    curr_y = placed_dict[item_id]['y'] if item_id in placed_dict else 0
                    state['man_x'] = curr_x
                    state['man_y'] = curr_y
                else: 
                    state['man_x'] = None
                    state['man_y'] = None
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
        df_gaps_data.append({T["col_type"]: T["fill"], "Pos": "Gap", T["col_status"]: "⚠️", T["col_dim"]: f"{g['w']} x {g['h']}", T["col_area"]: f"{area_m2:.2f}", "Herkunft": g['source'], T["col_price"]: "-"})
    df_gaps = pd.DataFrame(df_gaps_data)
    final_export_df = pd.concat([export_data, df_gaps], ignore_index=True)
    final_export_df = final_export_df.drop(columns=['_color', T['col_layer'], T['col_pin'], T['col_rotate'], '📍 Man X', '📍 Man Y', T['col_force']], errors='ignore')
    csv = final_export_df.to_csv(index=False).encode('utf-8')
    st.download_button(label=T["export_btn"], data=csv, file_name='stueckliste.csv', mime='text/csv', type="primary")
    
    st.subheader(T["gaps_header"])
    if not df_gaps.empty: st.dataframe(df_gaps[[T["col_type"], T["col_dim"], T["col_area"], "Herkunft"]], hide_index=True, use_container_width=True)
    else: st.success(T["no_gaps"])
else:
    st.info("👈 Bitte starte die Suche in der Seitenleiste.")
