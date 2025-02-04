import sys
import itertools
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QSpinBox, QTextEdit, QGridLayout,
                           QMessageBox, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import sympy as sp

class SolutionFinder(QThread):
    progress_updated = pyqtSignal(int)
    solution_found = pyqtSignal(tuple)
    calculation_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, polynomial, variables, n_start, n_end, var_range):
        super().__init__()
        self.polynomial = polynomial
        self.variables = variables
        self.n_start = n_start
        self.n_end = n_end
        self.var_range = var_range  # Değişkenlerin alabileceği değer aralığı
        self._is_running = True

    def stop(self):
        self._is_running = False

    def find_solutions_for_n(self, n_val):
        """n_val için tüm olası çözümleri bul"""
        try:
            expr = sp.sympify(self.polynomial + " - n")
            solutions = set()
            
            # Her değişken için [-var_range, var_range] aralığında değerler
            var_ranges = [list(range(-self.var_range, self.var_range + 1)) 
                       for _ in self.variables]
            
            # Tüm olası kombinasyonları dene
            for values in itertools.product(*var_ranges):
                if not self._is_running:
                    return [], n_val
                    
                try:
                    # Değerleri denkleme yerleştir
                    expr_vals = dict(zip(self.variables, values))
                    expr_vals['n'] = n_val
                    result = expr.subs(expr_vals)
                    
                    # Çözüm kontrolü
                    if abs(float(result)) < 1e-10:
                        solutions.add(values)
                except:
                    continue
                    
            return list(solutions), n_val
        except Exception as e:
            self.error_occurred.emit(f"Hesaplama hatası: {str(e)}")
            return [], n_val

    def run(self):
        try:
            total = self.n_end - self.n_start + 1
            current = 0
            
            for n_val in range(self.n_start, self.n_end + 1):
                if not self._is_running:
                    break
                    
                solutions, n = self.find_solutions_for_n(n_val)
                self.solution_found.emit((n, solutions))
                
                current += 1
                progress = int((current / total) * 100)
                self.progress_updated.emit(progress)
            
            self.calculation_finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class PolyAnalyst(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PolyAnalyst")
        self.setGeometry(100, 100, 1600, 800)
        self.solution_finder = None
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Sol Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Açıklama kutusu
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        info_layout = QVBoxLayout(info_frame)
        info_text = """
Nasıl Kullanılır:
1. Polinomu girin (örn: x**2 + y**2)
2. Değişkenleri virgülle ayırarak yazın (örn: x, y)
3. n için aralık seçin: [n_başlangıç, n_bitiş]
4. Değişkenler için aralık seçin: Her değişken [-aralık, aralık] içinde aranır
Örnek: x**2 + y**2 = 5 için
- Değişken aralığı = 5 seçerseniz, x ve y değerleri -5 ile 5 arasında aranır
"""
        info_label = QLabel(info_text)
        info_layout.addWidget(info_label)
        left_layout.addWidget(info_frame)

        # Giriş alanları
        input_group = QGridLayout()
        
        # Polinom girişi
        input_group.addWidget(QLabel("Polinom (= n formunda):"), 0, 0)
        self.poly_input = QLineEdit()
        self.poly_input.setPlaceholderText("Örnek: x**2 + y**2")
        input_group.addWidget(self.poly_input, 0, 1)
        
        # Değişkenler
        input_group.addWidget(QLabel("Değişkenler:"), 1, 0)
        self.vars_input = QLineEdit()
        self.vars_input.setPlaceholderText("x, y")
        input_group.addWidget(self.vars_input, 1, 1)
        
        # n için başlangıç
        input_group.addWidget(QLabel("n başlangıç:"), 2, 0)
        self.n_start = QSpinBox()
        self.n_start.setRange(-2147483647, 2147483647)
        self.n_start.setValue(1)
        input_group.addWidget(self.n_start, 2, 1)
        
        # n için bitiş
        input_group.addWidget(QLabel("n bitiş:"), 3, 0)
        self.n_end = QSpinBox()
        self.n_end.setRange(-2147483647, 2147483647)
        self.n_end.setValue(10)
        input_group.addWidget(self.n_end, 3, 1)
        
        # Değişkenler için aralık
        input_group.addWidget(QLabel("Değişken aralığı [-aralık, aralık]:"), 4, 0)
        self.var_range = QSpinBox()
        self.var_range.setRange(-2147483647, 2147483647)
        self.var_range.setValue(10)
        input_group.addWidget(self.var_range, 4, 1)
        
        left_layout.addLayout(input_group)

        # Progress Bar
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)

        # Butonlar
        button_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("Analiz Et")
        self.analyze_btn.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.analyze_btn)
        
        self.stop_btn = QPushButton("Durdur")
        self.stop_btn.clicked.connect(self.stop_analysis)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        left_layout.addLayout(button_layout)

        # Sonuç alanı
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        left_layout.addWidget(self.result_text)
        
        layout.addWidget(left_panel)

        # Sağ Panel (Grafik)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.figure = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)
        
        layout.addWidget(right_panel)
        
        layout.setStretch(0, 40)
        layout.setStretch(1, 60)

        # Sonuçları saklamak için liste
        self.all_results = []

    def plot_polynomial(self, expr_str, variables, n_val):
        """Polinomu görselleştir"""
        try:
            if len(variables) >= 2:  # 3D plot
                x_var, y_var = variables[:2]
                x = np.linspace(-self.var_range.value(), self.var_range.value(), 50)
                y = np.linspace(-self.var_range.value(), self.var_range.value(), 50)
                X, Y = np.meshgrid(x, y)
                
                Z = np.zeros_like(X)
                expr = sp.sympify(expr_str)
                
                for i in range(len(x)):
                    for j in range(len(y)):
                        try:
                            val = expr.subs({x_var: X[i,j], y_var: Y[i,j]})
                            Z[i,j] = float(val)
                        except:
                            Z[i,j] = np.nan
                
                self.figure.clear()
                ax = self.figure.add_subplot(111, projection='3d')
                ax.plot_surface(X, Y, Z, cmap='viridis')
                
                Zn = np.full_like(X, n_val)
                ax.plot_surface(X, Y, Zn, alpha=0.3, color='red')
                
                ax.set_xlabel(x_var)
                ax.set_ylabel(y_var)
                ax.set_zlabel('f(x,y)')
                ax.set_title(f'{expr_str} = n')
                
            elif len(variables) == 1:  # 2D plot
                x = np.linspace(-self.var_range.value(), self.var_range.value(), 200)
                expr = sp.sympify(expr_str)
                
                y = []
                for xi in x:
                    try:
                        val = float(expr.subs(variables[0], xi))
                        y.append(val)
                    except:
                        y.append(np.nan)
                
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.plot(x, y)
                ax.axhline(y=n_val, color='r', linestyle='--')
                ax.grid(True)
                ax.set_xlabel(variables[0])
                ax.set_ylabel('f(x)')
                ax.set_title(f'{expr_str} = n')
                
            self.canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Grafik çizilirken hata oluştu: {str(e)}")

    def start_analysis(self):
        try:
            # Girişleri kontrol et
            expr = self.poly_input.text().strip()
            if not expr:
                raise ValueError("Lütfen bir polinom girin")
            
            variables = [v.strip() for v in self.vars_input.text().split(',')]
            if not variables:
                raise ValueError("Lütfen değişkenleri girin")
            
            # UI'ı güncelle
            self.analyze_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setValue(0)
            self.all_results.clear()
            self.result_text.clear()
            
            # Grafiği çiz
            self.plot_polynomial(expr, variables, self.n_start.value())
            
            # Çözüm bulucuyu başlat
            self.solution_finder = SolutionFinder(
                expr,
                variables,
                self.n_start.value(),
                self.n_end.value(),
                self.var_range.value()
            )
            
            self.solution_finder.progress_updated.connect(self.update_progress)
            self.solution_finder.solution_found.connect(self.add_solution)
            self.solution_finder.calculation_finished.connect(self.show_all_results)
            self.solution_finder.error_occurred.connect(self.show_error)
            
            self.solution_finder.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def stop_analysis(self):
        if self.solution_finder:
            self.solution_finder.stop()
            self.analyze_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def add_solution(self, solution_data):
        self.all_results.append(solution_data)

    def show_error(self, message):
        QMessageBox.critical(self, "Hata", message)
        self.analyze_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def show_all_results(self):
        self.analyze_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Sonuçları sırala
        self.all_results.sort(key=lambda x: x[0])
        
        # Sonuçları göster
        text = []
        text.append(f"Polinom: {self.poly_input.text()} = n")
        text.append(f"Değişkenler: {self.vars_input.text()}")
        text.append(f"n değerleri: [{self.n_start.value()}, {self.n_end.value()}]")
        text.append(f"Değişken aralığı: [-{self.var_range.value()}, {self.var_range.value()}]")
        text.append("\nSonuçlar:")
        text.append("-" * 50)
        
        for n, solutions in self.all_results:
            text.append(f"\nn = {n}:")
            if solutions:
                text.append(f"Toplam {len(solutions)} adet {len(self.vars_input.text().split(','))}'li yazılım:")
                for sol in solutions:
                    vars_str = ", ".join(f"{var}={val}" 
                                       for var, val in zip(self.vars_input.text().split(','), sol))
                    text.append(f"  ({vars_str})")
            else:
                text.append("  Bu sayı verilen formda yazılamaz!")
        
        self.result_text.setText("\n".join(text))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PolyAnalyst()
    window.show()
    sys.exit(app.exec())