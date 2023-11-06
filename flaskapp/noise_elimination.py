import cv2
from matplotlib import pyplot as plt
import numpy as np

def apply_gaussian_blur(image):
    # Фильтр Гаусса для сглаживания изображения
    return cv2.GaussianBlur(image, (5, 5), 0)

def apply_median_blur(image):
    # Медианный фильтр для сглаживания изображения
    return cv2.medianBlur(image, 5)

def color_distribution(image, dst_fname):
    image = np.array(image)
    if image.ndim == 2:
        image = np.dstack([image] * 3)
    colors = ('r', 'g', 'b')
    plt.figure()
    for i, col in enumerate(colors):
        hist, _ = np.histogram(image[:, :, i], 255)
        plt.plot(hist, color=col)
        plt.xlim([0, 256])
    plt.savefig(dst_fname)
    plt.clf()

def generate_noise_histogram(image, smoothed_image, dst_fname):
    # Генерация графика распределения шума (разницы между оригинальным и сглаженным изображением)
    noise_distribution = image - smoothed_image
    noise_distribution = np.abs(noise_distribution).sum(axis=2).flatten()

    plt.hist(noise_distribution, bins=256, range=(0, 256), density=True)
    plt.title('Noise\'s distribution')
    plt.xlabel('Brightness')
    plt.ylabel('Frequency')
    plt.savefig(dst_fname)
    plt.clf()

