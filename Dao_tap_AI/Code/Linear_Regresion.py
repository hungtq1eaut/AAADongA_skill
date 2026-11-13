"""
Bài tập Linear Regression
- Cài đặt từ đầu bằng NumPy: Gradient Descent và Normal Equation
- So sánh với scikit-learn
- Đánh giá bằng MSE, R², vẽ đồ thị đường hồi quy và hàm mất mát
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

np.random.seed(42)

# ---------------------------------------------------------------
# 1. Tạo dữ liệu giả lập: y = 4 + 3x + nhiễu
# ---------------------------------------------------------------
X = 2 * np.random.rand(200, 1)
y = 4 + 3 * X[:, 0] + np.random.randn(200)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# ---------------------------------------------------------------
# 2. Linear Regression cài đặt từ đầu
# ---------------------------------------------------------------
class MyLinearRegression:
    def __init__(self, lr=0.05, n_iters=1000, method="gd"):
        self.lr = lr
        self.n_iters = n_iters
        self.method = method        # "gd" hoặc "normal"
        self.w = None               # trọng số
        self.b = None               # bias
        self.loss_history = []

    def fit(self, X, y):
        n_samples, n_features = X.shape

        if self.method == "normal":
            # Normal Equation: theta = (X^T X)^-1 X^T y
            Xb = np.c_[np.ones(n_samples), X]          # thêm cột 1 cho bias
            theta = np.linalg.pinv(Xb.T @ Xb) @ Xb.T @ y
            self.b, self.w = theta[0], theta[1:]
            return self

        # Gradient Descent
        self.w = np.zeros(n_features)
        self.b = 0.0
        for _ in range(self.n_iters):
            y_pred = X @ self.w + self.b
            error = y_pred - y
            # Đạo hàm của MSE theo w và b
            dw = (2 / n_samples) * (X.T @ error)
            db = (2 / n_samples) * np.sum(error)
            self.w -= self.lr * dw
            self.b -= self.lr * db
            self.loss_history.append(np.mean(error ** 2))
        return self

    def predict(self, X):
        return X @ self.w + self.b


def evaluate(name, y_true, y_pred, w, b):
    print(f"{name:<22} w = {w[0]:.4f}  b = {b:.4f}  "
          f"MSE = {mean_squared_error(y_true, y_pred):.4f}  "
          f"R² = {r2_score(y_true, y_pred):.4f}")


# ---------------------------------------------------------------
# 3. Huấn luyện và so sánh 3 cách
# ---------------------------------------------------------------
gd = MyLinearRegression(lr=0.05, n_iters=1000, method="gd").fit(X_train, y_train)
ne = MyLinearRegression(method="normal").fit(X_train, y_train)
sk = LinearRegression().fit(X_train, y_train)

print("Kết quả trên tập test (giá trị thật: w = 3, b = 4)")
evaluate("Gradient Descent", y_test, gd.predict(X_test), gd.w, gd.b)
evaluate("Normal Equation", y_test, ne.predict(X_test), ne.w, ne.b)
evaluate("scikit-learn", y_test, sk.predict(X_test), sk.coef_, sk.intercept_)

# ---------------------------------------------------------------
# 4. Vẽ đồ thị
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

x_line = np.linspace(0, 2, 100).reshape(-1, 1)
axes[0].scatter(X_train, y_train, alpha=0.5, label="Train")
axes[0].scatter(X_test, y_test, alpha=0.7, color="orange", label="Test")
axes[0].plot(x_line, gd.predict(x_line), "r-", linewidth=2, label="Gradient Descent")
axes[0].plot(x_line, sk.predict(x_line), "k--", label="scikit-learn")
axes[0].set_title("Đường hồi quy tuyến tính")
axes[0].set_xlabel("x")
axes[0].set_ylabel("y")
axes[0].legend()

axes[1].plot(gd.loss_history)
axes[1].set_title("Loss (MSE) qua các vòng lặp")
axes[1].set_xlabel("Iteration")
axes[1].set_ylabel("MSE")
axes[1].set_yscale("log")

plt.tight_layout()
plt.savefig("linear_regression.png", dpi=120)
plt.show()