#!/usr/bin/env python
"""
Скрипт для создания Урока 2: Сравнение и сокращение дробей с интерактивом
Запуск: python manage.py shell < create_lesson2.py
"""

from main.models import Lesson
from datetime import date

# Теоретический материал для урока 2 с визуализацией и интерактивом
theory_html = """
<div style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6;">
    <h2 style="color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 10px;">📊 Сравнение и сокращение дробей</h2>

    <h3 style="color: #FF6B35; margin-top: 30px;">1️⃣ Сокращение дробей</h3>
    <p><strong>Сокращение дроби</strong> — это деление числителя и знаменателя на их общий делитель.</p>

    <div style="background: #E3F2FD; padding: 15px; border-left: 4px solid #1976D2; margin: 15px 0;">
        <p><strong>Правило:</strong> Чтобы сократить дробь, нужно найти наибольший общий делитель (НОД) числителя и знаменателя, и разделить оба числа на него.</p>
    </div>

    <!-- Визуальная схема сокращения -->
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; margin: 25px 0;">
        <h4 style="color: white; margin-top: 0; text-align: center;">📐 Визуальная схема сокращения</h4>
        <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="text-align: center; font-size: 24px; margin-bottom: 15px;">
                <span style="background: rgba(255,255,255,0.3); padding: 10px 20px; border-radius: 8px;">$\\frac{12}{18}$</span>
            </div>
            <div style="text-align: center; font-size: 20px; margin: 15px 0;">⬇️ Находим НОД(12, 18) = 6</div>
            <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 15px; align-items: center; margin: 20px 0;">
                <div style="text-align: center;">
                    <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        Числитель: 12 ÷ 6 = <strong>2</strong>
                    </div>
                </div>
                <div style="font-size: 30px;">➗</div>
                <div style="text-align: center;">
                    <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        Знаменатель: 18 ÷ 6 = <strong>3</strong>
                    </div>
                </div>
            </div>
            <div style="text-align: center; font-size: 24px; margin-top: 15px;">
                <span style="background: #4CAF50; padding: 10px 20px; border-radius: 8px;">✅ Ответ: $\\frac{2}{3}$</span>
            </div>
        </div>
    </div>

    <p><strong>Пример 1:</strong> Сократим дробь $\\frac{12}{18}$</p>
    <ul>
        <li>НОД(12, 18) = 6</li>
        <li>$\\frac{12}{18} = \\frac{12 \\div 6}{18 \\div 6} = \\frac{2}{3}$</li>
    </ul>

    <p><strong>Пример 2:</strong> Сократим дробь $\\frac{24}{36}$</p>
    <ul>
        <li>НОД(24, 36) = 12</li>
        <li>$\\frac{24}{36} = \\frac{24 \\div 12}{36 \\div 12} = \\frac{2}{3}$</li>
    </ul>

    <!-- Интерактивный тренажёр сокращения -->
    <div style="background: #FFF; border: 3px solid #1976D2; border-radius: 15px; padding: 25px; margin: 30px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h4 style="color: #1976D2; margin-top: 0; text-align: center;">🎯 Интерактивный тренажёр: Попробуй сам!</h4>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
            <div>
                <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #1976D2;">Числитель:</label>
                <input type="number" id="trainNum" style="width: 100%; padding: 12px; border: 2px solid #1976D2; border-radius: 8px; font-size: 18px; text-align: center;" value="24" min="1">
            </div>
            <div>
                <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #1976D2;">Знаменатель:</label>
                <input type="number" id="trainDen" style="width: 100%; padding: 12px; border: 2px solid #1976D2; border-radius: 8px; font-size: 18px; text-align: center;" value="36" min="1">
            </div>
        </div>

        <button onclick="reduceFraction()" style="width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: 600; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 10px rgba(102, 126, 234, 0.4);">
            ✨ Сократить дробь
        </button>

        <div id="reduceResult" style="margin-top: 20px; padding: 20px; background: #E3F2FD; border-radius: 10px; display: none;">
            <div style="font-size: 20px; font-weight: 600; color: #1976D2; margin-bottom: 15px; text-align: center;">📊 Решение:</div>
            <div id="reduceSteps" style="line-height: 2; font-size: 16px;"></div>
        </div>
    </div>

    <h3 style="color: #FF6B35; margin-top: 40px;">2️⃣ Сравнение дробей с одинаковым знаменателем</h3>
    <p>Если у дробей <strong>одинаковый знаменатель</strong>, то больше та дробь, у которой <strong>больше числитель</strong>.</p>

    <div style="background: #E3F2FD; padding: 15px; border-left: 4px solid #1976D2; margin: 15px 0;">
        <p><strong>Правило:</strong> Из двух дробей с одинаковым знаменателем больше та, у которой числитель больше.</p>
    </div>

    <!-- Визуальное сравнение с графикой -->
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 25px; border-radius: 15px; margin: 25px 0;">
        <h4 style="color: white; margin-top: 0; text-align: center;">📊 Наглядное сравнение</h4>
        <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px;">
            <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 20px; align-items: center;">
                <div style="text-align: center;">
                    <div style="font-size: 28px; margin-bottom: 10px;">$\\frac{3}{7}$</div>
                    <div style="background: rgba(255,255,255,0.3); height: 100px; border-radius: 8px; position: relative; overflow: hidden;">
                        <div style="background: #4CAF50; height: 43%; width: 100%; position: absolute; bottom: 0; border-radius: 0 0 8px 8px;"></div>
                    </div>
                    <div style="margin-top: 8px; font-size: 14px; opacity: 0.9;">3 части из 7</div>
                </div>

                <div style="font-size: 40px; font-weight: bold;">&lt;</div>

                <div style="text-align: center;">
                    <div style="font-size: 28px; margin-bottom: 10px;">$\\frac{5}{7}$</div>
                    <div style="background: rgba(255,255,255,0.3); height: 100px; border-radius: 8px; position: relative; overflow: hidden;">
                        <div style="background: #FF6B35; height: 71%; width: 100%; position: absolute; bottom: 0; border-radius: 0 0 8px 8px;"></div>
                    </div>
                    <div style="margin-top: 8px; font-size: 14px; opacity: 0.9;">5 частей из 7</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px; font-size: 18px; background: rgba(255,255,255,0.2); padding: 12px; border-radius: 8px;">
                Знаменатели одинаковые (7 = 7) → Сравниваем числители: 3 &lt; 5
            </div>
        </div>
    </div>

    <p><strong>Пример:</strong> Сравним $\\frac{3}{7}$ и $\\frac{5}{7}$</p>
    <ul>
        <li>Знаменатели одинаковые (7 = 7)</li>
        <li>Сравниваем числители: 3 < 5</li>
        <li><strong>Ответ:</strong> $\\frac{3}{7} < \\frac{5}{7}$</li>
    </ul>

    <h3 style="color: #FF6B35; margin-top: 40px;">3️⃣ Сравнение дробей с разными знаменателями</h3>
    <p>Если у дробей <strong>разные знаменатели</strong>, нужно привести их к общему знаменателю, а затем сравнить числители.</p>

    <div style="background: #E3F2FD; padding: 15px; border-left: 4px solid #1976D2; margin: 15px 0;">
        <p><strong>Правило:</strong></p>
        <ol>
            <li>Найти общий знаменатель (обычно НОК)</li>
            <li>Привести дроби к общему знаменателю</li>
            <li>Сравнить числители</li>
        </ol>
    </div>

    <!-- Пошаговая схема приведения к общему знаменателю -->
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: #333; padding: 25px; border-radius: 15px; margin: 25px 0;">
        <h4 style="margin-top: 0; text-align: center;">🔄 Пошаговое приведение к общему знаменателю</h4>
        <div style="background: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px;">
            <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 15px; margin-bottom: 20px;">
                <div style="text-align: center; padding: 15px; background: #E3F2FD; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold; color: #1976D2;">$\\frac{2}{3}$</div>
                    <div style="margin-top: 10px; font-size: 14px;">Исходная дробь</div>
                </div>
                <div style="align-self: center; font-size: 30px;">⚡</div>
                <div style="text-align: center; padding: 15px; background: #FFE0B2; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold; color: #FF6B35;">$\\frac{3}{4}$</div>
                    <div style="margin-top: 10px; font-size: 14px;">Исходная дробь</div>
                </div>
            </div>

            <div style="text-align: center; padding: 12px; background: #FFF3E0; border-radius: 8px; margin: 15px 0; font-weight: 600;">
                ⬇️ НОК(3, 4) = 12 ⬇️
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                <div style="padding: 15px; background: #E3F2FD; border-radius: 8px; border: 2px solid #1976D2;">
                    <div style="text-align: center; margin-bottom: 10px;">$\\frac{2}{3} = \\frac{2 \\times 4}{3 \\times 4}$</div>
                    <div style="text-align: center; font-size: 22px; font-weight: bold; color: #1976D2;">$\\frac{8}{12}$</div>
                </div>
                <div style="padding: 15px; background: #FFE0B2; border-radius: 8px; border: 2px solid #FF6B35;">
                    <div style="text-align: center; margin-bottom: 10px;">$\\frac{3}{4} = \\frac{3 \\times 3}{4 \\times 3}$</div>
                    <div style="text-align: center; font-size: 22px; font-weight: bold; color: #FF6B35;">$\\frac{9}{12}$</div>
                </div>
            </div>

            <div style="text-align: center; padding: 15px; background: #C8E6C9; border-radius: 8px; margin-top: 15px;">
                <div style="font-size: 18px; font-weight: 600;">Сравниваем числители: 8 &lt; 9</div>
                <div style="font-size: 22px; font-weight: bold; color: #4CAF50; margin-top: 10px;">
                    ✅ Ответ: $\\frac{2}{3} < \\frac{3}{4}$
                </div>
            </div>
        </div>
    </div>

    <p><strong>Пример:</strong> Сравним $\\frac{2}{3}$ и $\\frac{3}{4}$</p>
    <ul>
        <li>Общий знаменатель: НОК(3, 4) = 12</li>
        <li>$\\frac{2}{3} = \\frac{2 \\times 4}{3 \\times 4} = \\frac{8}{12}$</li>
        <li>$\\frac{3}{4} = \\frac{3 \\times 3}{4 \\times 3} = \\frac{9}{12}$</li>
        <li>Сравниваем: 8 < 9</li>
        <li><strong>Ответ:</strong> $\\frac{2}{3} < \\frac{3}{4}$</li>
    </ul>

    <!-- Интерактивный калькулятор сравнения -->
    <div style="background: #FFF; border: 3px solid #FF6B35; border-radius: 15px; padding: 25px; margin: 30px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h4 style="color: #FF6B35; margin-top: 0; text-align: center;">🎯 Сравни дроби сам!</h4>

        <div style="display: grid; grid-template-columns: 2fr auto 2fr; gap: 15px; align-items: end; margin: 20px 0;">
            <div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-size: 14px; color: #666;">Числитель 1:</label>
                        <input type="number" id="comp1Num" style="width: 100%; padding: 10px; border: 2px solid #FF6B35; border-radius: 8px; text-align: center; font-size: 16px;" value="2" min="1">
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-size: 14px; color: #666;">Знаменатель 1:</label>
                        <input type="number" id="comp1Den" style="width: 100%; padding: 10px; border: 2px solid #FF6B35; border-radius: 8px; text-align: center; font-size: 16px;" value="3" min="1">
                    </div>
                </div>
            </div>

            <div style="font-size: 30px; text-align: center; padding-bottom: 10px;">⚡</div>

            <div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-size: 14px; color: #666;">Числитель 2:</label>
                        <input type="number" id="comp2Num" style="width: 100%; padding: 10px; border: 2px solid #FF6B35; border-radius: 8px; text-align: center; font-size: 16px;" value="3" min="1">
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-size: 14px; color: #666;">Знаменатель 2:</label>
                        <input type="number" id="comp2Den" style="width: 100%; padding: 10px; border: 2px solid #FF6B35; border-radius: 8px; text-align: center; font-size: 16px;" value="4" min="1">
                    </div>
                </div>
            </div>
        </div>

        <button onclick="compareFractions()" style="width: 100%; padding: 15px; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: #333; border: none; border-radius: 10px; font-size: 18px; font-weight: 600; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 10px rgba(250, 112, 154, 0.4);">
            🔍 Сравнить дроби
        </button>

        <div id="compareResult" style="margin-top: 20px; padding: 20px; background: #FFF3E0; border-radius: 10px; display: none;">
            <div style="font-size: 20px; font-weight: 600; color: #FF6B35; margin-bottom: 15px; text-align: center;">📊 Решение:</div>
            <div id="compareSteps" style="line-height: 2; font-size: 16px;"></div>
        </div>
    </div>

    <h3 style="color: #FF6B35; margin-top: 40px;">💡 Полезные советы</h3>
    <ul>
        <li>Всегда старайтесь сокращать дроби до несократимого вида</li>
        <li>При сравнении дробей с одинаковым знаменателем смотрите только на числители</li>
        <li>Для сравнения дробей с разными знаменателями удобно использовать "крест-накрест": сравните $a \\times d$ и $b \\times c$ для дробей $\\frac{a}{b}$ и $\\frac{c}{d}$</li>
        <li>Метод "крест-накрест": если $a \\times d > b \\times c$, то $\\frac{a}{b} > \\frac{c}{d}$</li>
    </ul>

    <div style="background: #FFF3E0; padding: 15px; border-left: 4px solid #FF6B35; margin: 20px 0;">
        <p><strong>⚠️ Важно!</strong> В последнем задании теста будет повышенная сложность. Оно обязательно для получения оценки 7!</p>
    </div>

    <script>
    // Функция нахождения НОД (алгоритм Евклида)
    function gcd(a, b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b !== 0) {
            let temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    // Функция нахождения НОК
    function lcm(a, b) {
        return Math.abs(a * b) / gcd(a, b);
    }

    // Сокращение дроби
    function reduceFraction() {
        const num = parseInt(document.getElementById('trainNum').value);
        const den = parseInt(document.getElementById('trainDen').value);

        if (!num || !den || den === 0) {
            alert('Введите корректные числа! Знаменатель не может быть нулём.');
            return;
        }

        const divisor = gcd(num, den);
        const reducedNum = num / divisor;
        const reducedDen = den / divisor;

        let steps = '<div style="padding: 15px; background: white; border-radius: 8px; margin-bottom: 15px;">';
        steps += '<div style="font-size: 18px; margin-bottom: 10px;">🔢 Исходная дробь: <strong style="color: #1976D2;">$\\\\frac{' + num + '}{' + den + '}$</strong></div>';
        steps += '</div>';

        steps += '<div style="padding: 15px; background: white; border-radius: 8px; margin-bottom: 15px;">';
        steps += '<div style="margin-bottom: 8px;">📐 НОД(' + num + ', ' + den + ') = <strong style="color: #FF6B35;">' + divisor + '</strong></div>';
        steps += '</div>';

        if (divisor === 1) {
            steps += '<div style="padding: 15px; background: #C8E6C9; border-radius: 8px; border: 2px solid #4CAF50;">';
            steps += '<div style="font-size: 18px; font-weight: 600; color: #4CAF50;">✅ Дробь уже несократимая!</div>';
            steps += '<div style="margin-top: 10px; font-size: 20px;">Ответ: <strong>$\\\\frac{' + num + '}{' + den + '}$</strong></div>';
            steps += '</div>';
        } else {
            steps += '<div style="padding: 15px; background: white; border-radius: 8px; margin-bottom: 15px;">';
            steps += '<div style="margin-bottom: 8px;">➗ Числитель: ' + num + ' ÷ ' + divisor + ' = <strong>' + reducedNum + '</strong></div>';
            steps += '<div>➗ Знаменатель: ' + den + ' ÷ ' + divisor + ' = <strong>' + reducedDen + '</strong></div>';
            steps += '</div>';

            steps += '<div style="padding: 15px; background: #C8E6C9; border-radius: 8px; border: 2px solid #4CAF50;">';
            steps += '<div style="font-size: 18px; font-weight: 600; color: #4CAF50;">✅ Дробь сокращена!</div>';
            steps += '<div style="margin-top: 10px; font-size: 22px;">$\\\\frac{' + num + '}{' + den + '} = \\\\frac{' + reducedNum + '}{' + reducedDen + '}$</div>';
            steps += '</div>';
        }

        document.getElementById('reduceSteps').innerHTML = steps;
        document.getElementById('reduceResult').style.display = 'block';

        // Перерисовка MathJax
        if (window.MathJax) {
            MathJax.typesetPromise([document.getElementById('reduceSteps')]);
        }
    }

    // Сравнение дробей
    function compareFractions() {
        const num1 = parseInt(document.getElementById('comp1Num').value);
        const den1 = parseInt(document.getElementById('comp1Den').value);
        const num2 = parseInt(document.getElementById('comp2Num').value);
        const den2 = parseInt(document.getElementById('comp2Den').value);

        if (!num1 || !den1 || !num2 || !den2 || den1 === 0 || den2 === 0) {
            alert('Введите корректные числа! Знаменатели не могут быть нулём.');
            return;
        }

        let steps = '<div style="padding: 15px; background: white; border-radius: 8px; margin-bottom: 15px;">';
        steps += '<div style="font-size: 18px; margin-bottom: 10px;">Сравниваем: <strong style="color: #1976D2;">$\\\\frac{' + num1 + '}{' + den1 + '}$</strong> и <strong style="color: #FF6B35;">$\\\\frac{' + num2 + '}{' + den2 + '}$</strong></div>';
        steps += '</div>';

        let comparison;

        if (den1 === den2) {
            // Одинаковые знаменатели
            steps += '<div style="padding: 15px; background: #E3F2FD; border-radius: 8px; margin-bottom: 15px;">';
            steps += '<div>✅ Знаменатели одинаковые (' + den1 + ' = ' + den2 + ')</div>';
            steps += '<div style="margin-top: 8px;">📊 Сравниваем числители: ' + num1 + ' и ' + num2 + '</div>';
            steps += '</div>';

            if (num1 > num2) comparison = '>';
            else if (num1 < num2) comparison = '<';
            else comparison = '=';
        } else {
            // Разные знаменатели
            const commonDen = lcm(den1, den2);
            const newNum1 = num1 * (commonDen / den1);
            const newNum2 = num2 * (commonDen / den2);

            steps += '<div style="padding: 15px; background: #FFF3E0; border-radius: 8px; margin-bottom: 15px;">';
            steps += '<div>⚠️ Знаменатели разные (' + den1 + ' ≠ ' + den2 + ')</div>';
            steps += '<div style="margin-top: 8px;">📐 Находим НОК(' + den1 + ', ' + den2 + ') = <strong>' + commonDen + '</strong></div>';
            steps += '</div>';

            steps += '<div style="padding: 15px; background: white; border-radius: 8px; margin-bottom: 15px;">';
            steps += '<div style="margin-bottom: 10px;">🔄 Приводим к общему знаменателю:</div>';
            steps += '<div style="margin-left: 20px; margin-bottom: 8px;">$\\\\frac{' + num1 + '}{' + den1 + '} = \\\\frac{' + num1 + ' \\\\times ' + (commonDen/den1) + '}{' + den1 + ' \\\\times ' + (commonDen/den1) + '} = \\\\frac{' + newNum1 + '}{' + commonDen + '}$</div>';
            steps += '<div style="margin-left: 20px;">$\\\\frac{' + num2 + '}{' + den2 + '} = \\\\frac{' + num2 + ' \\\\times ' + (commonDen/den2) + '}{' + den2 + ' \\\\times ' + (commonDen/den2) + '} = \\\\frac{' + newNum2 + '}{' + commonDen + '}$</div>';
            steps += '</div>';

            steps += '<div style="padding: 15px; background: #E3F2FD; border-radius: 8px; margin-bottom: 15px;">';
            steps += '<div>📊 Сравниваем числители: ' + newNum1 + ' и ' + newNum2 + '</div>';
            steps += '</div>';

            if (newNum1 > newNum2) comparison = '>';
            else if (newNum1 < newNum2) comparison = '<';
            else comparison = '=';
        }

        const compSymbol = comparison === '>' ? '&gt;' : (comparison === '<' ? '&lt;' : '=');
        const compColor = comparison === '>' ? '#FF6B35' : (comparison === '<' ? '#1976D2' : '#4CAF50');

        steps += '<div style="padding: 20px; background: #C8E6C9; border-radius: 8px; border: 2px solid #4CAF50;">';
        steps += '<div style="font-size: 18px; font-weight: 600; color: #4CAF50; margin-bottom: 10px;">✅ Результат сравнения:</div>';
        steps += '<div style="font-size: 24px; text-align: center; font-weight: bold; color: ' + compColor + ';">';
        steps += '$\\\\frac{' + num1 + '}{' + den1 + '}$ ' + compSymbol + ' $\\\\frac{' + num2 + '}{' + den2 + '}$';
        steps += '</div>';
        steps += '</div>';

        document.getElementById('compareSteps').innerHTML = steps;
        document.getElementById('compareResult').style.display = 'block';

        // Перерисовка MathJax
        if (window.MathJax) {
            MathJax.typesetPromise([document.getElementById('compareSteps')]);
        }
    }
    </script>
</div>
"""

# Проверяем, не создан ли уже урок
existing_lesson = Lesson.objects.filter(date=date(2026, 2, 3)).first()

if existing_lesson:
    print(f"⚠️ Урок на 03.02.2026 уже существует: {existing_lesson.title}")
    print(f"Хотите обновить его? (Удалите старый урок в админке, затем запустите скрипт снова)")
else:
    # Создаём урок
    lesson2 = Lesson.objects.create(
        title="Урок 2. Сравнение и сокращение дробей",
        date=date(2026, 2, 3),
        subject="Математика",
        grade="5",
        theory_content=theory_html,
        duration_minutes=40,
        test_duration_minutes=10,
        is_active=True
    )

    print("✅ Успешно создан урок с интерактивом:")
    print(f"   Название: {lesson2.title}")
    print(f"   Дата: {lesson2.date.strftime('%d.%m.%Y')}")
    print(f"   URL: /lessons/{lesson2.date}/")
    print(f"   Длительность: {lesson2.duration_minutes} мин")
    print(f"   Время на тест: {lesson2.test_duration_minutes} мин")
    print()
    print("🎨 Добавлено:")
    print("   ✅ Визуальные схемы с градиентами")
    print("   ✅ Столбчатые диаграммы сравнения")
    print("   ✅ Интерактивный тренажёр сокращения")
    print("   ✅ Интерактивный калькулятор сравнения")
    print("   ✅ Пошаговые решения с анимацией")
    print()
    print("🎯 Типы заданий в тесте:")
    print("   - 3 задания на сокращение дробей")
    print("   - 3 задания на сравнение (одинаковый знаменатель)")
    print("   - 3 задания на сравнение (разные знаменатели)")
    print("   - 1 задание повышенной сложности (обязательно для оценки 7)")
    print()
    print("📊 Задания генерируются автоматически для каждого ученика индивидуально!")
