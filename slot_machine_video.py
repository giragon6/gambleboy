import asyncio
import os
import random
import ST7735
from PIL import Image
import glob

class SlotMachineVideo:
    def __init__(self):
        self.disp = ST7735.ST7735(port=0, cs=0, dc=24, rst=25,
                                  width=128, height=160, rotation=270,
                                  invert=False, bgr=False)
        self.disp.begin()
        
        self.win_frames = self.load_frames("winning_frames")
        self.lose_frames = self.load_frames("awdangit_frames")
        self.spin_frames = self.load_frames("letsgo_frames")
    
    def load_frames(self, frames_dir):
        """Load frames from directory"""
        if not os.path.exists(frames_dir):
            return []
        
        frame_files = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
        frames = []
        
        for frame_file in frame_files:
            try:
                img = Image.open(frame_file).convert('RGB')
                frames.append(img)
            except Exception as e:
                print(f"Error loading {frame_file}: {e}")
        
        return frames
    
    async def play_animation(self, frames, fps=10):
        """Play animation frames"""
        if not frames:
            return
        
        frame_delay = 1.0 / fps
        
        for frame in frames:
            self.disp.display(frame)
            await asyncio.sleep(frame_delay)
    
    async def show_win_animation(self):
        """Play win animation"""
        await self.play_animation(self.win_frames)
    
    async def show_lose_animation(self):
        """Play lose animation"""
        await self.play_animation(self.lose_frames)
    
    async def show_spin_animation(self):
        """Play spin animation"""
        await self.play_animation(self.spin_frames)