# codemm.py 

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

def generer_graphiques_vraie_sequence_proximale_distale_avec_phases_labels():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.interpolate import make_interp_spline

    temps_points = np.array([0.0, 0.5, 1.0, 1.3, 1.5, 1.7, 1.85, 2.0, 2.3, 3.0])
    hip_speed_points   = [0, 25, 65, 80, 60, 35, 25, 17, 20, 0]
    knee_speed_points  = [0, 10, 70, 115, 160, 110, 60, 45, 30, 0]
    ankle_speed_points = [0, 8, 20, 35, 70, 180, 260, 200, 100, 0]

    temps_lisse = np.linspace(0, 3.0, 300)
    hip_speed   = make_interp_spline(temps_points, hip_speed_points, k=3)(temps_lisse)
    knee_speed  = make_interp_spline(temps_points, knee_speed_points, k=3)(temps_lisse)
    ankle_speed = make_interp_spline(temps_points, ankle_speed_points, k=3)(temps_lisse)

    impact_time = 1.7
    phases = ['Approche', 'Frappe', 'Impact', 'Suivi']
    phase_times = [0.0, 1.2, impact_time, 2.0, 3.0]
    phase_colors = ["#d0e1f9", '#f9d0d0', '#ffe0b2', '#dcedc8']

    fig, ax = plt.subplots(figsize=(10, 3.5))

    for i in range(len(phases)):
        ax.axvspan(phase_times[i], phase_times[i+1], color=phase_colors[i], alpha=0.4)
        center = (phase_times[i] + phase_times[i+1]) / 2
        ax.text(center, 0.65 * np.max(ankle_speed), phases[i], ha='center', va='center',
                fontsize=10, color='black', fontweight='bold')

    l1, = ax.plot(temps_lisse, hip_speed, color='black', linewidth=2, label="Hanche")
    l2, = ax.plot(temps_lisse, knee_speed, color='black', linewidth=2, linestyle='--', label="Genou")
    l3, = ax.plot(temps_lisse, ankle_speed, color='black', linewidth=2, linestyle=':', label="Cheville")

    ax.axvline(x=impact_time, color='red', linestyle='-', linewidth=2)
    ax.text(impact_time+0.01, np.max(ankle_speed), 'IMPACT', rotation=90, va='bottom', color='red', fontsize=8, fontweight='bold')

    ax.set_xlabel("Temps (s)")
    ax.set_xlim(0, 3)
    ax.set_xticks(np.arange(0, 3.5, 0.5))
    ax.set_xticklabels([f"{t:.1f}" for t in np.arange(0, 3.5, 0.5)])
    ax.set_yticks([])
    ax.set_ylabel("")
    # Légende bien éloignée
    ax.legend(handles=[l3, l2, l1], loc='upper center', bbox_to_anchor=(0.5, 1.33), ncol=3, frameon=False, fontsize=11)

    for spine in ["left", "right", "top"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_linewidth(1.2)
    ax.grid(False)
    plt.tight_layout()
    return fig


# Générer et afficher le graphe
fig = generer_graphiques_vraie_sequence_proximale_distale_avec_phases_labels()
fig.savefig("graphe_points_proximale_distale.png")
plt.show()


# Décalage du pic de jambe à 1.9 secondes (erreur biomécanique simulée)
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

def generer_vitesses_angulaires_jambe_pic_1_9s():
    # Temps
    temps_points = np.array([0.0, 0.5, 1.0, 1.3, 1.5, 1.7, 1.9, 2.2, 3.0])

    # Cuisse reste inchangée
    cuisse_points = np.array([0, 50, 180, 220, 200, 80, 30, 20, 0])

    # Jambe avec pic décalé à 1.9s
    jambe_points = np.array([0, 0, 30, 80, 160, 300, 400, 200, 0])

    # Temps lissé
    temps_lisse = np.linspace(0, 3.0, 300)

    # Spline cubique naturelle
    spline_cuisse = CubicSpline(temps_points, cuisse_points, bc_type='natural')
    spline_jambe = CubicSpline(temps_points, jambe_points, bc_type='natural')

    cuisse_speed = spline_cuisse(temps_lisse)
    jambe_speed = spline_jambe(temps_lisse)

    cuisse_speed[0] = 0.0
    jambe_speed[0] = 0.0

    impact_time = 1.7

    # Phases
    phases = ['Approche', 'Frappe', 'Impact', 'Suivi']
    phase_times = [0.0, 1.2, 1.7, 2.0, 3.0]
    phase_colors = ['#d0e1f9', '#f9d0d0', '#ffe0b2', '#dcedc8']

    fig, ax = plt.subplots(figsize=(10, 4))

    # Phases colorées
    for i in range(len(phases)):
        ax.axvspan(phase_times[i], phase_times[i + 1], color=phase_colors[i], alpha=0.4)
        center = (phase_times[i] + phase_times[i + 1]) / 2
        ax.text(center, 0.5 * np.max(jambe_speed), phases[i], ha='center', va='center',
                fontsize=12, color='black', fontweight='bold')

    # Courbes
    l1, = ax.plot(temps_lisse, cuisse_speed, color='black', linewidth=2, label="Cuisse")
    l2, = ax.plot(temps_lisse, jambe_speed, color='black', linewidth=2, linestyle='--', label="Jambe")

    # Ligne Impact
    ax.axvline(x=impact_time, color='red', linestyle='-', linewidth=2)
    ax.text(impact_time + 0.05, np.max(jambe_speed) + 20, 'IMPACT', rotation=90, verticalalignment='center', color='red')

    # Axe X
    ax.set_xlabel("Temps (s)")
    ax.set_xlim(0, 3)
    ax.set_xticks(np.arange(0, 3.5, 0.5))
    ax.set_xticklabels([f"{t:.1f}" for t in np.arange(0, 3.5, 0.5)])

    # Suppression axe Y
    ax.set_yticks([])
    ax.set_ylabel("")

    # Légende plus éloignée du graphe
    ax.legend(handles=[l2, l1], loc='upper center', bbox_to_anchor=(0.5, 1.27), ncol=2, frameon=False)

    # Clean
    for spine in ["left", "right", "top"]:
        ax.spines[spine].set_visible(False)
    
    ax.spines["bottom"].set_linewidth(1.2)
    ax.grid(False)
    plt.tight_layout()
    return fig


# Générer et afficher
fig_jambe_1_9s = generer_vitesses_angulaires_jambe_pic_1_9s()
fig_jambe_1_9s.savefig("graphe_vitesses_angulaires_jambe_pic_1_9s.png")
fig_jambe_1_9s.show()

import matplotlib.pyplot as plt
import numpy as np

def generer_radar_notes(notes_par_phase, figsize=(7, 7)):
    import matplotlib.pyplot as plt
    import numpy as np

    phases = list(notes_par_phase.keys())
    scores = list(notes_par_phase.values())
    scores += [scores[0]]
    labels = phases + [phases[0]]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=True)

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

    ax.plot(angles, scores, color='red', linewidth=2)
    ax.fill(angles, scores, color='red', alpha=0.25)

    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_ylim(0, 10)

    # Labels bien à l'extérieur (ici rayon = 12)
    for label, angle in zip(labels, angles):
        ax.text(
            angle,
            12,   # <- c’est ici que tu ajustes !
            label,
            size=15,
            horizontalalignment='center',
            verticalalignment='center',
            fontweight='bold'
        )

    ax.set_xticks([])
    ax.tick_params(axis='y', labelsize=12)
    plt.tight_layout(pad=3)
    return fig
