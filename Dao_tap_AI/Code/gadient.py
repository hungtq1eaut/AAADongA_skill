# -*- coding: utf-8 -*-
"""
Gradient Descent cho hàm 1 biến
    f(x)  = x^2 + 5 sin(x)
    f'(x) = 2x + 5 cos(x)
Cập nhật: x_{t+1} = x_t - eta * (2 x_t + 5 cos(x_t))
"""
import numpy as np
import matplotlib.pyplot as plt


def grad(x):
    return 2 * x + 5 * np.cos(x)


def cost(x):
    return x ** 2 + 5 * np.sin(x)


def myGD1(x0, eta, max_iter=100, tol=1e-3):
    x = [x0]
    for it in range(max_iter):
        x_new = x[-1] - eta * grad(x[-1])
        if abs(grad(x_new)) < tol:  # đạo hàm đủ nhỏ -> dừng
            break
        x.append(x_new)
    return (x, it)


if __name__ == "__main__":
    eta = 0.1
    results = []
    for x0 in (-5, 5):
        x, it = myGD1(x0, eta)
        results.append((x0, x))
        print(f"x0 = {x0:>3}: x* = {x[-1]:.6f}, f(x*) = {cost(x[-1]):.6f}, "
              f"sau {it} vòng lặp")

    # Vẽ đồ thị f(x) và quỹ đạo các bước GD
    xs = np.linspace(-6, 6, 400)
    plt.plot(xs, cost(xs), "k-", label="f(x) = x² + 5sin(x)")
    for x0, x in results:
        x = np.array(x)
        plt.plot(x, cost(x), "o-", ms=4, label=f"GD từ x0 = {x0}")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.title(f"Gradient Descent, eta = {eta}")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()
