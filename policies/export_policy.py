"""
Export Policy - Prevents output file collisions and data loss.

This module provides strategies to ensure output files are not accidentally
overwritten when multiple runs occur in rapid succession.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ExportPolicy:
    """Policy for safe file export with collision prevention."""
    
    # Strategy for preventing file overwrites:
    # - 'uuid': Append UUID to filename
    # - 'increment': Check existence and increment counter
    # - 'millisecond': Use millisecond-precision timestamp
    collision_strategy: str = 'uuid'
    
    # Whether to preserve original timestamp in filename
    include_timestamp: bool = True
    
    # Timezone for timestamps (always UTC for consistency)
    use_utc: bool = True
    
    def __init__(
        self, 
        collision_strategy: str = 'uuid',
        include_timestamp: bool = True,
        use_utc: bool = True
    ):
        """Initialize export policy with collision prevention strategy."""
        valid_strategies = {'uuid', 'increment', 'millisecond'}
        if collision_strategy not in valid_strategies:
            raise ValueError(
                f"Invalid collision_strategy: {collision_strategy}. "
                f"Must be one of {valid_strategies}"
            )
        
        self.collision_strategy = collision_strategy
        self.include_timestamp = include_timestamp
        self.use_utc = use_utc
    
    def generate_safe_filename(
        self, 
        base_name: str, 
        extension: str = 'csv',
        output_dir: Optional[Path] = None
    ) -> str:
        """
        Generate a filename guaranteed not to overwrite existing files.
        
        Args:
            base_name: Base filename without extension
            extension: File extension (without dot)
            output_dir: Directory to check for existing files (for increment strategy)
            
        Returns:
            Safe filename string
            
        Examples:
            >>> policy = ExportPolicy(collision_strategy='uuid')
            >>> policy.generate_safe_filename('lawyers', 'csv')
            'lawyers_20260126_143022_a1b2c3d4.csv'
        """
        parts = [base_name]
        
        # Add timestamp if enabled
        if self.include_timestamp:
            now = datetime.now(timezone.utc) if self.use_utc else datetime.now()
            
            if self.collision_strategy == 'millisecond':
                # Millisecond precision to reduce collision probability
                timestamp = now.strftime('%Y%m%d_%H%M%S_%f')[:-3]  # truncate to ms
            else:
                timestamp = now.strftime('%Y%m%d_%H%M%S')
            
            parts.append(timestamp)
        
        # Add collision prevention suffix
        if self.collision_strategy == 'uuid':
            # Use first 8 chars of UUID for readability
            unique_id = str(uuid.uuid4())[:8]
            parts.append(unique_id)
        
        elif self.collision_strategy == 'increment':
            # Check for existing files and increment counter
            if output_dir is None:
                output_dir = Path('.')
            
            counter = 0
            while True:
                if counter == 0:
                    test_name = '_'.join(parts)
                else:
                    test_name = '_'.join(parts + [f'v{counter}'])
                
                test_path = output_dir / f"{test_name}.{extension}"
                if not test_path.exists():
                    if counter > 0:
                        parts.append(f'v{counter}')
                    break
                counter += 1
                
                # Safety limit
                if counter > 999:
                    raise RuntimeError(
                        f"Cannot find unused filename after 999 attempts: {base_name}"
                    )
        
        # 'millisecond' strategy uses timestamp only (already added above)
        
        filename = '_'.join(parts) + f'.{extension}'
        return filename
