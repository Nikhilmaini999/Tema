"""Tests for TEMA protocol."""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.transport.protocol import (
    TEMAProtocol, TEMAFrame, TEMAHeader, PayloadType, Flags
)


class TestTEMAProtocol:
    """Test TEMA protocol implementation."""
    
    def test_frame_creation(self):
        """Test creating a TEMA frame."""
        protocol = TEMAProtocol()
        payload = b'test payload data'
        
        frame = protocol.create_frame(
            payload_type=PayloadType.CONTROL,
            payload=payload,
            dest_device_id=0x12345678
        )
        
        assert frame.header.payload_type == PayloadType.CONTROL
        assert frame.payload == payload
        assert frame.header.dest_device_id == 0x12345678
    
    def test_frame_serialization(self):
        """Test frame serialization and deserialization."""
        protocol = TEMAProtocol()
        payload = b'test data'
        
        frame = protocol.create_frame(
            payload_type=PayloadType.MUSIC,
            payload=payload,
            dest_device_id=0xDEADBEEF
        )
        
        # Serialize
        serialized = frame.to_bytes()
        assert len(serialized) > len(payload)  # Includes header and CRC
        
        # Deserialize
        deserialized = TEMAFrame.from_bytes(serialized)
        assert deserialized.payload == payload
        assert deserialized.header.payload_type == PayloadType.MUSIC
    
    def test_encryption_flag(self):
        """Test encrypted frame flag."""
        protocol = TEMAProtocol()
        
        frame = protocol.create_frame(
            payload_type=PayloadType.CONTROL,
            payload=b'data',
            dest_device_id=1,
            encrypted=True
        )
        
        assert frame.header.flags & Flags.ENCRYPTED
    
    def test_sequence_numbering(self):
        """Test sequence number increments."""
        protocol = TEMAProtocol()
        
        frame1 = protocol.create_frame(
            payload_type=PayloadType.CONTROL,
            payload=b'data1',
            dest_device_id=1
        )
        
        frame2 = protocol.create_frame(
            payload_type=PayloadType.CONTROL,
            payload=b'data2',
            dest_device_id=1
        )
        
        assert frame2.header.sequence_number == frame1.header.sequence_number + 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
