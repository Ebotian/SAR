import streamlit as st
import numpy as np
from PIL import Image
import plotly.graph_objs as go
import cv2
from scipy.fftpack import fft2, ifft2, fftshift, ifftshift
import matplotlib.pyplot as plt

# 加载图像
img_path = 'C:/Users/Lenovo/Desktop/SAR/week4/runway.jpg'
img = Image.open(img_path)
img_array = np.array(img)

# 转换为灰度图像
gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

# 创建Plotly图像
fig = go.Figure(data=go.Heatmap(z=gray_img, colorscale='gray', showscale=False))

# 获取用户输入的坐标
x = st.number_input('Enter x coordinate:', min_value=0, max_value=img.width-1, value=555, step=1)
y = st.number_input('Enter y coordinate:', min_value=0, max_value=img.height-1, value=632, step=1)

x, y = int(x), int(y)
# 获取种子点的灰度值
seed_value = gray_img[y, x]
st.write(f'The gray level of the seed point is: {seed_value}')

# 获取用户输入的增长准则
threshold = st.number_input('Enter growth criterion:', min_value=0, max_value=255, value=50, step=1)

from collections import deque

def region_growing(img, seed, threshold):
  # 创建一个和输入图像同样大小的布尔数组，用于标记访问过的像素
  visited = np.zeros_like(img, dtype=np.bool_)
  dx = [-1, 0, 1, 0]
  dy = [0, 1, 0, -1]
  queue = deque([seed])
  seed_value = int(img[seed])

  while queue:
    x, y = queue.popleft()
    if not visited[y, x] and abs(int(img[y, x]) - seed_value) <= threshold:
      visited[y, x] = True
      img[y, x] = 0
      for i in range(4):
        nx, ny = x + dx[i], y + dy[i]
        if 0 <= nx < img.shape[1] and 0 <= ny < img.shape[0]:
          queue.append((nx, ny))
  return img

# 在主程序中使用区域增长算法
gray_img = region_growing(gray_img, (x, y), threshold)

# 更新Plotly图像
fig = go.Figure(data=go.Heatmap(z=gray_img, colorscale='gray', showscale=False))

# 在图像上添加十字线
fig.add_shape(type="line", x0=x, y0=0, x1=x, y1=gray_img.shape[0], line=dict(color="Red", width=2))
fig.add_shape(type="line", x0=0, y0=y, x1=gray_img.shape[1], y1=y, line=dict(color="Red", width=2))

# 自动调整图像大小以适应窗口宽度
fig.update_layout(autosize=True)
st.plotly_chart(fig)

# enter 模糊比参数b=光学/SAR
b = st.number_input('Enter the fuzzy ratio parameter b:', min_value=1.0, max_value=1000.0, value=50.0, step=0.1)

# 计算带宽omega
omega = (gray_img.shape[0] * gray_img.shape[1]) /((b+2.0)/3.0)

original_picture = gray_img.copy()

from scipy.fftpack import fftn, ifftn, fftshift, ifftshift

def low_pass_filter(complex_image, cutoff):
  # 提取复数图像的幅度和相位
  magnitude = np.abs(complex_image)
  phase = np.angle(complex_image)

  # Compute the 2-dimensional FFT of the phase
  fft_phase = fftshift(fftn(phase))

  # Create a grid of distances from the center of the image
  rows, cols = phase.shape
  half_rows, half_cols = rows // 2, cols // 2
  x, y = np.ogrid[:rows, :cols]
  distances = np.sqrt((x - half_rows)**2 + (y - half_cols)**2)

  # Create a mask that is True for all pixels within the cutoff distance
  mask = distances <= cutoff

  # Apply the mask to the FFT phase
  fft_phase *= mask

  # Compute the inverse FFT of the masked phase
  filtered_phase = np.angle(ifftn(ifftshift(fft_phase)))

  # Combine the filtered phase with the original magnitude
  filtered_complex_image = magnitude * np.exp(1j * filtered_phase)

  return filtered_complex_image

# 生成一个与图像大小相同的随机相位数组
theta = np.random.uniform(0, 2*np.pi, gray_img.shape)

# 对图像中的每个点乘以exp(j*theta)
complex_img = gray_img * np.exp(1j * theta)
# Apply the low-pass filter
filtered_img = low_pass_filter(complex_img, omega)

# 显示滤波后的图像
fig = go.Figure(data=go.Heatmap(z=filtered_img.real, colorscale='gray', showscale=False))
fig.update_layout(autosize=True)
st.plotly_chart(fig)
def plot_difference(original_picture, picture):
    # Compute the absolute difference
    difference = np.abs(original_picture.astype(int) - picture.astype(int))

    # Convert the difference to uint8
    difference = difference.astype(np.uint8)

    # Create the x, y, and z coordinate arrays
    y, x = np.mgrid[:difference.shape[0], :difference.shape[1]]
    z = difference

    # Create a 3D surface plot
    fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])

    return fig
# Create a 3D surface plot
#fig = plot_difference(original_picture, img_back)

# Update layout options
#fig.update_layout(title='灰度差异的3D图像表示', autosize=False,
#                  width=500, height=500,
#                  margin=dict(l=65, r=50, b=65, t=90))

# Display the figure
#st.plotly_chart(fig)