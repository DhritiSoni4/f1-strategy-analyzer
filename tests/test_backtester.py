import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.backtester import evaluate_race

result = evaluate_race(2023, 'Bahrain')

print(result)