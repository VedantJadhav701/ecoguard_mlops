"""Test if weight estimator pickle is valid"""
import pickle

try:
    with open('weight_model/weight_estimator.pkl', 'rb') as f:
        obj = pickle.load(f)
    print(f"✅ Pickle valid!")
    print(f"   Type: {type(obj).__name__}")
    print(f"   Has estimate method: {hasattr(obj, 'estimate')}")
    print(f"   Base weights: {obj.base_weights}")
except Exception as e:
    print(f"❌ Error: {e}")
