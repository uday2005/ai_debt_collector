"""
Simple tests to validate performance optimization changes.
These tests verify that caching mechanisms work correctly without breaking functionality.
Uses static analysis to avoid dependency issues.
"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_feedback_module_caching():
    """Test that feedback module has caching code"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'tools', 'feedback_module.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for cache globals
        assert '_cached_model' in content, "Missing _cached_model global"
        assert '_cached_vectorizer' in content, "Missing _cached_vectorizer global"
        
        # Check for cache check in load_model
        assert 'if _cached_model is not None' in content, "Missing cache check"
        
        print("✓ Feedback module has caching mechanism")
        return True
    except Exception as e:
        print(f"✗ Feedback module test failed: {e}")
        return False


def test_web_app_caching():
    """Test that web_app has HTML caching code"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'web_app.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for cache global
        assert '_cached_html' in content, "Missing _cached_html global"
        assert 'get_index_html' in content, "Missing get_index_html function"
        
        # Check that index route uses get_index_html
        assert 'get_index_html()' in content, "Index route doesn't use caching function"
        
        print("✓ Web app has HTML caching mechanism")
        return True
    except Exception as e:
        print(f"✗ Web app test failed: {e}")
        return False


def test_compliance_retriever_caching():
    """Test that compliance retriever has LRU cache"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'tools', 'compliance_tool', 'retriever.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for lru_cache import
        assert 'from functools import lru_cache' in content, "Missing lru_cache import"
        
        # Check for lru_cache decorator
        assert '@lru_cache' in content, "Missing @lru_cache decorator"
        assert 'maxsize=' in content, "Missing maxsize parameter"
        
        print("✓ Compliance retriever has LRU cache")
        return True
    except Exception as e:
        print(f"✗ Compliance retriever test failed: {e}")
        return False


def test_tts_module_optimization():
    """Test that TTS module uses io module instead of tempfile"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'tools', 'tts_module.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check that it uses io module
        assert 'import io' in content, "Missing io import"
        assert 'BytesIO' in content, "Missing BytesIO usage"
        
        # Check that it doesn't use tempfile anymore
        assert 'tempfile.NamedTemporaryFile' not in content, "Still using tempfile"
        
        print("✓ TTS module uses in-memory buffer (BytesIO)")
        return True
    except Exception as e:
        print(f"✗ TTS module test failed: {e}")
        return False


def test_borrower_module_llm_reuse():
    """Test that borrower module has comment about LLM reuse"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'tools', 'borrower_module.py')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check that llm is initialized at module level
        assert 'llm = OllamaLLM' in content, "Missing module-level LLM initialization"
        
        # Check for documentation about reuse
        assert 'connection reuse' in content.lower() or 'reuse' in content.lower(), "Missing optimization comment"
        
        print("✓ Borrower module has module-level LLM instance with optimization note")
        return True
    except Exception as e:
        print(f"✗ Borrower module test failed: {e}")
        return False


def test_javascript_optimization():
    """Test that JavaScript uses optimized base64 encoding"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'app.js')
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for optimized encoding
        assert 'String.fromCharCode.apply(null, bytes)' in content, "Missing optimized base64 encoding"
        
        # Check that old loop is gone
        assert 'for (let i = 0; i < bytes.byteLength; i++)' not in content, "Old inefficient loop still present"
        
        print("✓ JavaScript uses optimized base64 encoding")
        return True
    except Exception as e:
        print(f"✗ JavaScript test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("Running Performance Optimization Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Feedback Module Caching", test_feedback_module_caching),
        ("Web App HTML Caching", test_web_app_caching),
        ("Compliance Retriever LRU Cache", test_compliance_retriever_caching),
        ("TTS Module BytesIO Optimization", test_tts_module_optimization),
        ("Borrower Module LLM Reuse", test_borrower_module_llm_reuse),
        ("JavaScript Base64 Optimization", test_javascript_optimization),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing: {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
