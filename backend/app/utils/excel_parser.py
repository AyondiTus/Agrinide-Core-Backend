import pandas as pd
import io
from typing import Tuple, List, Dict, Any

def parse_commodities_excel(file_content: bytes, farmer_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    try:
        df = pd.read_excel(io.BytesIO(file_content))
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {str(e)}")
        
    expected_columns = ['name', 'price_per_kg', 'current_stock', 'location']
    
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in Excel: {', '.join(missing_cols)}")
        
    valid_data = []
    errors = []
    
    for index, row in df.iterrows():
        row_num = index + 2 # 1-based index + 1 for header
        
        try:
            name = str(row.get('name', '')).strip()
            if not name or name == 'nan':
                raise ValueError("Name is required")
                
            try:
                price_per_kg = float(row.get('price_per_kg', 0))
            except ValueError:
                raise ValueError("Price must be a valid number")
                
            if pd.isna(price_per_kg) or price_per_kg <= 0:
                raise ValueError("Price must be greater than 0")
                
            try:
                current_stock = float(row.get('current_stock', 0))
            except ValueError:
                raise ValueError("Stock must be a valid number")
                
            if pd.isna(current_stock) or current_stock < 0:
                raise ValueError("Stock cannot be negative")
                
            location = str(row.get('location', '')).strip()
            if location == 'nan':
                location = None
                
            valid_data.append({
                'farmer_id': farmer_id,
                'name': name,
                'price_per_kg': price_per_kg,
                'current_stock': current_stock,
                'location': location,
                'is_active': True
            })
        except Exception as e:
            errors.append({
                "row_number": row_num,
                "error_message": str(e)
            })
            
    return valid_data, errors
