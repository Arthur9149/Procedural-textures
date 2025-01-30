import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.ndimage import gaussian_filter
import os

def generate_random_hex_colors(seed=None):
    """
    Generate a list of random hexadecimal colors.
    
    Args:
        seed (int, optional): Seed for the random number generator.
    
    Returns:
        list: List of random hexadecimal color codes.
    """
    if seed is not None:
        random.seed(seed)
    number_of_colors = random.randint(1, 40)
    random_colors = []
    for _ in range(number_of_colors):
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        random_colors.append(color)
    return random_colors

def create_smooth_gradient(colors, n_colors=1024):
    """
    Create a smooth gradient colormap from a list of colors.
    
    Args:
        colors (list): List of hexadecimal color codes.
        n_colors (int, optional): Number of colors in the gradient.
    
    Returns:
        tuple: Colormap and gradient array.
    """
    cmap = mcolors.LinearSegmentedColormap.from_list('custom_gradient', colors, N=n_colors)
    gradient = np.linspace(0, 1, n_colors)
    gradient = np.vstack((gradient, gradient))
    return cmap, gradient

def perlin_noise(shape=(4096, 4096), scale=10):
    """
    Generate Perlin noise and a corresponding colormap.
    
    Args:
        shape (tuple, optional): Shape of the output noise array.
        scale (int, optional): Scaling factor for the noise.
    
    Returns:
        tuple: Normalized Perlin noise array and colormap.
    """
    def lerp(a, b, x):
        return a + x * (b - a)

    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def grad(hash, x, y):
        h = hash & 3
        u = np.where(h < 2, x, y)
        v = np.where(h < 2, y, x)
        return (np.where((h & 1) == 0, u, -u) + np.where((h & 2) == 0, v, -v))

    def perlin(x, y):
        xi, yi = x.astype(int) & 255, y.astype(int) & 255
        xf, yf = x - xi, y - yi
        u, v = fade(xf), fade(yf)

        n00 = grad(p[p[xi] + yi], xf, yf)
        n01 = grad(p[p[xi] + yi + 1], xf, yf - 1)
        n11 = grad(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
        n10 = grad(p[p[xi + 1] + yi], xf - 1, yf)

        x1 = lerp(n00, n10, u)
        x2 = lerp(n01, n11, u)
        return lerp(x1, x2, v)

    print("Perlin Noise generation...")

    lin = np.linspace(0, shape[0] // scale, shape[0], endpoint=False)
    x, y = np.meshgrid(lin, lin)

    seed = random.randint(0, 100)
    np.random.seed(seed)
    p = np.arange(256, dtype=int)
    np.random.shuffle(p)
    p = np.stack([p, p]).flatten()

    noise = perlin(x, y)
    norm_noise = (noise - noise.min()) / (noise.max() - noise.min())

    seed = random.randint(0, 100)
    random_hex_colors_list = generate_random_hex_colors(seed)
    cmap, gradient = create_smooth_gradient(random_hex_colors_list)
    
    return norm_noise, cmap

def voronoi_noise(shape=(4096, 4096), points=50):
    """
    Generate Voronoi noise.
    
    Args:
        shape (tuple, optional): Shape of the output noise array.
        points (int, optional): Number of points to generate Voronoi regions.
    
    Returns:
        numpy.ndarray: Voronoi noise array.
    """
    print("Voronoi Noise generation...")
    point_x = np.random.randint(0, shape[0], points)
    point_y = np.random.randint(0, shape[1], points)
    
    grid_x, grid_y = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]))
    grid_x = grid_x.flatten()
    grid_y = grid_y.flatten()
    
    distances = np.zeros((shape[0] * shape[1], points))
    for i in range(points):
        distances[:, i] = np.sqrt((grid_x - point_x[i]) ** 2 + (grid_y - point_y[i]) ** 2)
    
    min_distances = distances.min(axis=1).reshape(shape)
    
    return min_distances

def get_unique_filename(base_path, extension):
    """
    Generate a unique filename by appending a number to the base path.
    
    Args:
        base_path (str): Base path for the file.
        extension (str): File extension.
    
    Returns:
        str: Unique filename.
    """
    i = 1
    while True:
        filename = f"{base_path}_{i}.{extension}"
        if not os.path.exists(filename):
            return filename
        i += 1

def main(output_dir):
    """
    Main function to generate and save noise texture.
    
    Args:
        output_dir (str): Directory to save the generated texture.
    """
    noise_type = input("Do you want Perlin or Voronoi noise ? (Perlin/Voronoi): ").strip().lower()
    shape = (4096, 4096)
    
    if noise_type == 'perlin':
        noise, cmap = perlin_noise(shape=shape, scale=10)
    elif noise_type == 'voronoi':
        noise_seed = random.randint(0, 100)
        np.random.seed(noise_seed)
        points = random.randint(5, 50)
        voronoi = voronoi_noise(shape, points)
        noise = (voronoi - voronoi.min()) / (voronoi.max() - voronoi.min())
        
        seed = random.randint(0, 100)
        random_hex_colors_list = generate_random_hex_colors(seed)
        cmap, gradient = create_smooth_gradient(random_hex_colors_list)
    else:
        print("Invalid choice. Please enter 'Perlin' or 'Voronoi'.")
        return

    blur_seed = random.randint(0, 100)
    random.seed(blur_seed)
    sigma = random.uniform(0.06, 0.10) * min(shape)  # Minimum de 6% pour le flou gaussien
    noise = gaussian_filter(noise, sigma=sigma)

    base_path = os.path.join(output_dir, "texture")
    output_path = get_unique_filename(base_path, "png")
    plt.imsave(output_path, noise, cmap=cmap)
    
    print(f"The image has been saved here: {output_path}")

# Specify the output directory path
output_dir = r"C:\ESAD\Autonomie\tout_faire_avec_rien_rien_faire_avec_tout\Dossier_couleur\procedural_textures"  # Replace with the actual path
main(output_dir)
