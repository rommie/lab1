import cv2
from matplotlib import pyplot as plt
import numpy as np

def apply_gaussian_blur(image):
    # Применить фильтр Гаусса для сглаживания изображения
    return cv2.GaussianBlur(image, (5, 5), 0)

def apply_median_blur(image):
    # Применить медианный фильтр для сглаживания изображения
    return cv2.medianBlur(image, 5)


def color_distribution(image, dst_fname):
    # Функция для создания графиков распределения цветов в изображении.
    # Преобразование изображения в массив NumPy
    image = np.array(image)
    # Если изображение имеет всего один канал, конвертируем его в RGB формат
    if image.ndim == 2:
        image = np.dstack([image] * 3)
    # Определение цветовых каналов (красный, зеленый, синий)
    colors = ('r', 'g', 'b')
    # Создание нового графика
    plt.figure()
    # Для каждого цветового канала
    for i, col in enumerate(colors):
        # Вычисление гистограммы распределения значений цветового канала
        hist, _ = np.histogram(image[:, :, i], 255)
        # Отображение гистограммы на графике с указанием цвета
        plt.plot(hist, color=col)
        # Установка пределов для оси X
        plt.xlim([0, 256])
    # Сохранение графика в файл с указанным именем
    plt.savefig(dst_fname)
    # Очистка текущего графика
    plt.clf()


def generate_noise_histogram(image, smoothed_image, dst_fname):
    # Функция для генерации гистограммы шума (разницы между оригинальным и сглаженным изображением).
    # Расчет разницы между оригинальным и сглаженным изображением
    noise_distribution = image - smoothed_image
    # Преобразование разницы в абсолютные значения и суммирование значений по всем каналам
    noise_distribution = np.abs(noise_distribution).sum(axis=2).flatten()
    # Создание гистограммы на основе полученных значений шума
    plt.hist(noise_distribution, bins=256, range=(0, 256), density=True)
    # Установка заголовка для гистограммы
    plt.title('Распределение шума')
    # Установка подписей осей X и Y
    plt.xlabel('Яркость')
    plt.ylabel('Частота')
    # Сохранение гистограммы в файл с указанным именем
    plt.savefig(dst_fname)
    # Очистка текущего графика
    plt.clf()

