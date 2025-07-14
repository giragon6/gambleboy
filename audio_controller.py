#!/usr/bin/env python3
"""
Audio controller for Raspberry Pi with MAX98357 I2S amplifier
"""

import subprocess
import os
import pygame
import asyncio
from pathlib import Path

class AudioController:
    def __init__(self, sample_rate=44100, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the audio system"""
        try:
            # Check if we're in SSH with X11 forwarding
            if os.environ.get('DISPLAY') and os.environ.get('SSH_CLIENT'):
                print("SSH X11 forwarding detected - using network audio")
                # Set PulseAudio to use network if available
                os.environ['PULSE_RUNTIME_PATH'] = f"/run/user/{os.getuid()}/pulse"
            
            # Initialize pygame mixer for audio playback
            pygame.mixer.pre_init(
                frequency=self.sample_rate,
                size=-16,  # 16-bit signed
                channels=2,  # Stereo
                buffer=self.buffer_size
            )
            pygame.mixer.init()
            self.is_initialized = True
            print("Audio system initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing audio: {e}")
            print("Trying fallback initialization...")
            try:
                # Fallback: try with different settings
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
                pygame.mixer.init()
                self.is_initialized = True
                print("Audio system initialized with fallback settings")
                return True
            except Exception as e2:
                print(f"Fallback audio initialization failed: {e2}")
                return False
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        if self.is_initialized:
            pygame.mixer.music.set_volume(volume)
    
    def play_sound(self, file_path):
        """Play a sound file"""
        if not self.is_initialized:
            print("Audio not initialized")
            return False
        
        try:
            if not os.path.exists(file_path):
                print(f"Audio file not found: {file_path}")
                return False
            
            sound = pygame.mixer.Sound(file_path)
            sound.play()
            return True
        except Exception as e:
            print(f"Error playing sound {file_path}: {e}")
            return False
    
    async def play_sound_async(self, file_path):
        """Play sound asynchronously"""
        if not self.is_initialized:
            print("Audio not initialized")
            return False
        
        try:
            sound = pygame.mixer.Sound(file_path)
            channel = sound.play()
            
            # Wait for sound to finish
            while channel.get_busy():
                await asyncio.sleep(0.1)
            
            return True
        except Exception as e:
            print(f"Error playing sound {file_path}: {e}")
            return False
    
    def play_music(self, file_path, loops=-1):
        """Play background music (loops=-1 for infinite loop)"""
        if not self.is_initialized:
            print("Audio not initialized")
            return False
        
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(loops)
            return True
        except Exception as e:
            print(f"Error playing music {file_path}: {e}")
            return False
    
    def stop_music(self):
        """Stop background music"""
        if self.is_initialized:
            pygame.mixer.music.stop()
    
    def test_audio(self):
        """Test audio output"""
        print("Testing audio output...")
        
        # Test with speaker-test command
        try:
            result = subprocess.run([
                'speaker-test', '-t', 'sine', '-f', '1000', '-c', '2', '-s', '1'
            ], capture_output=True, timeout=5)
            
            if result.returncode == 0:
                print("Hardware audio test successful")
            else:
                print(f"Hardware audio test failed: {result.stderr.decode()}")
        except subprocess.TimeoutExpired:
            print("Audio test completed")
        except Exception as e:
            print(f"Error running audio test: {e}")
    
    def get_audio_devices(self):
        """List available audio devices"""
        try:
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            print("Available audio devices:")
            print(result.stdout)
        except Exception as e:
            print(f"Error listing audio devices: {e}")
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.is_initialized:
            pygame.mixer.quit()
            self.is_initialized = False

# Example usage class for slot machine
class SlotMachineAudio:
    def __init__(self, sounds_dir="sounds"):
        self.audio = AudioController()
        self.sounds_dir = Path(sounds_dir)
        
        # Define sound files
        self.sounds = {
            'spin': self.sounds_dir / 'spin.wav',
            'win': self.sounds_dir / 'win.wav',
            'lose': self.sounds_dir / 'lose.wav',
            'button': self.sounds_dir / 'button.wav',
            'jackpot': self.sounds_dir / 'jackpot.wav',
            'background': self.sounds_dir / 'background.mp3'
        }
        
        # Create sounds directory if it doesn't exist
        self.sounds_dir.mkdir(exist_ok=True)
        
    def initialize(self):
        """Initialize audio system"""
        success = self.audio.initialize()
        if success:
            self.audio.set_volume(0.8)  # Set to 80% volume
        return success
    
    async def play_spin_sound(self):
        """Play spinning sound"""
        await self.audio.play_sound_async(str(self.sounds['spin']))
    
    async def play_win_sound(self):
        """Play win sound"""
        await self.audio.play_sound_async(str(self.sounds['win']))
    
    async def play_jackpot_sound(self):
        """Play jackpot sound"""
        await self.audio.play_sound_async(str(self.sounds['jackpot']))
    
    async def play_lose_sound(self):
        """Play lose sound"""
        await self.audio.play_sound_async(str(self.sounds['lose']))

    def play_button_sound(self):
        """Play button press sound"""
        self.audio.play_sound(str(self.sounds['button']))
    
    def play_background_music(self):
        """Start background music"""
        if self.sounds['background'].exists():
            self.audio.play_music(str(self.sounds['background']))
    
    def stop_background_music(self):
        """Stop background music"""
        self.audio.stop_music()
    
    def cleanup(self):
        """Clean up audio resources"""
        self.audio.cleanup()

# Test script
async def test_audio_system():
    """Test the audio system"""
    audio = SlotMachineAudio()
    
    if not audio.initialize():
        print("Failed to initialize audio")
        return
    
    print("Testing audio system...")
    
    # Test hardware
    audio.audio.test_audio()
    
    # Test if sound files exist
    for name, path in audio.sounds.items():
        if path.exists():
            print(f"✓ {name}: {path}")
        else:
            print(f"✗ {name}: {path} (missing)")
    
    audio.cleanup()

if __name__ == "__main__":
    asyncio.run(test_audio_system())
