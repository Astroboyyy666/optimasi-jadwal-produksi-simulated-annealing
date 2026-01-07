from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
import math

app = Flask(__name__)
CORS(app)

# ================= DATA PEKERJAAN (Satuan: Menit) =================
JOBS_DATA = [
    {"id": 1, "task": "Job 1", "duration": 120},
    {"id": 2, "task": "Job 2", "duration": 600},
    {"id": 3, "task": "Job 3", "duration": 240},
    {"id": 4, "task": "Job 4", "duration": 720},
    {"id": 5, "task": "Job 5", "duration": 360},
    {"id": 6, "task": "Job 6", "duration": 180}
]

# ================= SETUP TIME (Satuan: Menit) =================
# Waktu tambahan yang dibutuhkan jika urutan pekerjaan tertentu bertemu
SETUP_TIME = {
    ("Job 1", "Job 2"): 2,
    ("Job 3", "Job 4"): 3,
    ("Job 5", "Job 6"): 1
}

# ================= COST FUNCTION =================
def calculate_cost(schedule):
    total = 0
    for i, job in enumerate(schedule):
        total += job['duration']
        if i > 0:
            prev_task = schedule[i - 1]['task']
            curr_task = job['task']
            total += SETUP_TIME.get((prev_task, curr_task), 0)
    return total

# ================= SIMULATED ANNEALING =================
def simulated_annealing(data):
    current = list(data)
    best = list(data)

    current_cost = calculate_cost(current)
    best_cost = current_cost

    T = 100.0
    cooling_rate = 0.95
    iteration = 1
    logs = []

    while T > 1:
        new = list(current)
        # Swap dua posisi secara acak
        i, j = random.sample(range(len(new)), 2)
        new[i], new[j] = new[j], new[i]

        new_cost = calculate_cost(new)
        delta_E = new_cost - current_cost

        accepted = False
        # Logika penerimaan solusi baru (Metropolis Criterion)
        if delta_E <= 0 or random.random() < math.exp(-delta_E / T):
            accepted = True
            current = new
            current_cost = new_cost

        # Simpan solusi terbaik yang pernah ditemukan
        if current_cost < best_cost:
            best = current
            best_cost = current_cost

        logs.append({
            "iterasi": iteration,
            "temperature": round(T, 2),
            "delta_E": delta_E,
            "accepted": accepted,
            "cost": current_cost
        })

        T *= cooling_rate
        iteration += 1

    return best, best_cost, logs

# ================= RUMUS SA (Satuan: Menit) =================
def sa_formula():
    return {
        "cost": "Cost = Σ durasi + setup time (Menit)",
        "delta": "ΔE = Cost_baru − Cost_lama",
        "probability": "P = e^(−ΔE / T)",
        "cooling": "T_baru = T_lama × α",
        "decision": [
            "Jika ΔE ≤ 0 → solusi diterima",
            "Jika ΔE > 0 → solusi diterima jika random < P"
        ]
    }

# ================= ROUTES =================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'atmin' and data.get('password') == 'amba123':
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "failed"}), 401

@app.route('/initial-data')
def initial_data():
    return jsonify({
        "original": JOBS_DATA,
        "total_minutes": calculate_cost(JOBS_DATA) # Diubah dari total_hours
    })

@app.route('/optimize')
def optimize():
    optimized, cost, logs = simulated_annealing(JOBS_DATA)
    return jsonify({
        "optimized": optimized,
        "total_minutes": cost, # Diubah dari total_hours
        "logs": logs
    })

@app.route('/formula')
def formula():
    return jsonify(sa_formula())

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)