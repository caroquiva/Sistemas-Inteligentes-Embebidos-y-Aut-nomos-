import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 1. Función para la Matriz D-H (Estándar)
def dh_matrix(alpha, a, d, theta):
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,             np.sin(alpha),                np.cos(alpha),               d],
        [0,             0,                            0,                           1]
    ])

# 2. Cinemática Directa del Pórtico Cartesiano 4-DOF
def forward_kinematics(q):
    """
    q = [x, y, z, theta4_deg]
    x, y, z: Posiciones de los ejes prismáticos (metros)
    theta4_deg: Ángulo de la muñeca (grados)
    """
    x, y, z, theta4_deg = q
    theta4 = np.deg2rad(theta4_deg)
    d4 = 0.1  # Altura fija de la herramienta/garra (m)

    # Transformaciones homogéneas según la convención D-H
    T01 = dh_matrix(-np.pi/2, 0, x, 0)
    T12 = dh_matrix(-np.pi/2, 0, y, -np.pi/2)
    T23 = dh_matrix(0, 0, z, 0)
    T34 = dh_matrix(0, 0, d4, theta4)

    T02 = T01 @ T12
    T03 = T02 @ T23
    T04 = T03 @ T34

    # Coordenadas de la estructura física del pórtico
    points = np.array([
        [0, 0, 0.6],             # Base del eje X superior
        [x, 0, 0.6],             # Carro X
        [x, y, 0.6],             # Carro Y
        [x, y, 0.6 - z],         # Extremo inferior del eje vertical Z
        [x, y, 0.6 - z - d4]     # Punta de la garra (Efector final)
    ])
    return points

# 3. Configuración de la Ventana 3D
fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection='3d')

# Dibujar la estructura en la posición inicial
pts_init = forward_kinematics([0.1, 0.1, 0.1, 0])
line, = ax.plot(pts_init[:, 0], pts_init[:, 1], pts_init[:, 2], '-o', linewidth=4, markersize=8, color='#1f77b4', label='Estructura del Robot')
end_point, = ax.plot([pts_init[-1, 0]], [pts_init[-1, 1]], [pts_init[-1, 2]], 'ro', markersize=9, label='Garra/Efector')

# Configuración del espacio de trabajo
ax.set_xlim([0, 0.8])
ax.set_ylim([0, 0.8])
ax.set_zlim([0, 0.8])
ax.set_xlabel('Eje X (m)')
ax.set_ylabel('Eje Y (m)')
ax.set_zlabel('Eje Z (m)')
ax.set_title('Animación Multieje: Robot Pórtico Cartesiano 4-DOF (PPP-R)')
ax.legend(loc='upper right')

# 4. Generación de la Trayectoria Multieje (Simulación Pick and Place)
num_steps = 100

# Animación lineal simultánea de X, Y, Z y giro de theta4
x_traj = np.linspace(0.1, 0.7, num_steps)        # Desplazamiento en X
y_traj = np.linspace(0.1, 0.6, num_steps)        # Desplazamiento en Y
z_traj = 0.2 + 0.15 * np.sin(np.linspace(0, np.pi, num_steps)) # Descenso y ascenso en Z
th4_traj = np.linspace(0, 360, num_steps)        # Giro completo de 360° en la muñeca

# Combinar trayectoria de ida y vuelta para hacer un bucle suave
x_full = np.concatenate([x_traj, x_traj[::-1]])
y_full = np.concatenate([y_traj, y_traj[::-1]])
z_full = np.concatenate([z_traj, z_traj[::-1]])
th4_full = np.concatenate([th4_traj, th4_traj[::-1]])

# 5. Función de actualización de la animación
def update(frame):
    x_curr = x_full[frame]
    y_curr = y_full[frame]
    z_curr = z_full[frame]
    th4_curr = th4_full[frame]

    new_pts = forward_kinematics([x_curr, y_curr, z_curr, th4_curr])

    # Actualizar líneas de los eslabones
    line.set_data(new_pts[:, 0], new_pts[:, 1])
    line.set_3d_properties(new_pts[:, 2])

    # Actualizar punto del efector final
    end_point.set_data([new_pts[-1, 0]], [new_pts[-1, 1]])
    end_point.set_3d_properties([new_pts[-1, 2]])

    return line, end_point

# Crear animación
ani = animation.FuncAnimation(
    fig, 
    update, 
    frames=len(x_full), 
    interval=30, 
    blit=False
)

plt.show()