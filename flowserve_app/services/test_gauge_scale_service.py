"""
Test module for the gauge scale service.
"""

from gauge_scale_service import get_gauge_scale, get_gauge_scale_from_valve_class_name, extract_class_rating


def test_gauge_scale():
    """Test the basic gauge scale functionality."""
    print("Testing basic gauge scale calculations...")
    
    # Test bar/kg/cm2g with different class ratings
    assert get_gauge_scale('bar', '#150') == 70
    assert get_gauge_scale('bar', '#300') == 200
    assert get_gauge_scale('bar', '#600') == 280
    assert get_gauge_scale('bar', '#900') == 400
    assert get_gauge_scale('bar', '#1500') == 700
    
    # Test kg/cm2g (should behave the same as bar)
    assert get_gauge_scale('kg/cm2g', '#150') == 70
    assert get_gauge_scale('kg/cm2g', '#300') == 200
    assert get_gauge_scale('kg/cm2g', '#600') == 280
    assert get_gauge_scale('kg/cm2g', '#900') == 400
    assert get_gauge_scale('kg/cm2g', '#1500') == 700
    
    # Test psi with different class ratings
    assert get_gauge_scale('psi', '#150') == 1015
    assert get_gauge_scale('psi', '#300') == 2900
    assert get_gauge_scale('psi', '#600') == 4060
    assert get_gauge_scale('psi', '#900') == 5800
    assert get_gauge_scale('psi', '#1500') == 10150
    
    print("Basic gauge scale tests passed!")


def test_extract_class_rating():
    """Test the class rating extraction functionality."""
    print("Testing class rating extraction...")
    
    assert extract_class_rating("150#") == "#150"
    assert extract_class_rating("#150") == "#150"
    assert extract_class_rating("Class 150") == "#150"
    assert extract_class_rating("class 150") == "#150"
    assert extract_class_rating("  300  ") == "#300"
    assert extract_class_rating("Class 600") == "#600"
    assert extract_class_rating("900#") == "#900"
    assert extract_class_rating("1500#") == "#1500"
    
    print("Class rating extraction tests passed!")


def test_gauge_scale_from_valve_class_name():
    """Test the gauge scale calculation from valve class name."""
    print("Testing gauge scale from valve class name...")
    
    # Test with various valve class name formats
    assert get_gauge_scale_from_valve_class_name("150#", "bar") == 70
    assert get_gauge_scale_from_valve_class_name("#150", "bar") == 70
    assert get_gauge_scale_from_valve_class_name("Class 150", "bar") == 70
    assert get_gauge_scale_from_valve_class_name("class 150", "bar") == 70
    
    assert get_gauge_scale_from_valve_class_name("300#", "psi") == 2900
    assert get_gauge_scale_from_valve_class_name("Class 300", "psi") == 2900
    
    assert get_gauge_scale_from_valve_class_name("600#", "bar") == 280
    assert get_gauge_scale_from_valve_class_name("Class 600", "psi") == 4060
    
    print("Gauge scale from valve class name tests passed!")


def run_all_tests():
    """Run all tests."""
    print("Running all tests for gauge scale service...\n")
    
    test_gauge_scale()
    print()
    
    test_extract_class_rating()
    print()
    
    test_gauge_scale_from_valve_class_name()
    print()
    
    print("All tests passed successfully!")


if __name__ == "__main__":
    run_all_tests()