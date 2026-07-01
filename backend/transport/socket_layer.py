"""Low-level socket communication over raw Ethernet."""

import socket
import struct
import logging
from typing import Optional, Tuple
from abc import ABC, abstractmethod
import asyncio
import threading

logger = logging.getLogger(__name__)


class RawSocketManager:
    """Manages raw socket communication over Ethernet."""
    
    AF_PACKET = 17  # Linux socket family for raw packet access
    
    def __init__(self, interface: str = 'eth0', ethertype: int = 0x9999):
        self.interface = interface
        self.ethertype = ethertype
        self.sock: Optional[socket.socket] = None
        self.receiving = False
        self.packet_handlers = []
        self._lock = threading.Lock()
    
    def get_interface_mac(self) -> str:
        """Get MAC address of the network interface."""
        import socket as sock
        import fcntl
        
        try:
            s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
            mac_bytes = fcntl.ioctl(
                s.fileno(),
                0x8927,  # SIOCGIFHWADDR
                struct.pack('256s', self.interface.encode()[:15])
            )[18:24]
            return ':'.join('%02x' % b for b in mac_bytes)
        except Exception as e:
            logger.error(f"Failed to get MAC for {self.interface}: {e}")
            return "00:00:00:00:00:00"
    
    def bind(self) -> bool:
        """Bind raw socket to network interface."""
        try:
            if self.sock:
                self.sock.close()
            
            # Create raw socket
            self.sock = socket.socket(
                self.AF_PACKET,  # AF_PACKET on Linux for raw frames
                socket.SOCK_RAW,
                socket.htons(self.ethertype)
            )
            
            # Bind to interface
            self.sock.bind((self.interface, 0))
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2097152)  # 2MB buffer
            
            logger.info(f"Raw socket bound to {self.interface} with EtherType 0x{self.ethertype:04x}")
            return True
        
        except PermissionError:
            logger.error("Raw socket requires root/administrator privileges")
            return False
        except Exception as e:
            logger.error(f"Failed to bind raw socket: {e}")
            return False
    
    def send(self, dest_mac: str, payload: bytes) -> bool:
        """Send raw Ethernet frame."""
        if not self.sock:
            logger.error("Socket not bound")
            return False
        
        try:
            # Parse destination MAC
            dest_bytes = bytes.fromhex(dest_mac.replace(':', ''))
            src_bytes = bytes.fromhex(self.get_interface_mac().replace(':', ''))
            
            # Build Ethernet frame
            eth_frame = (
                dest_bytes +                          # Destination MAC (6 bytes)
                src_bytes +                           # Source MAC (6 bytes)
                struct.pack('>H', self.ethertype) +   # EtherType (2 bytes)
                payload                               # Payload
            )
            
            self.sock.sendto(eth_frame, (self.interface, 0))
            logger.debug(f"Sent {len(eth_frame)} bytes to {dest_mac}")
            return True
        
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def receive_async(self, callback):
        """Start async receive loop."""
        if not self.sock:
            logger.error("Socket not bound")
            return
        
        self.receiving = True
        
        def receive_loop():
            while self.receiving:
                try:
                    data, _ = self.sock.recvfrom(65535)
                    
                    # Extract source MAC from frame
                    src_mac = ':'.join(f'{b:02x}' for b in data[6:12])
                    payload = data[14:]  # Skip Ethernet header
                    
                    callback(src_mac, payload)
                
                except Exception as e:
                    if self.receiving:
                        logger.error(f"Receive error: {e}")
        
        thread = threading.Thread(target=receive_loop, daemon=True)
        thread.start()
        return thread
    
    def close(self):
        """Close socket."""
        self.receiving = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        logger.info("Socket closed")
