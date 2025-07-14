import asyncio
import random
import RPi.GPIO as GPIO

from serial_communication import SerialCommunication
from slot_machine_video import SlotMachineVideo

# Constants

# Buttons
BUTTON_PIN = 20  # Pin 20 for the spin button

# Serial Communication
SERIAL_PORT     = "/dev/ttyACM0"
SERIAL_BAUD     = 115200
SERIAL_TIMEOUT  = 1        

# Values
GAMBLE_AMT = 200
GAMBLE_CHANCES  = [10,  50, 100,  200,  500,  1000, 10000,  100000]
GAMBLE_WEIGHTS  = [0.5, 1,  0.5,  0.4,  0.35, 0.1,  0.01,   0.001 ]

# Classes

class Button:
    def __init__(self, pin: int):
        self.pin = pin
        self.last_state = False
        
    def is_pressed(self) -> bool:
        return GPIO.input(self.pin) == GPIO.LOW
        
    def was_just_pressed(self) -> bool:
        """Returns True only on the moment the button is pressed (not held)"""
        current_state = self.is_pressed()
        if current_state and not self.last_state:
            self.last_state = current_state
            return True
        self.last_state = current_state
        return False

# Init

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN)

video_player = SlotMachineVideo()

serial_comm = SerialCommunication(SERIAL_PORT, SERIAL_BAUD, SERIAL_TIMEOUT)

spin_button = Button(BUTTON_PIN)


async def handle_button_presses():
    """Handle button press detection and trigger spins"""
    while True:
        if spin_button.was_just_pressed():
            print("Spin button pressed! Starting spin...")
            
            # Send GAMBLE command before spinning
            serial_comm.send_data(f"GAMBLE {GAMBLE_AMT}")
            print(f"Sent: GAMBLE {GAMBLE_AMT}")
            
            # Perform the spin
            payout = await spin()
            
            # Send result to RP2350
            if payout > 0:
                serial_comm.send_data(f"WIN {payout}")
                print(f"Sent: WIN {payout} - Won payout: {payout}")
            else:
                serial_comm.send_data("LOSE")
                print("Sent: LOSE - No payout")
                
            # Wait a moment before allowing next spin
            await asyncio.sleep(1)
        
        await asyncio.sleep(0.05)  # Check button every 50ms
    
def get_payout():
  payout = random.choices(GAMBLE_CHANCES, weights=GAMBLE_WEIGHTS)[0]
  return payout 
  
async def spin():    
    await video_player.show_spin_animation()
    
    rand = random.random()
    if rand < 0.2:
      await video_player.show_win_animation()
      return get_payout()
    else:
      await video_player.show_lose_animation()
      return 0
  
async def main():
    print("Initializing serial communication...")
    
    while not serial_comm.connect():
        await asyncio.sleep(0.5)
        
    print("Connected to RP2350")
    print("Waiting for button press on pin 20...")
    
    try:
        await handle_button_presses()
        
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        serial_comm.disconnect()
        GPIO.cleanup()

if __name__ == "__main__":
    asyncio.run(main())