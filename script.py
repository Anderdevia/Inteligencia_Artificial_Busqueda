!pip install gradio
# =========================
# IMPORTACIONES
# =========================
import heapq
import gradio as gr
import time
# =========================
# GRAFO (BASE DE CONOCIMIENTO)
# =========================
graph = {
    "Usaquén": {"Chapinero": 15, "Suba": 20},
    "Chapinero": {"Usaquén": 15, "Teusaquillo": 10, "Santa Fe": 8},
    "Suba": {"Usaquén": 20, "Engativá": 12, "Chapinero": 18},
    "Engativá": {"Suba": 12, "Fontibón": 10, "Teusaquillo": 14},
    "Fontibón": {"Engativá": 10, "Kennedy": 8, "Santa Fe": 20},
    "Kennedy": {"Fontibón": 8, "Bosa": 7, "Teusaquillo": 18},
    "Bosa": {"Kennedy": 7, "Santa Fe": 25},
    "Teusaquillo": {"Chapinero": 10, "Santa Fe": 6, "Engativá": 14, "Kennedy": 18},
    "Santa Fe": {"Chapinero": 8, "Teusaquillo": 6, "Fontibón": 20, "Bosa": 25}
}

# =========================
# HEURÍSTICA DINÁMICA
# =========================
def heuristic(node, goal):
    if node == goal:
        return 0
    if goal in graph[node]:
        return graph[node][goal]
    return 20


# =========================
# A* (MEJOR RUTA)
# =========================
def astar(start, goal):
    queue = [(0, start, [], 0)]
    visited = set()
    steps_log = []
    step = 0

    while queue:
        f, node, path, g = heapq.heappop(queue)

        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        step += 1
        steps_log.append(f"Step {step} | Expand: {node} | Cost: {g}")

        if node == goal:
            return path, g, steps_log

        for neighbor, weight in graph[node].items():
            if neighbor not in visited:
                new_g = g + weight
                h = heuristic(neighbor, goal)
                new_f = new_g + h

                steps_log.append(
                    f"   -> push: {neighbor} (g={new_g}, h={h}, f={new_f})"
                )

                heapq.heappush(queue, (new_f, neighbor, path, new_g))

    return path, g, steps_log


# =========================
# TODAS LAS RUTAS
# =========================
def find_all_routes(start, end, path=None):
    if path is None:
        path = []

    path = path + [start]

    if start == end:
        return [path]

    routes = []

    for node in graph[start]:
        if node not in path:
            new_routes = find_all_routes(node, end, path)
            for r in new_routes:
                routes.append(r)

    return routes


# =========================
# COSTO DE RUTA
# =========================
def calculate_cost(route):
    cost = 0
    for i in range(len(route) - 1):
        cost += graph[route[i]][route[i + 1]]
    return cost


# =========================
# FUNCIÓN PRINCIPAL
# =========================
def find_route(start, end):
    if start == end:
        return "⚠️ El punto A y el punto B no pueden ser el mismo"

    # 🔹 Mejor ruta con A*
    best_path, best_cost, log = astar(start, end)

    # 🔹 Todas las rutas posibles
    routes = find_all_routes(start, end)

    routes_info = []

    for r in routes:
        # ⏱️ medir tiempo por ruta
        route_start = time.time()

        cost = calculate_cost(r)

        route_end = time.time()
        route_time = (route_end - route_start) * 1000  # ms

        routes_info.append((r, cost, route_time))

    # 🔹 ordenar por tiempo de viaje
    routes_info.sort(key=lambda x: x[1])

    best = routes_info[0]
    worst = routes_info[-1]

    # 🔹 quitar mejor ruta de alternativas
    alternative_routes = [
        (r, c, t) for r, c, t in routes_info if r != best_path
    ]

    # 🔹 construir texto de rutas alternativas
    routes_text = ""
    for r, c, t in alternative_routes[:5]:
        routes_text += (
            "• " + " → ".join(r)
            + f"\n  📍 Barrios: {len(r)}"
            + f"\n  ⏱️ Tiempo: {c} min"
            + f"\n  ⚙️ Ejecución: {t} ms\n\n"
        )

    # 🔹 log A*
    log_text = "\n".join(log)

    return (
        "## ✅ Mejor ruta (más rápida)\n\n"
        + " → ".join(best[0])
        + f"\n📍 Barrios: {len(best[0])}"
        + f"\n⏱️ Tiempo: {best[1]} min"
        + f"\n⚙️ Ejecución: {best[2]} ms\n\n"
        + "## 🐢 Ruta más lenta\n\n"
        + " → ".join(worst[0])
        + f"\n📍 Barrios: {len(worst[0])}"
        + f"\n⏱️ Tiempo: {worst[1]} min"
        + f"\n⚙️ Ejecución: {worst[2]} ms\n\n"
        + "## 🔄 Otras rutas posibles\n\n"
        + (routes_text if routes_text else "No hay rutas alternativas\n\n")
        + "---\n\n"
        + "## 🔍 Proceso A*\n\n"
        + log_text
    )
# =========================
# INTERFAZ (GRADIO)
# =========================
with gr.Blocks() as demo:
    gr.Markdown("# Sistema Inteligente ")

    with gr.Row():
        start = gr.Dropdown(list(graph.keys()), label="📍 Punto A")
        end = gr.Dropdown(list(graph.keys()), label="🎯 Punto B")

    btn = gr.Button("🔍 Calcular rutas")

    result = gr.Markdown()

    btn.click(fn=find_route, inputs=[start, end], outputs=result)

# =========================
# EJECUCIÓN
# =========================
demo.launch()