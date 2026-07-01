"""Main TEMA application server."""

import asyncio
import logging
import argparse
import sys
import os
from typing import Dict, List

from transport.socket_layer import RawSocketManager
from transport.protocol import TEMAProtocol, PayloadType
from security.encryption import TEMAEncryption
from ai.music_analyzer import MusicAnalyzer
from config import TEMAConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TEMAServer:
    """Main TEMA application server."""
    
    def __init__(self, config: TEMAConfig):
        self.config = config
        self.socket_manager = RawSocketManager(
            interface=config.transport.interface,
            ethertype=TEMAProtocol.ETHERTYPE
        )
        self.protocol = TEMAProtocol()
        self.encryption = TEMAEncryption()
        self.analyzer = MusicAnalyzer(sr=config.ai.analyzer_sample_rate)
        self.peers: Dict[int, str] = {}  # device_id -> MAC address
        self.is_running = False
    
    async def start(self) -> bool:
        """Start the TEMA server."""
        logger.info(f"Starting TEMA Server on {self.config.transport.interface}")
        
        # Bind socket
        if not self.socket_manager.bind():
            logger.error("Failed to bind socket")
            return False
        
        self.is_running = True
        
        try:
            # Start receiving in background
            self.socket_manager.receive_async(self._on_packet_received)
            
            # Start discovery
            await self._start_discovery()
            
            logger.info("TEMA Server started successfully")
            return True
        
        except Exception as e:
            logger.error(f"Server startup failed: {e}")
            await self.stop()
            return False
    
    async def stop(self):
        """Stop the TEMA server."""
        logger.info("Stopping TEMA Server")
        self.is_running = False
        self.socket_manager.close()
    
    def _on_packet_received(self, src_mac: str, payload: bytes):
        """Handle received packet."""
        try:
            frame = self.protocol.parse_frame(payload)
            if not frame:
                return
            
            logger.debug(f"Received {frame.header.payload_type.name} from {src_mac}")
            
            # Store peer
            self.peers[frame.header.source_device_id] = src_mac
            
            # Handle different payload types
            if frame.header.payload_type == PayloadType.DISCOVERY:
                self._handle_discovery(frame, src_mac)
            elif frame.header.payload_type == PayloadType.MUSIC:
                self._handle_music(frame, src_mac)
            elif frame.header.payload_type == PayloadType.AI_REQUEST:
                self._handle_ai_request(frame, src_mac)
        
        except Exception as e:
            logger.error(f"Error processing packet from {src_mac}: {e}")
    
    async def _start_discovery(self):
        """Broadcast discovery message to find peers."""
        import struct
        
        while self.is_running:
            try:
                # Create discovery frame
                discovery_data = struct.pack(
                    '>I',
                    self.protocol.device_id
                )
                
                frame = self.protocol.create_frame(
                    payload_type=PayloadType.DISCOVERY,
                    payload=discovery_data,
                    dest_device_id=0xFFFFFFFF  # Broadcast
                )
                
                # Send to broadcast address
                self.socket_manager.send('ff:ff:ff:ff:ff:ff', frame.to_bytes())
                
                # Wait before next discovery
                await asyncio.sleep(30)
            
            except Exception as e:
                logger.error(f"Discovery error: {e}")
                await asyncio.sleep(5)
    
    def _handle_discovery(self, frame, src_mac: str):
        """Handle discovery request from peer."""
        logger.info(f"Discovered peer {frame.header.source_device_id} at {src_mac}")
        # Could send back a response here
    
    def _handle_music(self, frame, src_mac: str):
        """Handle music streaming data."""
        logger.debug(f"Music data received: {len(frame.payload)} bytes")
    
    def _handle_ai_request(self, frame, src_mac: str):
        """Handle AI analysis request."""
        try:
            import json
            request = json.loads(frame.payload.decode('utf-8'))
            logger.info(f"AI request from {src_mac}: {request.get('type')}")
        except Exception as e:
            logger.error(f"Failed to parse AI request: {e}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='TEMA Music & AI Server')
    parser.add_argument('--interface', default='eth0', help='Network interface to use')
    parser.add_argument('--config', default='~/.tema/config.json', help='Config file path')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Load config
    config_path = os.path.expanduser(args.config)
    config = TEMAConfig.from_file(config_path) if os.path.exists(config_path) else TEMAConfig()
    config.transport.interface = args.interface
    config.log_level = args.log_level
    
    # Start server
    server = TEMAServer(config)
    
    try:
        if await server.start():
            # Keep running
            while server.is_running:
                await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        await server.stop()


if __name__ == '__main__':
    asyncio.run(main())
