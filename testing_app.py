import sys
import os
import json
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, 
                             QLabel, QVBoxLayout, QWidget, QMessageBox, QStackedWidget,
                             QHBoxLayout, QFrame, QScrollArea, QGridLayout, QRadioButton,
                             QCheckBox, QTextEdit, QComboBox, QSpinBox, QListWidget,
                             QListWidgetItem, QDialog, QFormLayout, QTabWidget)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPalette

# --- ДОБАВЛЕНО: функция для чтения csv с автоматическим определением кодировки ---
def read_csv_with_encoding(filename, sep=";"):
    encodings = ['utf-8', 'cp1251', 'latin1', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            return pd.read_csv(filename, sep=sep, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            continue
    
    # Если ничего не сработало, пробуем с обработкой ошибок
    try:
        # Читаем файл как байты и декодируем с заменой ошибок
        with open(filename, 'rb') as f:
            content = f.read()
        
        # Пробуем разные кодировки
        for encoding in encodings:
            try:
                decoded_content = content.decode(encoding, errors='replace')
                # Создаем временный файл с правильной кодировкой
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.csv') as temp_file:
                    temp_file.write(decoded_content)
                    temp_filename = temp_file.name
                
                # Читаем временный файл
                df = pd.read_csv(temp_filename, sep=sep, encoding='utf-8')
                
                # Удаляем временный файл
                import os
                os.unlink(temp_filename)
                
                return df
            except Exception:
                continue
        
        raise Exception(f"Не удалось прочитать файл {filename} ни в одной из кодировок")
    except Exception as e:
        raise Exception(f"Не удалось прочитать файл {filename}: {str(e)}")

# Константы
SOTRYDNIKI_FILE = "sotrydniki.mpp"
RESULT_FILE = "result.mpp"
TESTS_FILE = "tests.json"

def create_new_csv_file(filename, columns):
    """Создает новый CSV файл с правильной кодировкой UTF-8"""
    try:
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, sep=";", index=False, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Ошибка при создании файла {filename}: {str(e)}")
        return False

class FadeWidget(QWidget):
    """Виджет с эффектом появления"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        
    def setOpacity(self, opacity):
        self._opacity = opacity
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        super().paintEvent(event)
        
    opacity = pyqtProperty(float, fget=lambda self: self._opacity, fset=setOpacity)

class AnimatedWidget(QWidget):
    """Виджет с анимацией появления"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.0
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def setOpacity(self, opacity):
        self._opacity = opacity
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        super().paintEvent(event)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    opacity = pyqtProperty(float, fget=lambda self: self._opacity, fset=setOpacity)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система тестирования")
        self.setFixedSize(500, 400)
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        # Центральный виджет с анимацией
        central_widget = AnimatedWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Заголовок
        title_label = QLabel("Вход в систему тестирования")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title")
        main_layout.addWidget(title_label)
        
        # Форма входа
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # ФИО
        self.fio_input = QLineEdit()
        self.fio_input.setPlaceholderText("Введите ваше ФИО")
        self.fio_input.setObjectName("input_field")
        
        # Табельный номер
        self.tabnum_input = QLineEdit()
        self.tabnum_input.setPlaceholderText("Введите табельный номер")
        self.tabnum_input.setObjectName("input_field")
        
        # Кнопка входа
        self.login_btn = QPushButton("Дальше")
        self.login_btn.setObjectName("login_button")
        self.login_btn.clicked.connect(self.login)
        
        # Анимация кнопки при наведении
        self.login_btn.enterEvent = lambda event: self.animate_button(self.login_btn, True)
        self.login_btn.leaveEvent = lambda event: self.animate_button(self.login_btn, False)
        
        # Добавляем элементы в форму
        # Удаляем надписи fio_label и tabnum_label, оставляем только поля ввода
        # form_layout.addWidget(fio_label)
        form_layout.addWidget(self.fio_input)
        # form_layout.addWidget(tabnum_label)
        form_layout.addWidget(self.tabnum_input)
        form_layout.addWidget(self.login_btn)
        
        main_layout.addWidget(form_frame)
        
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a2342, stop:0.5 #173f5f, stop:1 #20639b);
            }
            
            QLabel#title {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            
            QFrame#form_frame {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            QLineEdit#input_field {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #20639b;
                border-radius: 8px;
                padding: 16px;
                font-size: 14px;
                color: #0a2342;
                min-height: 20px;
            }
            
            QLineEdit#input_field:focus {
                border-color: #3d7ea6;
                background-color: white;
            }
            
            QPushButton#login_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20639b, stop:1 #173f5f);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            
            QPushButton#login_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d7ea6, stop:1 #20639b);
            }
            
            QPushButton#login_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #173f5f, stop:1 #0a2342);
            }
            
            QLabel#hint {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                margin-top: 10px;
            }
        """)
        
    def login(self):
        fio = self.fio_input.text().strip()
        tabnum = self.tabnum_input.text().strip()
        
        if not fio or not tabnum:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")
            return
            
        try:
            if fio == "admin" and tabnum == "admin":
                # Открыть админ-панель
                self.admin_panel = AdminPanel()
                self.admin_panel.show()
                self.close()
            else:
                # Сохранить/обновить сотрудника и открыть список тестов
                if self.save_employee(fio, tabnum):
                    self.test_list = TestListWindow(fio, tabnum)
                    self.test_list.show()
                    self.close()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные сотрудника!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при входе: {str(e)}")
            
    def save_employee(self, fio, tabnum):
        """Сохраняет или обновляет данные сотрудника"""
        try:
            if os.path.exists(SOTRYDNIKI_FILE):
                df = read_csv_with_encoding(SOTRYDNIKI_FILE, sep=";")
            else:
                df = pd.DataFrame(columns=["ФИО", "Табельный номер", "Пройдено тестов"])
                
            # Проверяем, есть ли уже такой сотрудник
            mask = (df["ФИО"] == fio) & (df["Табельный номер"] == tabnum)
            if mask.any():
                # Сотрудник уже существует
                pass
            else:
                # Добавляем нового сотрудника
                new_row = pd.DataFrame([[fio, tabnum, 0]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                
            df.to_csv(SOTRYDNIKI_FILE, sep=";", index=False, encoding="utf-8")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {str(e)}")
            return False
            
    def animate_button(self, button, hover):
        """Анимация кнопки при наведении"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        current_geometry = button.geometry()
        if hover:
            # Увеличиваем кнопку при наведении
            new_geometry = current_geometry.adjusted(-2, -2, 2, 2)
        else:
            # Возвращаем к исходному размеру
            new_geometry = current_geometry.adjusted(2, 2, -2, -2)
            
        animation.setStartValue(current_geometry)
        animation.setEndValue(new_geometry)
        animation.start()

class TestListWindow(QMainWindow):
    def __init__(self, fio, tabnum):
        super().__init__()
        self.fio = fio
        self.tabnum = tabnum
        self.setWindowTitle("Список тестов")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_tests()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel(f"Добро пожаловать, {self.fio}!")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Список тестов
        self.test_list = QListWidget()
        self.test_list.setObjectName("test_list")
        layout.addWidget(self.test_list)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Начать тест")
        self.start_btn.setObjectName("action_button")
        self.start_btn.clicked.connect(self.start_test)
        
        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.setObjectName("logout_button")
        self.logout_btn.clicked.connect(self.logout)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.logout_btn)
        layout.addLayout(btn_layout)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a2342, stop:1 #173f5f);
            }
            
            QLabel#title {
                color: white;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            QListWidget#test_list {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #20639b;
                border-radius: 8px;
                font-size: 14px;
                color: #0a2342;
            }
            
            QPushButton#action_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20639b, stop:1 #173f5f);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#logout_button {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
            }
        """)
        
    def load_tests(self):
        """Загружает список тестов из JSON файла"""
        try:
            if os.path.exists(TESTS_FILE):
                with open(TESTS_FILE, 'r', encoding='utf-8') as f:
                    tests_data = json.load(f)
                    
                for test in tests_data.get('tests', []):
                    item = QListWidgetItem(f"{test['name']} - {test['description']}")
                    item.setData(Qt.ItemDataRole.UserRole, test)
                    self.test_list.addItem(item)
            else:
                # Создаем тестовые данные
                self.create_sample_tests()
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке тестов: {str(e)}")
            
    def create_sample_tests(self):
        """Создает примеры тестов"""
        sample_tests = {
            "tests": [
                {
                    "id": 1,
                    "name": "Основы безопасности",
                    "description": "Тест по основам безопасности труда",
                    "questions": [
                        {
                            "id": 1,
                            "type": "single",
                            "text": "Какой цвет имеет предупреждающий знак?",
                            "options": ["Красный", "Желтый", "Зеленый", "Синий"],
                            "correct": 1
                        },
                        {
                            "id": 2,
                            "type": "multiple",
                            "text": "Какие средства защиты необходимо использовать при работе с химикатами?",
                            "options": ["Перчатки", "Очки", "Респиратор", "Каска"],
                            "correct": [0, 1, 2]
                        },
                        {
                            "id": 3,
                            "type": "matching",
                            "text": "Сопоставьте знаки безопасности с их значениями:",
                            "left_items": ["Огнеопасно", "Токсично", "Радиация"],
                            "right_items": ["Может вызвать отравление", "Может загореться", "Опасное излучение"],
                            "correct": [1, 0, 2]
                        },
                        {
                            "id": 4,
                            "type": "sequence",
                            "text": "Установите правильную последовательность действий при эвакуации:",
                            "items": ["Покинуть помещение", "Вызвать пожарных", "Оповестить окружающих", "Собраться в безопасном месте"],
                            "correct": [2, 0, 1, 3]
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "Правила пожарной безопасности",
                    "description": "Тест по правилам пожарной безопасности",
                    "questions": [
                        {
                            "id": 1,
                            "type": "single",
                            "text": "Что делать при обнаружении пожара?",
                            "options": ["Спасаться бегством", "Вызвать пожарных", "Попытаться потушить", "Все вышеперечисленное"],
                            "correct": 3
                        },
                        {
                            "id": 2,
                            "type": "multiple",
                            "text": "Какие действия запрещены при пожаре?",
                            "options": ["Использовать лифт", "Открывать окна", "Пользоваться огнетушителем", "Прятаться в шкафу"],
                            "correct": [0, 1, 3]
                        }
                    ]
                }
            ]
        }
        
        with open(TESTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sample_tests, f, ensure_ascii=False, indent=2)
            
        self.load_tests()
        
    def start_test(self):
        """Начинает выбранный тест"""
        current_item = self.test_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите тест!")
            return
            
        test_data = current_item.data(Qt.ItemDataRole.UserRole)
        self.test_window = TestWindow(test_data, self.fio, self.tabnum)
        self.test_window.show()
        self.close()
        
    def logout(self):
        """Выход из системы"""
        self.close()
        login_window = LoginWindow()
        login_window.show()

class TestWindow(QMainWindow):
    def __init__(self, test_data, fio, tabnum):
        super().__init__()
        self.test_data = test_data
        self.fio = fio
        self.tabnum = tabnum
        self.current_question = 0
        self.answers = []
        
        self.setWindowTitle(f"Тест: {test_data['name']}")
        self.setFixedSize(900, 700)
        self.setup_ui()
        self.show_question()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Прогресс
        self.progress_label = QLabel()
        self.progress_label.setObjectName("progress")
        layout.addWidget(self.progress_label)
        
        # Вопрос
        self.question_label = QLabel()
        self.question_label.setObjectName("question")
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)
        
        # Контейнер для вариантов ответов
        self.answers_widget = QWidget()
        self.answers_layout = QVBoxLayout(self.answers_widget)
        layout.addWidget(self.answers_widget)
        
        # Кнопки навигации
        btn_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Назад")
        self.prev_btn.setObjectName("nav_button")
        self.prev_btn.clicked.connect(self.previous_question)
        
        self.next_btn = QPushButton("Далее")
        self.next_btn.setObjectName("nav_button")
        self.next_btn.clicked.connect(self.next_question)
        
        self.finish_btn = QPushButton("Завершить тест")
        self.finish_btn.setObjectName("finish_button")
        self.finish_btn.clicked.connect(self.finish_test)
        self.finish_btn.hide()
        
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)
        btn_layout.addWidget(self.finish_btn)
        layout.addLayout(btn_layout)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a2342, stop:1 #173f5f);
            }
            
            QLabel#progress {
                color: white;
                font-size: 14px;
                margin-bottom: 10px;
            }
            
            QLabel#question {
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin: 20px 0;
                padding: 15px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
            
            QRadioButton, QCheckBox {
                color: white;
                font-size: 14px;
                margin: 5px 0;
            }
            
            QLabel#matching_item {
                color: white;
                font-size: 14px;
                margin: 5px 0;
                padding: 5px;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
            
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #20639b;
                border-radius: 5px;
                padding: 5px;
                color: #0a2342;
                font-size: 14px;
            }
            
            QSpinBox {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #20639b;
                border-radius: 5px;
                padding: 5px;
                color: #0a2342;
                font-size: 14px;
            }
            
            QPushButton#nav_button {
                background-color: #20639b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            
            QPushButton#finish_button {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
    def show_question(self):
        """Показывает текущий вопрос"""
        questions = self.test_data['questions']
        if self.current_question >= len(questions):
            return
            
        question = questions[self.current_question]
        
        # Обновляем прогресс
        self.progress_label.setText(f"Вопрос {self.current_question + 1} из {len(questions)}")
        
        # Показываем вопрос
        self.question_label.setText(question['text'])
        
        # Очищаем предыдущие варианты ответов
        for i in reversed(range(self.answers_layout.count())):
            self.answers_layout.itemAt(i).widget().setParent(None)
            
        # Создаем варианты ответов в зависимости от типа вопроса
        if question['type'] == 'single':
            self.create_single_choice(question)
        elif question['type'] == 'multiple':
            self.create_multiple_choice(question)
        elif question['type'] == 'matching':
            self.create_matching_question(question)
        elif question['type'] == 'sequence':
            self.create_sequence_question(question)
        else:
            # Неизвестный тип вопроса
            self.create_single_choice(question)
        
        # Обновляем кнопки
        self.prev_btn.setEnabled(self.current_question > 0)
        if self.current_question == len(questions) - 1:
            self.next_btn.hide()
            self.finish_btn.show()
        else:
            self.next_btn.show()
            self.finish_btn.hide()
            
    def create_single_choice(self, question):
        """Создает варианты ответов для вопроса с одним правильным ответом"""
        self.answer_widgets = []
        for i, option in enumerate(question['options']):
            radio = QRadioButton(option)
            radio.setObjectName("answer_option")
            self.answer_widgets.append(radio)
            self.answers_layout.addWidget(radio)
            
    def create_multiple_choice(self, question):
        """Создает варианты ответов для вопроса с несколькими правильными ответами"""
        self.answer_widgets = []
        for i, option in enumerate(question['options']):
            checkbox = QCheckBox(option)
            checkbox.setObjectName("answer_option")
            self.answer_widgets.append(checkbox)
            self.answers_layout.addWidget(checkbox)
            
    def create_matching_question(self, question):
        """Создает вопрос на сопоставление"""
        self.answer_widgets = []
        
        # Создаем два столбца
        layout = QHBoxLayout()
        
        # Левый столбец
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Левая колонка:"))
        self.left_items = []
        for i, item in enumerate(question['left_items']):
            label = QLabel(f"{i+1}. {item}")
            label.setObjectName("matching_item")
            self.left_items.append(label)
            left_layout.addWidget(label)
        layout.addLayout(left_layout)
        
        # Правый столбец с комбобоксами
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Правая колонка:"))
        self.matching_combos = []
        for i in range(len(question['left_items'])):
            combo = QComboBox()
            combo.addItem("Выберите ответ")
            for j, item in enumerate(question['right_items']):
                combo.addItem(f"{j+1}. {item}")
            self.matching_combos.append(combo)
            self.answer_widgets.append(combo)
            right_layout.addWidget(combo)
        layout.addLayout(right_layout)
        
        self.answers_layout.addLayout(layout)
        
    def create_sequence_question(self, question):
        """Создает вопрос на установку последовательности"""
        self.answer_widgets = []
        
        # Создаем спинбоксы для каждого элемента
        for i, item in enumerate(question['items']):
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f"{i+1}. {item}"))
            spinbox = QSpinBox()
            spinbox.setRange(1, len(question['items']))
            spinbox.setValue(i+1)
            spinbox.setObjectName("sequence_spinbox")
            self.answer_widgets.append(spinbox)
            layout.addWidget(spinbox)
            self.answers_layout.addLayout(layout)
            
    def save_current_answer(self):
        """Сохраняет ответ на текущий вопрос"""
        questions = self.test_data['questions']
        if self.current_question >= len(questions):
            return
            
        question = questions[self.current_question]
        
        if question['type'] == 'single':
            # Находим выбранный радиокнопка
            selected = None
            for i, widget in enumerate(self.answer_widgets):
                if widget.isChecked():
                    selected = i
                    break
            self.answers.append(selected)
            
        elif question['type'] == 'multiple':
            # Находим все выбранные чекбоксы
            selected = []
            for i, widget in enumerate(self.answer_widgets):
                if widget.isChecked():
                    selected.append(i)
            self.answers.append(selected)
        elif question['type'] == 'matching':
            # Сохраняем выбранные индексы из комбобоксов
            selected = []
            for combo in self.matching_combos:
                index = combo.currentIndex() - 1  # -1 потому что первый элемент "Выберите ответ"
                selected.append(index if index >= 0 else None)
            self.answers.append(selected)
        elif question['type'] == 'sequence':
            # Сохраняем порядок из спинбоксов
            sequence = []
            for spinbox in self.answer_widgets:
                sequence.append(spinbox.value() - 1)  # -1 для индексации с 0
            self.answers.append(sequence)
            
    def previous_question(self):
        """Переход к предыдущему вопросу"""
        if self.current_question > 0:
            self.save_current_answer()
            self.current_question -= 1
            self.show_question()
            
    def next_question(self):
        """Переход к следующему вопросу"""
        questions = self.test_data['questions']
        if self.current_question < len(questions) - 1:
            self.save_current_answer()
            self.current_question += 1
            self.show_question()
            
    def finish_test(self):
        """Завершает тест и показывает результаты"""
        self.save_current_answer()
        
        # Подсчитываем результаты
        questions = self.test_data['questions']
        correct_answers = 0
        
        for i, (question, answer) in enumerate(zip(questions, self.answers)):
            if question['type'] == 'single':
                if answer == question['correct']:
                    correct_answers += 1
            elif question['type'] == 'multiple':
                if answer == question['correct']:
                    correct_answers += 1
            elif question['type'] == 'matching':
                if answer == question['correct']:
                    correct_answers += 1
            elif question['type'] == 'sequence':
                if answer == question['correct']:
                    correct_answers += 1
                    
        percentage = (correct_answers / len(questions)) * 100
        
        # Сохраняем результат
        self.save_result(percentage)
        
        # Показываем результат
        QMessageBox.information(self, "Результат", 
                              f"Тест завершен!\nПравильных ответов: {correct_answers}/{len(questions)}\nПроцент: {percentage:.1f}%")
        
        # Возвращаемся к списку тестов
        self.test_list = TestListWindow(self.fio, self.tabnum)
        self.test_list.show()
        self.close()
        
    def save_result(self, percentage):
        """Сохраняет результат теста"""
        try:
            # Сохраняем в result.mpp
            result_data = {
                "Название теста": self.test_data['name'],
                "ФИО и табельный номер": f"{self.fio} ({self.tabnum})",
                "Результат": f"{percentage:.1f}%",
                "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Пытаемся прочитать существующий файл
            df = None
            if os.path.exists(RESULT_FILE):
                try:
                    df = read_csv_with_encoding(RESULT_FILE, sep=";")
                except Exception as e:
                    print(f"Ошибка чтения файла {RESULT_FILE}: {str(e)}")
                    # Создаем новый файл с правильной структурой
                    df = pd.DataFrame(columns=["Название теста", "ФИО и табельный номер", "Результат", "Дата"])
            else:
                df = pd.DataFrame(columns=["Название теста", "ФИО и табельный номер", "Результат", "Дата"])
                
            new_row = pd.DataFrame([result_data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(RESULT_FILE, sep=";", index=False, encoding="utf-8")
            
            # Обновляем количество пройденных тестов в sotrydniki.mpp
            if os.path.exists(SOTRYDNIKI_FILE):
                try:
                    df_sotr = read_csv_with_encoding(SOTRYDNIKI_FILE, sep=";")
                    mask = (df_sotr["ФИО"] == self.fio) & (df_sotr["Табельный номер"] == self.tabnum)
                    if mask.any():
                        df_sotr.loc[mask, "Пройдено тестов"] += 1
                        df_sotr.to_csv(SOTRYDNIKI_FILE, sep=";", index=False, encoding="utf-8")
                except Exception as e:
                    print(f"Ошибка обновления sotrydniki.mpp: {str(e)}")
                    # Не прерываем сохранение результата из-за ошибки обновления статистики
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении результата: {str(e)}")

class AddTestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить тест")
        self.setFixedSize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Название теста
        layout.addWidget(QLabel("Название теста:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Описание теста
        layout.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # Список вопросов
        layout.addWidget(QLabel("Вопросы:"))
        self.questions_list = QListWidget()
        layout.addWidget(self.questions_list)
        
        # Кнопки для вопросов
        btn_layout = QHBoxLayout()
        add_q_btn = QPushButton("Добавить вопрос")
        add_q_btn.clicked.connect(self.add_question)
        edit_q_btn = QPushButton("Редактировать вопрос")
        edit_q_btn.clicked.connect(self.edit_question)
        delete_q_btn = QPushButton("Удалить вопрос")
        delete_q_btn.clicked.connect(self.delete_question)
        
        btn_layout.addWidget(add_q_btn)
        btn_layout.addWidget(edit_q_btn)
        btn_layout.addWidget(delete_q_btn)
        layout.addLayout(btn_layout)
        
        # Кнопки диалога
        dialog_btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        dialog_btn_layout.addWidget(ok_btn)
        dialog_btn_layout.addWidget(cancel_btn)
        layout.addLayout(dialog_btn_layout)
        
        self.questions = []
        
    def refresh_questions_list(self):
        """Обновляет список вопросов"""
        self.questions_list.clear()
        for i, question in enumerate(self.questions):
            item = QListWidgetItem(f"Вопрос {i+1}: {question.get('text', '')[:50]}...")
            item.setData(Qt.ItemDataRole.UserRole, i)  # Индекс вопроса
            self.questions_list.addItem(item)
        
    def add_question(self):
        """Добавляет новый вопрос"""
        dialog = QuestionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            question_data = dialog.get_question_data()
            if question_data:
                # Генерируем ID для нового вопроса
                max_id = max([q.get('id', 0) for q in self.questions], default=0)
                question_data['id'] = max_id + 1
                self.questions.append(question_data)
                self.refresh_questions_list()
                
    def edit_question(self):
        """Редактирует выбранный вопрос"""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите вопрос для редактирования!")
            return
            
        question_index = current_item.data(Qt.ItemDataRole.UserRole)
        question_data = self.questions[question_index]
        
        dialog = QuestionDialog(self, question_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_question_data = dialog.get_question_data()
            if new_question_data:
                new_question_data['id'] = question_data['id']  # Сохраняем ID
                self.questions[question_index] = new_question_data
                self.refresh_questions_list()
                
    def delete_question(self):
        """Удаляет выбранный вопрос"""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите вопрос для удаления!")
            return
            
        reply = QMessageBox.question(self, "Подтверждение", 
                                   "Вы уверены, что хотите удалить этот вопрос?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            question_index = current_item.data(Qt.ItemDataRole.UserRole)
            del self.questions[question_index]
            self.refresh_questions_list()
        
    def get_test_data(self):
        return {
            "name": self.name_edit.text(),
            "description": self.desc_edit.toPlainText(),
            "questions": self.questions
        }

class EditTestDialog(QDialog):
    def __init__(self, test_data, parent=None):
        super().__init__(parent)
        self.test_data = test_data.copy()  # Копируем данные теста
        self.setWindowTitle("Редактировать тест")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_test_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Название теста
        layout.addWidget(QLabel("Название теста:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Описание теста
        layout.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # Список вопросов
        layout.addWidget(QLabel("Вопросы:"))
        self.questions_list = QListWidget()
        layout.addWidget(self.questions_list)
        
        # Кнопки для вопросов
        btn_layout = QHBoxLayout()
        add_q_btn = QPushButton("Добавить вопрос")
        add_q_btn.clicked.connect(self.add_question)
        edit_q_btn = QPushButton("Редактировать вопрос")
        edit_q_btn.clicked.connect(self.edit_question)
        delete_q_btn = QPushButton("Удалить вопрос")
        delete_q_btn.clicked.connect(self.delete_question)
        
        btn_layout.addWidget(add_q_btn)
        btn_layout.addWidget(edit_q_btn)
        btn_layout.addWidget(delete_q_btn)
        layout.addLayout(btn_layout)
        
        # Кнопки диалога
        dialog_btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        dialog_btn_layout.addWidget(ok_btn)
        dialog_btn_layout.addWidget(cancel_btn)
        layout.addLayout(dialog_btn_layout)
        
    def load_test_data(self):
        """Загружает данные теста в форму"""
        self.name_edit.setText(self.test_data.get('name', ''))
        self.desc_edit.setPlainText(self.test_data.get('description', ''))
        self.refresh_questions_list()
        
    def refresh_questions_list(self):
        """Обновляет список вопросов"""
        self.questions_list.clear()
        for i, question in enumerate(self.test_data.get('questions', [])):
            item = QListWidgetItem(f"Вопрос {i+1}: {question.get('text', '')[:50]}...")
            item.setData(Qt.ItemDataRole.UserRole, i)  # Индекс вопроса
            self.questions_list.addItem(item)
            
    def add_question(self):
        """Добавляет новый вопрос"""
        dialog = QuestionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            question_data = dialog.get_question_data()
            if question_data:
                # Генерируем ID для нового вопроса
                max_id = max([q.get('id', 0) for q in self.test_data.get('questions', [])], default=0)
                question_data['id'] = max_id + 1
                self.test_data['questions'].append(question_data)
                self.refresh_questions_list()
                
    def edit_question(self):
        """Редактирует выбранный вопрос"""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите вопрос для редактирования!")
            return
            
        question_index = current_item.data(Qt.ItemDataRole.UserRole)
        question_data = self.test_data['questions'][question_index]
        
        dialog = QuestionDialog(self, question_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_question_data = dialog.get_question_data()
            if new_question_data:
                new_question_data['id'] = question_data['id']  # Сохраняем ID
                self.test_data['questions'][question_index] = new_question_data
                self.refresh_questions_list()
                
    def delete_question(self):
        """Удаляет выбранный вопрос"""
        current_item = self.questions_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите вопрос для удаления!")
            return
            
        reply = QMessageBox.question(self, "Подтверждение", 
                                   "Вы уверены, что хотите удалить этот вопрос?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            question_index = current_item.data(Qt.ItemDataRole.UserRole)
            del self.test_data['questions'][question_index]
            self.refresh_questions_list()
            
    def get_test_data(self):
        """Возвращает обновленные данные теста"""
        return {
            'id': self.test_data.get('id'),
            'name': self.name_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'questions': self.test_data.get('questions', [])
        }

class QuestionDialog(QDialog):
    def __init__(self, parent=None, question_data=None):
        super().__init__(parent)
        self.question_data = question_data or {}
        self.setWindowTitle("Вопрос")
        self.setFixedSize(600, 500)
        self.setup_ui()
        if question_data:
            self.load_question_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Тип вопроса:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Один ответ", "Несколько ответов", "Сопоставление", "Последовательность"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Текст вопроса:"))
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(100)
        layout.addWidget(self.text_edit)
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        layout.addWidget(self.options_widget)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Сохранить")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        # НЕ вызываем on_type_changed здесь!

    def on_type_changed(self, question_type):
        # Очищаем предыдущие опции
        for i in reversed(range(self.options_layout.count())):
            item = self.options_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                self.options_layout.removeItem(item)
        if question_type == "Один ответ":
            self.setup_single_choice()
        elif question_type == "Несколько ответов":
            self.setup_multiple_choice()
        elif question_type == "Сопоставление":
            self.setup_matching()
        elif question_type == "Последовательность":
            self.setup_sequence()

    def setup_single_choice(self):
        """Настройка для вопроса с одним ответом"""
        self.options_edits = []
        self.correct_combo = QComboBox()
        
        # Опции
        for i in range(4):
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f"Опция {i+1}:"))
            edit = QLineEdit()
            self.options_edits.append(edit)
            layout.addWidget(edit)
            self.options_layout.addLayout(layout)
            
        # Правильный ответ
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Правильный ответ:"))
        self.correct_combo.addItems(["Опция 1", "Опция 2", "Опция 3", "Опция 4"])
        layout.addWidget(self.correct_combo)
        self.options_layout.addLayout(layout)
        
    def setup_multiple_choice(self):
        """Настройка для вопроса с несколькими вариантами ответа (от 2 до 10)"""
        self.options_edits = []
        self.correct_checkboxes = []
        self.multiple_rows = []
        self.multiple_count = 4  # по умолчанию 4 варианта
        def add_option_row():
            if len(self.options_edits) >= 10:
                return
            row_layout = QHBoxLayout()
            edit = QLineEdit()
            checkbox = QCheckBox("Правильный")
            self.options_edits.append(edit)
            self.correct_checkboxes.append(checkbox)
            row_layout.addWidget(edit)
            row_layout.addWidget(checkbox)
            # Кнопка удалить
            del_btn = QPushButton("–")
            del_btn.setFixedWidth(30)
            def remove_row():
                idx = self.multiple_rows.index(row_layout)
                for w in [edit, checkbox, del_btn]:
                    w.deleteLater()
                self.options_edits.pop(idx)
                self.correct_checkboxes.pop(idx)
                self.options_layout.removeItem(row_layout)
                self.multiple_rows.remove(row_layout)
            del_btn.clicked.connect(remove_row)
            row_layout.addWidget(del_btn)
            self.options_layout.addLayout(row_layout)
            self.multiple_rows.append(row_layout)
        # Кнопка добавить
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(30)
        def add_btn_clicked():
            add_option_row()
        add_btn.clicked.connect(add_btn_clicked)
        self.options_layout.addWidget(add_btn)
        # Добавляем стартовые строки
        for _ in range(self.multiple_count):
            add_option_row()

    def setup_matching(self):
        """Настройка для вопроса на сопоставление (одна строка = одна пара)"""
        self.left_edits = []
        self.right_edits = []
        self.correct_combos = []
        self.matching_rows = []
        self.matching_count = 3  # по умолчанию 3 пары

        def add_matching_row():
            if len(self.matching_rows) >= 10:
                return
            row_layout = QHBoxLayout()
            left_edit = QLineEdit()
            right_edit = QLineEdit()
            combo = QComboBox()
            # ComboBox будет обновляться после каждого добавления/удаления строки
            self.left_edits.append(left_edit)
            self.right_edits.append(right_edit)
            self.correct_combos.append(combo)
            row_layout.addWidget(left_edit)
            row_layout.addWidget(QLabel("⇄"))
            row_layout.addWidget(right_edit)
            row_layout.addWidget(QLabel("Правильная пара:"))
            row_layout.addWidget(combo)
            # Кнопка удалить
            del_btn = QPushButton("–")
            del_btn.setFixedWidth(30)
            def remove_row():
                idx = self.matching_rows.index(row_layout)
                for w in [left_edit, right_edit, combo, del_btn]:
                    w.deleteLater()
                self.left_edits.pop(idx)
                self.right_edits.pop(idx)
                self.correct_combos.pop(idx)
                self.options_layout.removeItem(row_layout)
                self.matching_rows.remove(row_layout)
                update_combos()
            del_btn.clicked.connect(remove_row)
            row_layout.addWidget(del_btn)
            self.options_layout.addLayout(row_layout)
            self.matching_rows.append(row_layout)
            update_combos()
        def update_combos():
            # В каждом ComboBox должны быть варианты по количеству строк
            n = len(self.left_edits)
            for combo in self.correct_combos:
                combo.clear()
                combo.addItems([f"{i+1}" for i in range(n)])
        # Кнопка добавить
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(30)
        def add_btn_clicked():
            add_matching_row()
        add_btn.clicked.connect(add_btn_clicked)
        self.options_layout.addWidget(add_btn)
        # Добавляем стартовые строки
        for _ in range(self.matching_count):
            add_matching_row()

    def setup_sequence(self):
        """Настройка для вопроса на последовательность"""
        self.items_edits = []
        self.sequence_edits = []
        
        # Элементы
        for i in range(4):
            layout = QHBoxLayout()
            layout.addWidget(QLabel(f"Элемент {i+1}:"))
            edit = QLineEdit()
            self.items_edits.append(edit)
            layout.addWidget(edit)
            
            sequence_edit = QLineEdit()
            sequence_edit.setPlaceholderText(f"Порядок {i+1}")
            self.sequence_edits.append(sequence_edit)
            layout.addWidget(sequence_edit)
            self.options_layout.addLayout(layout)
            
    def load_question_data(self):
        """Загружает данные вопроса в форму"""
        try:
            question_type = self.question_data.get('type', 'single')
            type_mapping = {
                'single': "Один ответ",
                'multiple': "Несколько ответов",
                'matching': "Сопоставление",
                'sequence': "Последовательность"
            }
            # Сначала вызываем on_type_changed для правильного типа
            self.type_combo.setCurrentText(type_mapping.get(question_type, "Один ответ"))
            self.on_type_changed(type_mapping.get(question_type, "Один ответ"))
            # Теперь заполняем поля
            self.text_edit.setPlainText(self.question_data.get('text', ''))
            if question_type == 'single':
                options = self.question_data.get('options', [])
                for i, edit in enumerate(getattr(self, 'options_edits', [])):
                    if i < len(options):
                        edit.setText(options[i])
                correct = self.question_data.get('correct', 0)
                if hasattr(self, 'correct_combo') and self.correct_combo.count() > 0:
                    if 0 <= correct < self.correct_combo.count():
                        self.correct_combo.setCurrentIndex(correct)
            elif question_type == 'multiple':
                options = self.question_data.get('options', [])
                correct = self.question_data.get('correct', [])
                for i, edit in enumerate(getattr(self, 'options_edits', [])):
                    if i < len(options):
                        edit.setText(options[i])
                    if hasattr(self, 'correct_checkboxes') and i < len(self.correct_checkboxes):
                        self.correct_checkboxes[i].setChecked(i in correct)
            elif question_type == 'matching':
                left_items = self.question_data.get('left_items', [])
                right_items = self.question_data.get('right_items', [])
                correct = self.question_data.get('correct', [])
                for i, edit in enumerate(getattr(self, 'left_edits', [])):
                    if i < len(left_items):
                        edit.setText(left_items[i])
                for i, edit in enumerate(getattr(self, 'right_edits', [])):
                    if i < len(right_items):
                        edit.setText(right_items[i])
                for i, combo in enumerate(getattr(self, 'correct_combos', [])):
                    if i < len(correct):
                        combo.setCurrentIndex(correct[i])
            elif question_type == 'sequence':
                items = self.question_data.get('items', [])
                correct = self.question_data.get('correct', [])
                for i, edit in enumerate(getattr(self, 'items_edits', [])):
                    if i < len(items):
                        edit.setText(items[i])
                for i, edit in enumerate(getattr(self, 'sequence_edits', [])):
                    if i < len(correct):
                        edit.setText(str(correct[i] + 1))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке вопроса: {str(e)}")
            
    def get_question_data(self):
        """Возвращает данные вопроса"""
        question_type = self.type_combo.currentText()
        text = self.text_edit.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите текст вопроса!")
            return None
            
        type_mapping = {
            "Один ответ": "single",
            "Несколько ответов": "multiple",
            "Сопоставление": "matching", 
            "Последовательность": "sequence"
        }
        
        question_data = {
            'type': type_mapping[question_type],
            'text': text
        }
        
        if question_type == "Один ответ":
            if not hasattr(self, 'options_edits') or not self.options_edits:
                QMessageBox.warning(self, "Ошибка", "Опции не инициализированы!")
                return None
            options = [edit.text().strip() for edit in self.options_edits]
            if not all(options):
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все опции!")
                return None
            question_data['options'] = options
            if hasattr(self, 'correct_combo'):
                question_data['correct'] = self.correct_combo.currentIndex()
            else:
                question_data['correct'] = 0
            
        elif question_type == "Несколько ответов":
            if not hasattr(self, 'options_edits') or not self.options_edits:
                QMessageBox.warning(self, "Ошибка", "Опции не инициализированы!")
                return None
            options = [edit.text().strip() for edit in self.options_edits]
            if not all(options):
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все опции!")
                return None
            question_data['options'] = options
            if hasattr(self, 'correct_checkboxes'):
                question_data['correct'] = [i for i, cb in enumerate(self.correct_checkboxes) if cb.isChecked()]
            else:
                question_data['correct'] = []
            
        elif question_type == "Сопоставление":
            if not hasattr(self, 'left_edits') or not hasattr(self, 'right_edits') or not hasattr(self, 'correct_combos'):
                QMessageBox.warning(self, "Ошибка", "Элементы сопоставления не инициализированы!")
                return None
            left_items = [edit.text().strip() for edit in self.left_edits]
            right_items = [edit.text().strip() for edit in self.right_edits]
            if not all(left_items) or not all(right_items):
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все элементы!")
                return None
            question_data['left_items'] = left_items
            question_data['right_items'] = right_items
            question_data['correct'] = [combo.currentIndex() for combo in self.correct_combos]
            
        elif question_type == "Последовательность":
            if not hasattr(self, 'items_edits') or not hasattr(self, 'sequence_edits'):
                QMessageBox.warning(self, "Ошибка", "Элементы последовательности не инициализированы!")
                return None
            items = [edit.text().strip() for edit in self.items_edits]
            if not all(items):
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все элементы!")
                return None
            question_data['items'] = items
            
            # Парсим последовательность
            sequence = []
            for edit in self.sequence_edits:
                try:
                    value = int(edit.text().strip()) - 1  # -1 для индексации с 0
                    sequence.append(value)
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректные номера последовательности!")
                    return None
            question_data['correct'] = sequence
            
        return question_data

class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.setFixedSize(1000, 700)
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("Панель администратора")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tab_widget")
        
        # Вкладка управления тестами
        self.tests_tab = QWidget()
        self.setup_tests_tab()
        self.tab_widget.addTab(self.tests_tab, "Управление тестами")
        
        # Вкладка статистики
        self.stats_tab = QWidget()
        self.setup_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "Статистика")
        
        layout.addWidget(self.tab_widget)
        
        # Кнопка выхода
        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.setObjectName("logout_button")
        self.logout_btn.clicked.connect(self.logout)
        layout.addWidget(self.logout_btn)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a2342, stop:1 #173f5f);
            }
            
            QLabel#title {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            
            QTabWidget::pane {
                border: 2px solid #20639b;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            
            QTabBar::tab {
                background-color: #173f5f;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            QTabBar::tab:selected {
                background-color: #20639b;
            }
            
            QPushButton#logout_button {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
            }
        """)
        
    def setup_tests_tab(self):
        """Настраивает вкладку управления тестами"""
        layout = QVBoxLayout(self.tests_tab)
        
        # Список тестов
        self.tests_list = QListWidget()
        layout.addWidget(QLabel("Список тестов:"))
        layout.addWidget(self.tests_list)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Добавить тест")
        add_btn.clicked.connect(self.add_test)
        
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_test)
        
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_test)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        self.load_tests_list()
        
    def setup_stats_tab(self):
        """Настраивает вкладку статистики"""
        layout = QVBoxLayout(self.stats_tab)
        
        # Статистика сотрудников
        layout.addWidget(QLabel("Статистика сотрудников:"))
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        self.load_stats()
        
    def load_tests_list(self):
        """Загружает список тестов в админ-панель"""
        try:
            if os.path.exists(TESTS_FILE):
                with open(TESTS_FILE, 'r', encoding='utf-8') as f:
                    tests_data = json.load(f)
                    
                self.tests_list.clear()
                for test in tests_data.get('tests', []):
                    item = QListWidgetItem(f"{test['name']} - {test['description']}")
                    item.setData(Qt.ItemDataRole.UserRole, test)
                    self.tests_list.addItem(item)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке тестов: {str(e)}")
            
    def load_stats(self):
        """Загружает статистику"""
        try:
            if os.path.exists(SOTRYDNIKI_FILE):
                try:
                    df = read_csv_with_encoding(SOTRYDNIKI_FILE, sep=";")
                    stats_text = "Статистика сотрудников:\n\n"
                    
                    for _, row in df.iterrows():
                        try:
                            fio = str(row['ФИО']) if pd.notna(row['ФИО']) else "Не указано"
                            tabnum = str(row['Табельный номер']) if pd.notna(row['Табельный номер']) else "Не указано"
                            tests = str(row['Пройдено тестов']) if pd.notna(row['Пройдено тестов']) else "0"
                            
                            stats_text += f"ФИО: {fio}\n"
                            stats_text += f"Табельный номер: {tabnum}\n"
                            stats_text += f"Пройдено тестов: {tests}\n"
                            stats_text += "-" * 30 + "\n"
                        except Exception as row_error:
                            stats_text += f"Ошибка при обработке строки: {str(row_error)}\n"
                            stats_text += "-" * 30 + "\n"
                        
                    self.stats_text.setText(stats_text)
                except Exception as read_error:
                    # Если файл повреждён, создаём новый
                    reply = QMessageBox.question(self, "Ошибка чтения файла", 
                                               f"Файл {SOTRYDNIKI_FILE} повреждён или имеет неподдерживаемую кодировку.\n\nСоздать новый файл?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        # Создаём новый файл
                        if create_new_csv_file(SOTRYDNIKI_FILE, ["ФИО", "Табельный номер", "Пройдено тестов"]):
                            self.stats_text.setText("Создан новый файл с данными сотрудников.\nФайл готов к использованию.")
                        else:
                            self.stats_text.setText("Не удалось создать новый файл.")
                    else:
                        self.stats_text.setText(f"Ошибка при загрузке статистики: {str(read_error)}")
            else:
                # Создаём новый файл, если его нет
                if create_new_csv_file(SOTRYDNIKI_FILE, ["ФИО", "Табельный номер", "Пройдено тестов"]):
                    self.stats_text.setText("Создан новый файл с данными сотрудников.\nФайл готов к использованию.")
                else:
                    self.stats_text.setText("Не удалось создать файл с данными сотрудников.")
                
        except Exception as e:
            self.stats_text.setText(f"Ошибка при загрузке статистики: {str(e)}\n\nПопробуйте перезапустить приложение.")
            
    def add_test(self):
        """Добавляет новый тест"""
        dialog = AddTestDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            test_data = dialog.get_test_data()
            if test_data["name"] and test_data["description"]:
                self.save_test(test_data)
                self.load_tests_list()
                QMessageBox.information(self, "Успех", "Тест успешно добавлен!")
            else:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните название и описание теста!")
        
    def edit_test(self):
        """Редактирует выбранный тест"""
        current_item = self.tests_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите тест для редактирования!")
            return
            
        test_data = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = EditTestDialog(test_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_test_data = dialog.get_test_data()
            if updated_test_data["name"] and updated_test_data["description"]:
                self.save_test(updated_test_data)
                self.load_tests_list()
                QMessageBox.information(self, "Успех", "Тест успешно отредактирован!")
            else:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните название и описание теста!")
        
    def delete_test(self):
        """Удаляет выбранный тест"""
        current_item = self.tests_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите тест для удаления!")
            return
            
        reply = QMessageBox.question(self, "Подтверждение", 
                                   "Вы уверены, что хотите удалить этот тест?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            test_data = current_item.data(Qt.ItemDataRole.UserRole)
            self.remove_test(test_data)
            self.load_tests_list()
            QMessageBox.information(self, "Успех", "Тест успешно удален!")
            
    def save_test(self, test_data):
        """Сохраняет новый тест"""
        try:
            if os.path.exists(TESTS_FILE):
                with open(TESTS_FILE, 'r', encoding='utf-8') as f:
                    tests_data = json.load(f)
            else:
                tests_data = {"tests": []}
                
            # Обновляем существующий тест или добавляем новый
            test_to_update = next((t for t in tests_data['tests'] if t.get('id') == test_data.get('id')), None)
            if test_to_update:
                test_to_update.update(test_data)
            else:
                # Генерируем новый ID, если тест добавляется
                new_id = max([test.get('id', 0) for test in tests_data['tests']], default=0) + 1
                test_data['id'] = new_id
                tests_data['tests'].append(test_data)
                
            with open(TESTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tests_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении теста: {str(e)}")
            
    def remove_test(self, test_data):
        """Удаляет тест"""
        try:
            if os.path.exists(TESTS_FILE):
                with open(TESTS_FILE, 'r', encoding='utf-8') as f:
                    tests_data = json.load(f)
                    
                # Удаляем тест по ID
                tests_data['tests'] = [test for test in tests_data['tests'] if test.get('id') != test_data.get('id')]
                
                with open(TESTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(tests_data, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении теста: {str(e)}")
        
    def logout(self):
        """Выход из админ-панели"""
        self.close()
        login_window = LoginWindow()
        login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем шрифт
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = LoginWindow()
    window.show()
    
    sys.exit(app.exec())