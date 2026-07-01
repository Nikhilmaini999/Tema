"""TEMA Protocol v1 - Custom Layer 2 Protocol for LAN communication."""

import struct
import enum
from typing import Optional, Tuple
from dataclasses import dataclass
import hashlib

try:
    import crc32c
except ImportError:
    import zlib
    crc32c = None


class PayloadType(enum.Enum):
    """Payload types for TEMA protocol."""
    MUSIC = 0x01
    AI_REQUEST = 0x02
    AI_RESPONSE = 0x03
    CONTROL = 0x04
    DISCOVERY = 0x05
    PAIRING = 0x06
    ACK = 0x07
    HEARTBEAT = 0x08


class Flags(enum.IntFlag):
    """TEMA frame flags."""
    ENCRYPTED = 0x01
    COMPRESSED = 0x02
    NEEDS_ACK = 0x04
    MORE_FRAGMENTS = 0x08
    PRIORITY = 0x10


@dataclass
class TEMAHeader:
    """TEMA Protocol Header.
    
    Total header size: 24 bytes
    """
    version: int = 1
    flags: int = 0
    payload_type: PayloadType = PayloadType.CONTROL
    sequence_number: int = 0
    source_device_id: int = 0
    dest_device_id: int = 0
    payload_length: int = 0
    timestamp: int = 0

    def to_bytes(self) -> bytes:
        """Serialize header to bytes."""
        return struct.pack(
            '>BBHIIIHQ',  # Network byte order (big-endian)
            self.version,
            self.flags,
            self.payload_type.value,
            self.sequence_number,
            self.source_device_id,
            self.dest_device_id,
            self.payload_length,
            self.timestamp
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> 'TEMAHeader':
        """Deserialize header from bytes."""
        if len(data) < 24:
            raise ValueError(f"Header too small: {len(data)} < 24")
        
        version, flags, payload_type, seq, src_id, dst_id, payload_len, timestamp = struct.unpack(
            '>BBHIIIHQ', data[:24]
        )
        
        return cls(
            version=version,
            flags=flags,
            payload_type=PayloadType(payload_type),
            sequence_number=seq,
            source_device_id=src_id,
            dest_device_id=dst_id,
            payload_length=payload_len,
            timestamp=timestamp
        )


@dataclass
class TEMAFrame:
    """Complete TEMA frame with header and payload."""
    header: TEMAHeader
    payload: bytes
    
    def to_bytes(self) -> bytes:
        """Serialize frame to bytes with CRC."""
        frame_data = self.header.to_bytes() + self.payload
        if crc32c:
            crc = struct.pack('>I', crc32c.crc32(frame_data))
        else:
            crc = struct.pack('>I', zlib.crc32(frame_data) & 0xffffffff)
        return frame_data + crc
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'TEMAFrame':
        """Deserialize frame from bytes with CRC verification."""
        if len(data) < 28:  # 24 header + 4 CRC
            raise ValueError(f"Frame too small: {len(data)} < 28")
        
        # Verify CRC
        frame_data = data[:-4]
        received_crc = struct.unpack('>I', data[-4:])[0]
        if crc32c:
            calculated_crc = crc32c.crc32(frame_data)
        else:
            calculated_crc = zlib.crc32(frame_data) & 0xffffffff
        
        if received_crc != calculated_crc:
            raise ValueError(f"CRC mismatch: {received_crc} != {calculated_crc}")
        
        header = TEMAHeader.from_bytes(data[:24])
        payload = data[24:24+header.payload_length]
        
        return cls(header=header, payload=payload)
    
    def get_size(self) -> int:
        """Total frame size in bytes."""
        return 24 + len(self.payload) + 4  # header + payload + CRC


class TEMAProtocol:
    """TEMA Protocol handler."""
    
    MAX_PAYLOAD_SIZE = 65536  # 64KB max payload
    ETHERTYPE = 0x9999  # Custom EtherType
    
    def __init__(self):
        self.sequence_counter = 0
        self.device_id = self._generate_device_id()
    
    @staticmethod
    def _generate_device_id() -> int:
        """Generate unique device ID from MAC address."""
        import socket
        import uuid
        mac = uuid.getnode()
        return mac & 0xFFFFFFFF  # Use lower 32 bits
    
    def create_frame(
        self,
        payload_type: PayloadType,
        payload: bytes,
        dest_device_id: int,
        flags: int = 0,
        encrypted: bool = False,
        compressed: bool = False
    ) -> TEMAFrame:
        """Create a TEMA frame."""
        if len(payload) > self.MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload too large: {len(payload)} > {self.MAX_PAYLOAD_SIZE}")
        
        if encrypted:
            flags |= Flags.ENCRYPTED
        if compressed:
            flags |= Flags.COMPRESSED
        
        header = TEMAHeader(
            version=1,
            flags=flags,
            payload_type=payload_type,
            sequence_number=self.sequence_counter,
            source_device_id=self.device_id,
            dest_device_id=dest_device_id,
            payload_length=len(payload),
            timestamp=int(__import__('time').time() * 1000)  # milliseconds
        )
        
        self.sequence_counter = (self.sequence_counter + 1) % 0xFFFF
        return TEMAFrame(header=header, payload=payload)
    
    def parse_frame(self, data: bytes) -> Optional[TEMAFrame]:
        """Parse received frame data."""
        try:
            return TEMAFrame.from_bytes(data)
        except (ValueError, struct.error) as e:
            print(f"Frame parse error: {e}")
            return None
