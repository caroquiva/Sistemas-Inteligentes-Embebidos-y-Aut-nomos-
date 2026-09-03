import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 1. Función para la Matriz D-H
def dh_matrix(alpha, a, d, theta):
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,             np.sin(alpha),                np.cos(alpha),               d],
        [0,             0,                            0,                           1]
    ])

# 2. Función de Cinemática Directa
def forward_kinematics(q_deg):
    d1, a2, a3, d4 = 0.25, 0.15, 0.10, 0.05
    q = np.deg2rad(q_deg)

    T01 = dh_matrix(0, 0, d1, q[0])
    T12 = dh_matrix(np.pi/2, 0, 0, q[1])
    T23 = dh_matrix(0, a2, 0, q[2])
    T34 = dh_matrix(0, a3, d4, q[3])

    T02 = T01 @ T12
    T03 = T02 @ T23
    T04 = T03 @ T34

    points = np.array([
        [0, 0, 0],
        T01[0:3, 3],
        T02[0:3, 3],
        T03[0:3, 3],
        T04[0:3, 3]
    ])
    return points

# 3. Configuración de la Ventana y Gráfico 3D
fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection='3d')

# Valores fijos para q1, q2, q3
q1_fijo, q2_fijo, q3_fijo = 15, 10, -20

# Dibujar robot en estado inicial
pts = forward_kinematics([q1_fijo, q2_fijo, q3_fijo, 0])
line, = ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], '-o', linewidth=4, markersize=8, color='#1f77b4')
end_point, = ax.plot([pts[-1, 0]], [pts[-1, 1]], [pts[-1, 2]], 'ro', markersize=8)

# Configurar límites del sistema cartesiano
ax.set_xlim([-0.4, 0.4])
ax.set_ylim([-0.4, 0.4])
ax.set_zlim([0, 0.6])
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('Movimiento Automático de q4')

# 4. Función de Animación (se ejecuta en cada frame)
def update(frame):
   
    q4_animado = frame
    q_current = [q1_fijo, q2_fijo, q3_fijo, q4_animado]
    new_pts = forward_kinematics(q_current)
    
    line.set_data(new_pts[:, 0], new_pts[:, 1])
    line.set_3d_properties(new_pts[:, 2])
    
    end_point.set_data([new_pts[-1, 0]], [new_pts[-1, 1]])
    end_point.set_3d_properties([new_pts[-1, 2]])
    
    return line, end_point

subida = np.linspace(-90, 90, 60)
bajada = np.linspace(90, -90, 60)
frames = np.concatenate([subida, bajada])
ani = animation.FuncAnimation(fig, update, frames=frames, interval=30)
plt.show()