from .gauge_config_service import get_gauge_config_mapping, get_gauge_class_mapping

"""
Gauge Scale Service Module

This module provides functionality to calculate the appropriate gauge scale
based on pressure unit and class rating for valve testing equipment.
"""

def get_gauge_scale(pressure_unit, class_rating):
    """
    Calculate the appropriate gauge scale based on pressure unit and class rating.
    
    Args:
        pressure_unit (str): The pressure unit ('bar', 'kg/cm2g', or 'psi')
        class_rating (str): The class rating ('#150', '#300', '#600', '#900', '#1500')
    
    Returns:
        int: The calculated gauge scale value
    """
    # Normalize pressure unit to lowercase for comparison
    pressure_unit = pressure_unit.lower().strip() if pressure_unit else 'psi'
    # Normalize class rating to ensure it starts with #
    if not class_rating.startswith('#'):
        class_rating = f"#{class_rating}"

    gauge_config_mapping = get_gauge_config_mapping()
    gauge_class_mapping = get_gauge_class_mapping()

    # Find dynamic configuration for this class
    target_class = class_rating.lstrip('#')
    dynamic_config = next((
        item for item in gauge_class_mapping
        if str(item.get('class_name')) == target_class
    ), None)
    
    # If dynamic class-based range is enabled and used successfully
    if gauge_config_mapping and gauge_config_mapping.get('class_based_range', {}).get('status') and dynamic_config:
        if pressure_unit == 'bar':
            return int(dynamic_config.get('range_bar', 0))
        elif pressure_unit == 'psi':
            return int(dynamic_config.get('range_psi', 0))
        elif pressure_unit == 'kg/cm2g':
            return int(dynamic_config.get('range_kgcm2', 0))

    # Fallback to hardcoded logic
    if pressure_unit in ['bar', 'kg/cm2g']:
        if class_rating == '#150':
            return 70
        elif class_rating == '#300':
            return 200
        elif class_rating == '#600':
            return 280
        elif class_rating == '#900':
            return 400
        elif class_rating == '#1500':
            return 700
    elif pressure_unit == 'psi':
        if class_rating == '#150':
            return 1000
        elif class_rating == '#300':
            return 3000
        elif class_rating == '#600':
            return 4000
        elif class_rating == '#800':
            return 6000
        elif class_rating == '#900':
            return 6000
        elif class_rating == '#1500':
            return 10000
        elif class_rating == '#2500':
            return 15000
    
    # Default value if no match found
    return 100


def get_gauge_scale_from_valve_class_name(valve_class_name, pressure_unit):
    """
    Calculate the appropriate gauge scale based on valve class name and pressure unit.
    
    This function extracts the class rating from the valve class name and calculates
    the gauge scale based on the pressure unit.
    
    Args:
        valve_class_name (str): The valve class name (e.g., "150#", "300#", "Class 600", etc.)
        pressure_unit (str): The pressure unit ('bar', 'kg/cm2g', or 'psi')
    
    Returns:
        int: The calculated gauge scale value
    """
    # Extract class rating from valve class name
    class_rating = extract_class_rating(valve_class_name)
    
    return get_gauge_scale(pressure_unit, class_rating)


def extract_class_rating(valve_class_name):
    """
    Extract the class rating from a valve class name.
    
    Args:
        valve_class_name (str): The valve class name (e.g., "150#", "300#", "Class 600", etc.)
    
    Returns:
        str: The class rating in format "#XXX" (e.g., "#150", "#300", etc.)
    """
    if not valve_class_name:
        return "#150"  # Default class rating
    
    # Clean up the class name
    cleaned_name = valve_class_name.strip().replace(" ", "").replace("Class", "").replace("class", "")
    
    # If it already starts with #, return it as is
    if cleaned_name.startswith('#'):
        return cleaned_name
    
    # Extract numeric part and add # prefix
    import re
    numbers = re.findall(r'\d+', cleaned_name)
    if numbers:
        return f"#{numbers[0]}"
    
    # Default to #150 if no number found
    return "#150"


def get_available_class_ratings():
    """
    Get the list of available class ratings.
    
    Returns:
        list: A list of available class ratings
    """
    return ['#150', '#300', '#600', '#900', '#1500']


def get_available_pressure_units():
    """
    Get the list of available pressure units.
    
    Returns:
        list: A list of available pressure units
    """
    return ['bar', 'psi', 'kg/cm2g']