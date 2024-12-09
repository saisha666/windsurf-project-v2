import os
import sys
import pytest
import torch
import numpy as np
from pathlib import Path

def test_python_version():
    """Test Python version is 3.8 or higher"""
    assert sys.version_info >= (3, 8), "Python version must be 3.8 or higher"

def test_cuda_availability():
    """Test CUDA availability"""
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"CUDA Version: {torch.version.cuda if torch.cuda.is_available() else 'Not Available'}")

def test_required_packages():
    """Test all required packages are installed"""
    required_packages = [
        'numpy',
        'torch',
        'scipy',
        'sklearn',
        'joblib',
        'pytest',
        'prometheus_client',
        'grafana_api',
        'elasticsearch'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            pytest.fail(f"Required package {package} is not installed")

def test_environment_variables():
    """Test environment variables are set"""
    required_vars = ['WINDSURF_HOME', 'WINDSURF_DATA', 'WINDSURF_MODELS']
    for var in required_vars:
        assert var in os.environ, f"Environment variable {var} is not set"
        assert Path(os.environ[var]).exists(), f"Path {os.environ[var]} does not exist"

def test_directory_structure():
    """Test project directory structure"""
    required_dirs = [
        'src',
        'data',
        'models',
        'tests',
        'src/analysis',
        'src/gaming',
        'src/database',
        'src/scrapers',
        'src/utils'
    ]
    
    base_path = Path(os.environ.get('WINDSURF_HOME', os.getcwd()))
    for dir_path in required_dirs:
        assert (base_path / dir_path).exists(), f"Directory {dir_path} does not exist"

def test_gpu_capabilities():
    """Test GPU capabilities if available"""
    if torch.cuda.is_available():
        # Test CUDA tensor operations
        x = torch.randn(100, 100).cuda()
        y = torch.randn(100, 100).cuda()
        z = torch.matmul(x, y)
        assert z.is_cuda, "GPU tensor operations failed"
        
        # Print GPU info
        print("\nGPU Information:")
        print(f"Device Count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"Device {i}: {torch.cuda.get_device_name(i)}")
            print(f"Memory Allocated: {torch.cuda.memory_allocated(i) / 1e9:.2f} GB")
            print(f"Memory Cached: {torch.cuda.memory_reserved(i) / 1e9:.2f} GB")

def test_numpy_operations():
    """Test basic numpy operations"""
    try:
        # Test basic operations
        arr = np.random.randn(1000, 1000)
        result = np.dot(arr, arr.T)
        assert result.shape == (1000, 1000), "NumPy matrix operations failed"
        
        # Test memory allocation
        print("\nNumPy Array Info:")
        print(f"Array Size: {arr.nbytes / 1e6:.2f} MB")
        print(f"Array Shape: {arr.shape}")
        print(f"Array Dtype: {arr.dtype}")
    except Exception as e:
        pytest.fail(f"NumPy operations failed: {str(e)}")

if __name__ == '__main__':
    pytest.main([__file__])
