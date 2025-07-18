import time
import gpiod
from gpiod.line import Direction, Value
import threading

class Motor:
    def __init__(self):  # Fixed: double underscores
        # GPIO pin definitions
        self.DIRECTION_PIN_1 = 24  # Direction control pin
        self.PWM_PIN_1 = 12        # PWM control pin (speed)
        self.DIRECTION_PIN_2 = 26  
        self.PWM_PIN_2 = 13  

        # PWM configuration
        self.PWM_FREQUENCY = 1000  # 1kHz PWM frequency
        self.PWM_PERIOD = 1.0 / self.PWM_FREQUENCY  # Period in seconds
        self.PWM_RESOLUTION = 100  # Number of steps for PWM (0-100%)
        
        # GPIO request object will be set when start() is called
        self.request = None
        self.running = False

    def start(self):
        """Initialize GPIO and start motor control"""
        self.request = gpiod.request_lines(
            "/dev/gpiochip0",
            consumer="dc-motor-control",
            config={
                self.DIRECTION_PIN_1: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.INACTIVE
                ),
                self.PWM_PIN_1: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.INACTIVE
                ),
                self.DIRECTION_PIN_2: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.INACTIVE
                ),
                self.PWM_PIN_2: gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=Value.INACTIVE
                )
            }
        )
        self.running = True
        print("Motor controller initialized")

    def stop(self):
        """Stop motors and release GPIO resources"""
        if self.request:
            self.running = False
            # Stop both motors
            self.software_pwm(self.PWM_PIN_1, 0, 0.1)
            self.software_pwm(self.PWM_PIN_2, 0, 0.1)
            # Release GPIO
            self.request.release()
            self.request = None
            print("Motor controller stopped")

    def software_pwm(self, pin, duty_cycle, duration):
        """
        Software PWM implementation
        pin: GPIO pin number
        duty_cycle: 0-100 (percentage)
        duration: how long to run PWM (seconds)
        """
        if not self.request:
            print("Error: Motor not initialized. Call start() first.")
            return
            
        # If 0% duty cycle then no PWM algo needed just break out from this function for efficiency
        # Just turn off the motor
        if duty_cycle == 0:
            self.request.set_value(pin, Value.INACTIVE)
            time.sleep(duration)
            return
        
        # If 100% duty cycle then no PWM algo needed just break out from this function for efficiency
        # Just turn on the motor
        if duty_cycle >= 100:
            self.request.set_value(pin, Value.ACTIVE)
            time.sleep(duration)
            return
        
        # Start here if 0 < duty cycle < 100
        on_time = self.PWM_PERIOD * (duty_cycle / 100)
        off_time = self.PWM_PERIOD - on_time

        # time.time() returns current time
        end_time = time.time() + duration 
        
        while time.time() < end_time and self.running:
            self.request.set_value(pin, Value.ACTIVE)
            time.sleep(on_time)
            self.request.set_value(pin, Value.INACTIVE)
            time.sleep(off_time)

    def MotorRun_Lane(self, speed=20, turn=0, duration=0):
        if not self.request:
            print("Error: Motor not initialized. Call start() first.")
            return

        pwm1 = self.PWM_PIN_1
        pwm2 = self.PWM_PIN_2
        direc1 = self.DIRECTION_PIN_1
        direc2 = self.DIRECTION_PIN_2

        # Calculate differential speeds
        turn_adjustment = turn * 70
        pwm1_LeftSpeed = speed + turn_adjustment
        pwm2_RightSpeed = speed - turn_adjustment

        # Clamp speeds to valid range
        pwm1_LeftSpeed = max(0, min(50, pwm1_LeftSpeed))
        pwm2_RightSpeed = max(0, min(50, pwm2_RightSpeed))

        print(f"Left Speed: {pwm1_LeftSpeed}, Right Speed: {pwm2_RightSpeed}")


        # Set motor directions (both forward for now)
        self.request.set_value(direc1, Value.INACTIVE)
        self.request.set_value(direc2, Value.INACTIVE)

        # Run both motors simultaneously using threading
        thread1 = threading.Thread(target=self.software_pwm, args=(pwm1, pwm1_LeftSpeed, duration))
        thread2 = threading.Thread(target=self.software_pwm, args=(pwm2, pwm2_RightSpeed, duration))

        # Start both threads
        thread1.start()
        thread2.start()

        # Wait for both to complete
        thread1.join()
        thread2.join()

    def run_both_motors(self, speed1, speed2, direction1, direction2, duration):
        if not self.request:
            print("Error: Motor not initialized. Call start() first.")
            return

        # Set directions
        self.request.set_value(self.DIRECTION_PIN_1, direction1)
        self.request.set_value(self.DIRECTION_PIN_2, direction2)

        # Create threads for simultaneous PWM
        thread1 = threading.Thread(target=self.software_pwm, args=(self.PWM_PIN_1, speed1, duration))
        thread2 = threading.Thread(target=self.software_pwm, args=(self.PWM_PIN_2, speed2, duration))

        # Start both threads
        thread1.start()
        thread2.start()

        # Wait for both to complete
        thread1.join()
        thread2.join()

    def MotorStop_Lane(self):
        """Stop both motors for lane control"""
        if not self.request:
            print("Error: Motor not initialized. Call start() first.")
            return
            
        print("Stopping both motors")
        
        # Set directions
        self.request.set_value(self.DIRECTION_PIN_1, Value.ACTIVE)
        self.request.set_value(self.DIRECTION_PIN_2, Value.ACTIVE)
        
        # Stop both motors simultaneously
        thread1 = threading.Thread(target=self.software_pwm, args=(self.PWM_PIN_1, 0, 0.1))
        thread2 = threading.Thread(target=self.software_pwm, args=(self.PWM_PIN_2, 0, 0.1))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()

    def move_backward(self, speed=20, duration=1):
        """Move forward"""
        print(f"Moving backward at speed {speed} for {duration}s")
        self.run_both_motors(speed, speed, Value.ACTIVE, Value.ACTIVE, duration)

    def move_forward(self, speed=20, duration=1):
        """Move backward"""
        print(f"Moving forward at speed {speed} for {duration}s")
        self.run_both_motors(speed, speed, Value.INACTIVE, Value.INACTIVE, duration)

    def turn_left(self, speed=20, duration=1):
        """Turn left"""
        print(f"Turning left at speed {speed} for {duration}s")
        self.run_both_motors(0, speed, Value.INACTIVE, Value.INACTIVE, duration)

    def turn_right(self, speed=20, duration=1):
        """Turn right"""
        print(f"Turning right at speed {speed} for {duration}s")
        self.run_both_motors(speed, 0, Value.INACTIVE, Value.INACTIVE, duration)

    def stop_motors(self):
        """Stop both motors"""
        print("Stopping motors")
        self.run_both_motors(0, 0, Value.INACTIVE, Value.INACTIVE, 0.1)

    # Simple test function
    def test_motors(self):
        """Test all motor movements"""
        movements = [
            ("Forward", self.move_forward),
            ("Backward", self.move_backward),
            ("Left", self.turn_left),
            ("Right", self.turn_right),
            ("Stop", self.stop_motors)
        ]
        
        for name, func in movements:
            print(f"\nTesting {name}...")
            func(20, 2)  # 20% speed for 2 seconds
            time.sleep(0.5)  # Brief pause between movements

"""
# Usage example
if __name__ == "__main__":  # Fixed: double underscores
    motor_controller = Motor()
    
    try:
        motor_controller.start()
        
        
        # Test MotorRun_Lane function
        print("\nTesting MotorRun_Lane function...")
        print("Going straight...")
        motor_controller.MotorRun_Lane(speed=20, turn=0, duration=2)
        time.sleep(0.5)
        
        print("Turning left...")
        motor_controller.MotorRun_Lane(speed=20, turn=-0.3, duration=2)
        time.sleep(0.5)
        
        print("Turning right...")
        motor_controller.MotorRun_Lane(speed=20, turn=0.3, duration=2)
        time.sleep(0.5)
        
        print("Stopping with MotorStop_Lane...")
        motor_controller.MotorStop_Lane(duration=1)
        
        
        
        # Original test
        print("\nRunning other motor tests...")
        motor_controller.test_motors()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    finally:
        motor_controller.stop()
"""